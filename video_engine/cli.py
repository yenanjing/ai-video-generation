"""
Command-line interface for video generation.
"""
import sys
import argparse
from pathlib import Path
from typing import Optional

from video_engine.core.orchestrator import VideoOrchestrator
from video_engine.models.registry import registry
from video_engine.config import config
from video_engine.llm.storyboard_generator import StoryboardGenerator


def print_progress(step: str, progress: float, shot_id: Optional[str] = None):
    """Print progress update."""
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "━" * filled + "━" * (bar_length - filled)

    shot_info = f" [{shot_id}]" if shot_id else ""
    print(f"\r{step}{shot_info}: [{bar}] {progress:.1f}%", end="", flush=True)

    if progress >= 100:
        print()  # New line when complete


def cmd_generate(args):
    """Generate video from prompt."""
    print("=" * 60)
    print("AI Video Generation")
    print("=" * 60)
    print(f"Prompt: {args.prompt}")
    print(f"Model: {args.model}")
    print(f"Max shots: {args.max_shots}")
    print()

    # Validate API keys
    api_keys = config.validate_api_keys()
    if not api_keys.get("anthropic"):
        print("ERROR: ANTHROPIC_API_KEY not configured")
        print("Please set ANTHROPIC_API_KEY in .env file")
        return 1

    if args.model.startswith("replicate:") and not api_keys.get("replicate"):
        print("ERROR: REPLICATE_API_TOKEN not configured")
        print("Please set REPLICATE_API_TOKEN in .env file")
        return 1

    # Create orchestrator
    orchestrator = VideoOrchestrator()

    try:
        # Create job
        print("Creating video generation job...")
        job = orchestrator.create_job(
            prompt=args.prompt,
            model_id=args.model,
            reference_image_path=args.reference_image,
            max_shots=args.max_shots,
        )

        print(f"Job created: {job.id}")
        print()

        # Execute job
        job = orchestrator.execute_job(
            job_id=job.id,
            progress_callback=print_progress,
        )

        print()
        print("=" * 60)
        print("✓ Video generation complete!")
        print("=" * 60)
        print(f"Job ID: {job.id}")
        print(f"Output: {job.output_video_path}")
        print(f"Shots: {job.storyboard.shot_count}")
        print(f"Duration: {job.storyboard.total_duration_seconds:.1f}s")
        print()

        # Copy to user-specified output if provided
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            import shutil
            shutil.copy2(job.output_video_path, output_path)
            print(f"Saved to: {output_path}")

        return 0

    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Error: {e}")
        print("=" * 60)
        return 1


def cmd_storyboard(args):
    """Generate storyboard only."""
    print("=" * 60)
    print("Storyboard Generation")
    print("=" * 60)
    print(f"Prompt: {args.prompt}")
    print()

    # Validate API keys
    api_keys = config.validate_api_keys()
    if not api_keys.get("anthropic"):
        print("ERROR: ANTHROPIC_API_KEY not configured")
        return 1

    try:
        generator = StoryboardGenerator(llm="claude")
        storyboard = generator.generate(
            user_prompt=args.prompt,
            max_shots=args.max_shots,
        )

        print("✓ Storyboard generated")
        print()
        print(f"Title: {storyboard.title}")
        print(f"Shots: {storyboard.shot_count}")
        print(f"Duration: {storyboard.total_duration_seconds:.1f}s")
        print()

        print("Shots:")
        print("-" * 60)
        for shot in storyboard.shots:
            print(f"\n{shot.sequence_number}. {shot.description}")
            print(f"   Duration: {shot.duration_seconds}s")
            print(f"   Camera: {shot.camera_movement}, {shot.camera_angle}")
            print(f"   Prompt: {shot.text_prompt}")

        # Save to file if specified
        if args.output:
            import json
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(storyboard.model_dump(), f, indent=2, default=str)

            print()
            print(f"Saved to: {output_path}")

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def cmd_list_models(args):
    """List available models."""
    print("=" * 60)
    print("Available Video Generation Models")
    print("=" * 60)
    print()

    models = registry.list_models()

    if not models:
        print("No models available.")
        return 1

    for model in models:
        status = "✓" if model.is_available else "✗"
        print(f"{status} {model.id}")
        print(f"   Name: {model.name}")
        print(f"   Provider: {model.provider}")
        print(f"   T2V: {model.capabilities.supports_text_to_video}")
        print(f"   I2V: {model.capabilities.supports_image_to_video}")
        print(f"   Max frames: {model.capabilities.max_frames}")
        print(f"   GPU required: {model.capabilities.requires_gpu}")
        print()

    return 0


def cmd_list_jobs(args):
    """List all jobs."""
    orchestrator = VideoOrchestrator()
    jobs = orchestrator.list_jobs()

    if not jobs:
        print("No jobs found.")
        return 0

    print("=" * 60)
    print("Video Generation Jobs")
    print("=" * 60)
    print()

    for job in jobs:
        print(f"{job.id}")
        print(f"   Status: {job.status.value}")
        print(f"   Prompt: {job.user_prompt[:60]}...")
        print(f"   Model: {job.model_id}")
        print(f"   Progress: {job.progress_percentage:.1f}%")
        if job.output_video_path:
            print(f"   Output: {job.output_video_path}")
        print()

    return 0


def cmd_get_job(args):
    """Get job details."""
    orchestrator = VideoOrchestrator()
    job = orchestrator.get_job(args.job_id)

    if not job:
        print(f"Job not found: {args.job_id}")
        return 1

    print("=" * 60)
    print(f"Job: {job.id}")
    print("=" * 60)
    print(f"Status: {job.status.value}")
    print(f"Prompt: {job.user_prompt}")
    print(f"Model: {job.model_id}")
    print(f"Progress: {job.progress_percentage:.1f}%")
    print(f"Current step: {job.current_step}")
    print()

    if job.storyboard:
        print(f"Storyboard: {job.storyboard.title}")
        print(f"Shots: {job.storyboard.shot_count}")
        print(f"Duration: {job.storyboard.total_duration_seconds:.1f}s")
        print()

    if job.output_video_path:
        print(f"Output: {job.output_video_path}")

    if job.error_message:
        print(f"Error: {job.error_message}")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Video Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate video from text prompt",
    )
    generate_parser.add_argument("prompt", help="Text description of desired video")
    generate_parser.add_argument(
        "--model",
        default=config.DEFAULT_VIDEO_MODEL,
        help="Model to use (default: %(default)s)",
    )
    generate_parser.add_argument(
        "--max-shots",
        type=int,
        default=5,
        help="Maximum number of shots (default: 5)",
    )
    generate_parser.add_argument(
        "--reference-image",
        help="Path to reference image for I2V",
    )
    generate_parser.add_argument(
        "--output",
        "-o",
        help="Output video path",
    )

    # Storyboard command
    storyboard_parser = subparsers.add_parser(
        "storyboard",
        help="Generate storyboard only",
    )
    storyboard_parser.add_argument("prompt", help="Text description")
    storyboard_parser.add_argument(
        "--max-shots",
        type=int,
        default=5,
        help="Maximum shots (default: 5)",
    )
    storyboard_parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file",
    )

    # List models command
    subparsers.add_parser(
        "list-models",
        help="List available models",
    )

    # List jobs command
    subparsers.add_parser(
        "list-jobs",
        help="List all jobs",
    )

    # Get job command
    get_job_parser = subparsers.add_parser(
        "get-job",
        help="Get job details",
    )
    get_job_parser.add_argument("job_id", help="Job ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handler
    handlers = {
        "generate": cmd_generate,
        "storyboard": cmd_storyboard,
        "list-models": cmd_list_models,
        "list-jobs": cmd_list_jobs,
        "get-job": cmd_get_job,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
