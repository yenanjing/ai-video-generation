#!/usr/bin/env python
"""
Test script to verify video engine components.
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from video_engine.config import config
        print("✓ Config imported")

        from video_engine.models.schemas import Shot, Storyboard, VideoJob
        print("✓ Schemas imported")

        from video_engine.models.registry import registry
        print("✓ Registry imported")

        from video_engine.llm.storyboard_generator import StoryboardGenerator
        print("✓ Storyboard generator imported")

        from video_engine.core.orchestrator import VideoOrchestrator
        print("✓ Orchestrator imported")

        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration."""
    print("\nTesting configuration...")

    from video_engine.config import config

    # Ensure directories
    config.ensure_directories()

    # Check directories exist
    for dir_name, dir_path in [
        ("WORKSPACE_DIR", config.WORKSPACE_DIR),
        ("VIDEO_OUTPUT_DIR", config.VIDEO_OUTPUT_DIR),
        ("VIDEO_UPLOAD_DIR", config.VIDEO_UPLOAD_DIR),
        ("JOBS_DIR", config.JOBS_DIR),
        ("TEMP_DIR", config.TEMP_DIR),
    ]:
        if dir_path.exists():
            print(f"✓ {dir_name}: {dir_path}")
        else:
            print(f"✗ {dir_name} not found: {dir_path}")
            return False

    # Check API keys
    api_keys = config.validate_api_keys()
    print(f"\nAPI Keys configured:")
    for key, value in api_keys.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}")

    return True


def test_registry():
    """Test model registry."""
    print("\nTesting model registry...")

    from video_engine.models.registry import registry

    models = registry.list_models()
    print(f"Registered models: {len(models)}")

    for model in models:
        status = "✓" if model.is_available else "✗"
        print(f"  {status} {model.id} - {model.name}")

    return True


def test_schemas():
    """Test data models."""
    print("\nTesting data models...")

    from video_engine.models.schemas import Shot, Storyboard, VideoJob
    from datetime import datetime

    try:
        # Create a shot
        shot = Shot(
            id="test_shot_001",
            sequence_number=1,
            duration_seconds=3.0,
            description="Test shot",
            text_prompt="A beautiful landscape",
        )
        print(f"✓ Created shot: {shot.id}")

        # Create a storyboard
        storyboard = Storyboard(
            id="test_storyboard_001",
            title="Test Storyboard",
            user_prompt="Test prompt",
            shots=[shot],
            total_duration_seconds=3.0,
            shot_count=1,
            generated_at=datetime.now(),
            generated_by="test",
        )
        print(f"✓ Created storyboard: {storyboard.id}")

        # Create a job
        job = VideoJob(
            id="test_job_001",
            user_prompt="Test prompt",
        )
        print(f"✓ Created job: {job.id}")

        return True

    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        return False


def test_ffmpeg():
    """Test FFmpeg availability."""
    print("\nTesting FFmpeg...")

    import subprocess

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True,
        )

        version_line = result.stdout.split("\n")[0]
        print(f"✓ FFmpeg available: {version_line}")
        return True

    except FileNotFoundError:
        print("✗ FFmpeg not found in PATH")
        print("  Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)")
        return False
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Video Engine Component Tests")
    print("=" * 60)
    print()

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Model Registry", test_registry),
        ("Data Schemas", test_schemas),
        ("FFmpeg", test_ffmpeg),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {e}")
            results.append((name, False))
        print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print()
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
