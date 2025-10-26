#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for E2E tests.
"""
import pytest
import subprocess
import time
from pathlib import Path


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "e2e_proce: E2E tests for message processing"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment before running tests.
    - Start localstack (SQS)
    - Create queues
    - Start consumer service
    """
    print("\n=== Setting up test environment ===")
    
    # Check if localstack is running
    try:
        subprocess.run(
            ["aws", "sqs", "list-queues", "--endpoint-url", "http://localhost:4566"],
            check=True,
            capture_output=True,
            timeout=5
        )
        print("✓ Localstack is running")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("✗ Localstack not running - please start it first")
        print("  Run: docker run -d -p 4566:4566 localstack/localstack")
        pytest.exit("Localstack not available", returncode=1)
    
    # Create queues
    queue_script = Path("/home/workspace/Documents/System/ParentZo-ChildZo/scripts/create_sqs_queues.sh")
    if queue_script.exists():
        try:
            subprocess.run([str(queue_script)], check=True, capture_output=True)
            print("✓ Queues created")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create queues: {e.stderr.decode()}")
            pytest.exit("Queue creation failed", returncode=1)
    
    yield
    
    # Cleanup
    print("\n=== Cleaning up test environment ===")
    # Purge queues
    for queue in ["proce-main", "proce-dlq"]:
        try:
            subprocess.run([
                "aws", "sqs", "purge-queue",
                "--endpoint-url", "http://localhost:4566",
                "--queue-url", f"http://localhost:4566/000000000000/{queue}"
            ], capture_output=True)
        except:
            pass


@pytest.fixture(scope="session")
def project_root():
    """Return project root directory."""
    return Path("/home/workspace/Documents/System/ParentZo-ChildZo")


@pytest.fixture(scope="function")
def clean_logs(project_root):
    """Clean log files before each test."""
    log_file = Path("/var/log/proce/consumer.log")
    if log_file.exists():
        log_file.unlink()
    
    yield
    
    # Archive logs after test
    if log_file.exists():
        test_name = os.environ.get("PYTEST_CURRENT_TEST", "unknown").split(":")[-1].split(" ")[0]
        archive_dir = project_root / "tests" / "logs" / test_name
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy(log_file, archive_dir / "consumer.log")


def pytest_collection_modifyitems(config, items):
    """Add custom test ordering if needed."""
    pass


def pytest_runtest_makereport(item, call):
    """Capture test results for reporting."""
    if call.when == "call":
        if call.excinfo is not None:
            # Test failed - could trigger additional logging here
            pass
