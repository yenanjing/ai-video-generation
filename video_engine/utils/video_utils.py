"""
Video processing utilities using FFmpeg.
"""
import subprocess
from pathlib import Path
from typing import List, Optional
import json

from video_engine.config import config


def concatenate_videos(
    input_paths: List[Path],
    output_path: Path,
    transition_duration: float = 0.0,
) -> bool:
    """
    Concatenate multiple videos into one.

    Args:
        input_paths: List of input video paths
        output_path: Output video path
        transition_duration: Duration of crossfade transition (0 = cut)

    Returns:
        True if successful
    """
    if not input_paths:
        raise ValueError("No input videos provided")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if transition_duration == 0.0:
            # Simple concatenation without transitions
            return _concat_simple(input_paths, output_path)
        else:
            # Concatenation with crossfade transitions
            return _concat_with_crossfade(input_paths, output_path, transition_duration)
    except Exception as e:
        print(f"Error concatenating videos: {e}")
        return False


def _concat_simple(input_paths: List[Path], output_path: Path) -> bool:
    """Simple concatenation using concat demuxer."""
    # Create file list
    list_file = config.TEMP_DIR / f"concat_list_{output_path.stem}.txt"

    with open(list_file, "w") as f:
        for path in input_paths:
            # Escape single quotes in path
            escaped_path = str(path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    try:
        # Run ffmpeg
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            "-y",  # Overwrite output
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        return True

    finally:
        # Clean up list file
        list_file.unlink(missing_ok=True)


def _concat_with_crossfade(
    input_paths: List[Path],
    output_path: Path,
    transition_duration: float,
) -> bool:
    """Concatenation with crossfade transitions."""
    if len(input_paths) == 1:
        # No transitions needed
        return _concat_simple(input_paths, output_path)

    # Build complex filter for crossfade
    filter_parts = []
    input_labels = [f"[{i}:v]" for i in range(len(input_paths))]

    current_label = input_labels[0]

    for i in range(len(input_paths) - 1):
        next_label = input_labels[i + 1]
        output_label = f"[v{i}]" if i < len(input_paths) - 2 else "[outv]"

        # Get duration of current video
        duration = get_video_duration(input_paths[i])
        offset = max(0, duration - transition_duration)

        filter_parts.append(
            f"{current_label}{next_label}xfade=transition=fade:duration={transition_duration}:offset={offset}{output_label}"
        )

        current_label = output_label

    filter_complex = ";".join(filter_parts)

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        *[item for path in input_paths for item in ["-i", str(path)]],
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", config.VIDEO_CODEC,
        "-pix_fmt", config.VIDEO_PIXEL_FORMAT,
        "-crf", str(config.VIDEO_CRF),
        "-y",
        str(output_path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    return True


def get_video_duration(video_path: Path) -> float:
    """
    Get video duration in seconds.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(video_path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def get_video_info(video_path: Path) -> dict:
    """
    Get video information.

    Args:
        video_path: Path to video file

    Returns:
        Dictionary with video info
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames:format=duration",
        "-of", "json",
        str(video_path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    stream = data["streams"][0]
    format_info = data["format"]

    # Parse frame rate
    frame_rate_str = stream.get("r_frame_rate", "0/1")
    num, den = map(int, frame_rate_str.split("/"))
    fps = num / den if den != 0 else 0

    return {
        "width": stream.get("width", 0),
        "height": stream.get("height", 0),
        "fps": fps,
        "duration": float(format_info.get("duration", 0)),
        "num_frames": int(stream.get("nb_frames", 0)),
    }


def extract_frame(video_path: Path, output_path: Path, frame_number: int = 0) -> bool:
    """
    Extract a single frame from video.

    Args:
        video_path: Input video path
        output_path: Output image path
        frame_number: Frame number to extract (0-indexed)

    Returns:
        True if successful
    """
    try:
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", f"select=eq(n\\,{frame_number})",
            "-vframes", "1",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error extracting frame: {e}")
        return False


def convert_to_standard_format(input_path: Path, output_path: Path) -> bool:
    """
    Convert video to standard format (H.264, yuv420p).

    Args:
        input_path: Input video path
        output_path: Output video path

    Returns:
        True if successful
    """
    try:
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-c:v", config.VIDEO_CODEC,
            "-pix_fmt", config.VIDEO_PIXEL_FORMAT,
            "-crf", str(config.VIDEO_CRF),
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {e}")
        return False
