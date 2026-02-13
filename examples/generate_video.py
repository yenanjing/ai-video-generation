#!/usr/bin/env python
"""
Example: Generate a video programmatically using the VideoOrchestrator.

This example shows how to use the video generation engine as a Python library
rather than through the CLI.
"""
import sys
from video_engine import VideoOrchestrator, config


def progress_handler(step: str, progress: float, shot_id: str = None):
    """
    Custom progress handler that prints updates.

    Args:
        step: Current step description
        progress: Progress percentage (0-100)
        shot_id: Optional shot ID being processed
    """
    # Simple progress bar
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    shot_info = f" [{shot_id}]" if shot_id else ""
    print(f"\r{step}{shot_info}: [{bar}] {progress:.1f}%", end="", flush=True)

    if progress >= 100:
        print()  # New line when complete


def main():
    """Main example function."""
    # Check API keys are configured
    api_keys = config.validate_api_keys()

    if not api_keys.get("anthropic"):
        print("Error: ANTHROPIC_API_KEY not configured")
        print("Please set it in your .env file")
        return 1

    if not api_keys.get("replicate"):
        print("Error: REPLICATE_API_TOKEN not configured")
        print("Please set it in your .env file")
        return 1

    print("=" * 60)
    print("Video Generation Example")
    print("=" * 60)
    print()

    # Create orchestrator
    orchestrator = VideoOrchestrator()

    # Define prompt
    prompt = "A serene Japanese garden with koi fish swimming in a pond, cherry blossoms falling gently"

    print(f"Prompt: {prompt}")
    print(f"Model: {config.DEFAULT_VIDEO_MODEL}")
    print(f"Max shots: 3")
    print()

    try:
        # Step 1: Create job
        print("Creating video generation job...")
        job = orchestrator.create_job(
            prompt=prompt,
            max_shots=3,  # Limit to 3 shots for faster generation
        )

        print(f"Job created: {job.id}")
        print()

        # Step 2: Execute job with progress tracking
        print("Starting video generation...")
        print()

        job = orchestrator.execute_job(
            job_id=job.id,
            progress_callback=progress_handler,
        )

        # Step 3: Display results
        print()
        print("=" * 60)
        print("✓ Video Generation Complete!")
        print("=" * 60)
        print()
        print(f"Job ID: {job.id}")
        print(f"Status: {job.status.value}")
        print()

        if job.storyboard:
            print("Storyboard:")
            print(f"  Title: {job.storyboard.title}")
            print(f"  Shots: {job.storyboard.shot_count}")
            print(f"  Duration: {job.storyboard.total_duration_seconds:.1f}s")
            print()

            print("Shots:")
            for i, shot in enumerate(job.storyboard.shots, 1):
                print(f"  {i}. {shot.description}")
                print(f"     Duration: {shot.duration_seconds}s")
                print(f"     Output: {shot.output_video_path}")
            print()

        print(f"Final Video: {job.output_video_path}")
        print()

        # Optional: Access job metadata
        print("Job Metadata:")
        print(f"  Created: {job.created_at}")
        print(f"  Updated: {job.updated_at}")
        print(f"  Model: {job.model_id}")
        print(f"  Mode: {job.generation_mode.value}")
        print()

        return 0

    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Error: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
