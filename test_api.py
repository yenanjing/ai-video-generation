#!/usr/bin/env python
"""
Test script for FastAPI endpoints.
"""
import sys
import time
import requests
from pathlib import Path


API_BASE = "http://localhost:8000/api/v1"


def test_health():
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{API_BASE}/health")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ API Status: {data['status']}")
        print(f"  Version: {data['version']}")
        print(f"  API Keys: {data['api_keys_configured']}")
        print(f"  Models Available: {data['models_available']}")
        return True
    else:
        print(f"✗ Health check failed: {response.status_code}")
        return False


def test_models():
    """Test models endpoint."""
    print("\nTesting models list...")
    response = requests.get(f"{API_BASE}/models")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['total']} models")

        for model in data['models']:
            status = "✓" if model['is_available'] else "✗"
            print(f"  {status} {model['id']} - {model['name']}")

        return True
    else:
        print(f"✗ Models list failed: {response.status_code}")
        return False


def test_create_job():
    """Test job creation endpoint."""
    print("\nTesting job creation...")

    payload = {
        "user_prompt": "A peaceful forest at sunrise",
        "model_id": "replicate:svd-xt",
        "max_shots": 2,  # Keep it small for testing
    }

    response = requests.post(f"{API_BASE}/jobs", json=payload)

    if response.status_code == 201:
        data = response.json()
        job_id = data['id']
        print(f"✓ Job created: {job_id}")
        print(f"  Status: {data['status']}")
        print(f"  Prompt: {data['user_prompt']}")
        print(f"  Model: {data['model_id']}")
        return job_id
    else:
        print(f"✗ Job creation failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def test_get_job(job_id: str):
    """Test get job endpoint."""
    print(f"\nTesting get job {job_id}...")

    response = requests.get(f"{API_BASE}/jobs/{job_id}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Job retrieved:")
        print(f"  Status: {data['status']}")
        print(f"  Progress: {data['progress_percentage']:.1f}%")
        print(f"  Current Step: {data['current_step']}")
        return data
    else:
        print(f"✗ Get job failed: {response.status_code}")
        return None


def test_list_jobs():
    """Test list jobs endpoint."""
    print("\nTesting list jobs...")

    response = requests.get(f"{API_BASE}/jobs?page=1&page_size=10")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['total']} jobs")

        for job in data['jobs'][:5]:  # Show first 5
            print(f"  - {job['id']}: {job['status']} ({job['progress_percentage']:.1f}%)")

        return True
    else:
        print(f"✗ List jobs failed: {response.status_code}")
        return False


def main():
    """Run all API tests."""
    print("=" * 60)
    print("FastAPI Endpoint Tests")
    print("=" * 60)
    print()
    print("Make sure the API server is running:")
    print("  python -m video_api.main")
    print()

    results = []

    # Test health
    results.append(("Health Check", test_health()))
    time.sleep(0.5)

    # Test models
    results.append(("Models List", test_models()))
    time.sleep(0.5)

    # Test job creation (only if API keys configured)
    print("\n" + "=" * 60)
    print("Job Creation Test (Requires API Keys)")
    print("=" * 60)

    proceed = input("\nCreate a test job? This will use API credits. (y/n): ").lower()

    if proceed == 'y':
        job_id = test_create_job()
        time.sleep(1)

        if job_id:
            # Test get job
            results.append(("Create Job", True))
            test_get_job(job_id)
            time.sleep(0.5)

            # Test list jobs
            results.append(("List Jobs", test_list_jobs()))
        else:
            results.append(("Create Job", False))
    else:
        print("Skipping job creation test")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server")
        print("  Make sure the server is running: python -m video_api.main")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
