#!/usr/bin/env python
"""
System readiness checker for AI Video Generation.

This script checks if everything is properly configured and ready to generate videos.
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    import sys
    version = sys.version_info

    print("Python Version:")
    if version >= (3, 10):
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_dependencies():
    """Check required Python packages."""
    print("\nPython Dependencies:")

    required = [
        ("anthropic", "Anthropic API client"),
        ("replicate", "Replicate API client"),
        ("PIL", "Pillow image library"),
        ("pydantic", "Data validation"),
        ("dotenv", "Environment variables"),
    ]

    all_ok = True
    for module, description in required:
        try:
            __import__(module)
            print(f"  ✓ {module} - {description}")
        except ImportError:
            print(f"  ✗ {module} - {description} (not installed)")
            all_ok = False

    return all_ok


def check_ffmpeg():
    """Check FFmpeg installation."""
    import subprocess

    print("\nFFmpeg:")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version_line = result.stdout.split("\n")[0]
        print(f"  ✓ {version_line}")
        return True
    except FileNotFoundError:
        print("  ✗ FFmpeg not found")
        print("     Install: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)")
        return False
    except Exception as e:
        print(f"  ✗ Error checking FFmpeg: {e}")
        return False


def check_env_file():
    """Check .env file configuration."""
    print("\nEnvironment Configuration:")

    env_path = Path(".env")

    if not env_path.exists():
        print("  ✗ .env file not found")
        print("     Create from template: cp .env.example .env")
        return False

    print("  ✓ .env file exists")

    # Load and check keys
    from dotenv import load_dotenv
    load_dotenv()

    keys = {
        "ANTHROPIC_API_KEY": "Claude API (required)",
        "REPLICATE_API_TOKEN": "Replicate API (required)",
        "OPENAI_API_KEY": "OpenAI API (optional)",
    }

    required_ok = True
    optional_ok = True

    print("\n  API Keys:")
    for key, description in keys.items():
        value = os.getenv(key, "")
        is_required = "required" in description.lower()

        if value and value != "your_" + key.lower() + "_here":
            print(f"    ✓ {key} - {description}")
        else:
            if is_required:
                print(f"    ✗ {key} - {description} (not set)")
                required_ok = False
            else:
                print(f"    ○ {key} - {description} (not set)")

    return required_ok


def check_directories():
    """Check workspace directories."""
    print("\nWorkspace Directories:")

    from video_engine.config import config

    config.ensure_directories()

    dirs = [
        ("WORKSPACE_DIR", config.WORKSPACE_DIR),
        ("VIDEO_OUTPUT_DIR", config.VIDEO_OUTPUT_DIR),
        ("VIDEO_UPLOAD_DIR", config.VIDEO_UPLOAD_DIR),
        ("JOBS_DIR", config.JOBS_DIR),
        ("TEMP_DIR", config.TEMP_DIR),
    ]

    all_ok = True
    for name, path in dirs:
        if path.exists() and path.is_dir():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ✗ {name}: {path} (not found)")
            all_ok = False

    return all_ok


def check_models():
    """Check available models."""
    print("\nAvailable Models:")

    from video_engine.models.registry import registry

    models = registry.list_models()

    if not models:
        print("  ✗ No models registered")
        print("     This may be due to missing API keys")
        return False

    available = [m for m in models if m.is_available]
    unavailable = [m for m in models if not m.is_available]

    if available:
        print(f"  Available ({len(available)}):")
        for model in available:
            print(f"    ✓ {model.id} - {model.name}")

    if unavailable:
        print(f"  Unavailable ({len(unavailable)}):")
        for model in unavailable:
            print(f"    ✗ {model.id} - {model.name}")

    return len(available) > 0


def check_llm():
    """Check LLM availability."""
    print("\nLLM Storyboard Generation:")

    from video_engine.llm.storyboard_generator import StoryboardGenerator

    available = StoryboardGenerator.get_available_llms()

    if not available:
        print("  ✗ No LLMs available")
        print("     Configure ANTHROPIC_API_KEY or OPENAI_API_KEY")
        return False

    for llm in available:
        print(f"  ✓ {llm} available")

    return True


def main():
    """Run all checks."""
    print("=" * 60)
    print("AI Video Generation - System Readiness Check")
    print("=" * 60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("FFmpeg", check_ffmpeg),
        ("Environment", check_env_file),
        ("Directories", check_directories),
        ("Models", check_models),
        ("LLM", check_llm),
    ]

    results = []

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed: {e}")
            results.append((name, False))
        print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print()
    print(f"Passed: {passed}/{total}")
    print()

    if passed == total:
        print("=" * 60)
        print("✓ System is ready!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Try generating a storyboard:")
        print('     python -m video_engine.cli storyboard "Your prompt"')
        print()
        print("  2. Generate a video:")
        print('     python -m video_engine.cli generate "Your prompt"')
        print()
        return 0
    else:
        print("=" * 60)
        print(f"✗ {total - passed} check(s) failed")
        print("=" * 60)
        print()
        print("Please fix the issues above before proceeding.")
        print("See QUICKSTART.md for detailed setup instructions.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
