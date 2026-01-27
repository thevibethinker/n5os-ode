#!/usr/bin/env python3
"""
Pulse Integration Tests: Post-build verification that everything works together.

Each build can define integration tests in:
  N5/builds/<slug>/INTEGRATION_TESTS.json

Format:
{
  "tests": [
    {
      "name": "API responds",
      "type": "http",
      "config": {"url": "http://localhost:3000/health", "expected_status": 200}
    },
    {
      "name": "File exists",
      "type": "file_exists",
      "config": {"path": "Sites/mysite/dist/index.html"}
    },
    {
      "name": "Command succeeds",
      "type": "command",
      "config": {"cmd": "cd Sites/mysite && bun run build", "expected_exit": 0}
    },
    {
      "name": "File contains",
      "type": "file_contains",
      "config": {"path": "Sites/mysite/package.json", "contains": "\"name\": \"mysite\""}
    }
  ]
}

Usage:
  pulse_integration_test.py run <slug>
  pulse_integration_test.py generate <slug>  # Auto-generate from artifacts
  pulse_integration_test.py add <slug> --type <type> --config <json>
"""

import argparse
import json
import os
import subprocess
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from pulse_common import PATHS, WORKSPACE

BUILDS_DIR = WORKSPACE / "N5" / "builds"


def load_tests(slug: str) -> dict:
    """Load integration tests for a build"""
    path = BUILDS_DIR / slug / "INTEGRATION_TESTS.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"tests": []}


def save_tests(slug: str, data: dict):
    """Save integration tests"""
    path = BUILDS_DIR / slug / "INTEGRATION_TESTS.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def run_test_file_exists(config: dict) -> tuple[bool, str]:
    """Test that a file exists"""
    path = WORKSPACE / config["path"]
    if path.exists():
        return True, f"File exists: {config['path']}"
    return False, f"File missing: {config['path']}"


def run_test_file_contains(config: dict) -> tuple[bool, str]:
    """Test that a file contains expected content"""
    path = WORKSPACE / config["path"]
    if not path.exists():
        return False, f"File missing: {config['path']}"
    
    with open(path) as f:
        content = f.read()
    
    if config["contains"] in content:
        return True, f"File contains expected content"
    return False, f"File missing expected content: {config['contains'][:50]}..."


def run_test_command(config: dict) -> tuple[bool, str]:
    """Test that a command succeeds"""
    try:
        result = subprocess.run(
            config["cmd"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=config.get("timeout", 60),
            cwd=str(WORKSPACE)
        )
        expected = config.get("expected_exit", 0)
        if result.returncode == expected:
            return True, f"Command succeeded (exit {result.returncode})"
        return False, f"Command failed (exit {result.returncode}, expected {expected}): {result.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {config.get('timeout', 60)}s"
    except Exception as e:
        return False, f"Command error: {str(e)}"


def run_test_http(config: dict) -> tuple[bool, str]:
    """Test HTTP endpoint"""
    try:
        resp = requests.request(
            config.get("method", "GET"),
            config["url"],
            timeout=config.get("timeout", 10),
            headers=config.get("headers", {}),
            json=config.get("body")
        )
        expected = config.get("expected_status", 200)
        if resp.status_code == expected:
            # Optional: check response body
            if "expected_body_contains" in config:
                if config["expected_body_contains"] not in resp.text:
                    return False, f"Response missing expected content"
            return True, f"HTTP {resp.status_code} OK"
        return False, f"HTTP {resp.status_code} (expected {expected})"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except Exception as e:
        return False, f"HTTP error: {str(e)}"


def run_test_service_running(config: dict) -> tuple[bool, str]:
    """Test that a service is running"""
    try:
        result = subprocess.run(
            f"pgrep -f '{config['process_name']}'",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, f"Service running: {config['process_name']}"
        return False, f"Service not running: {config['process_name']}"
    except Exception as e:
        return False, f"Check failed: {str(e)}"


TEST_RUNNERS = {
    "file_exists": run_test_file_exists,
    "file_contains": run_test_file_contains,
    "command": run_test_command,
    "http": run_test_http,
    "service_running": run_test_service_running,
}


def run_single_test(test: dict) -> dict:
    """Run a single test and return result"""
    test_type = test.get("type")
    config = test.get("config", {})
    
    if test_type not in TEST_RUNNERS:
        return {
            "name": test.get("name", "unnamed"),
            "type": test_type,
            "passed": False,
            "message": f"Unknown test type: {test_type}"
        }
    
    runner = TEST_RUNNERS[test_type]
    passed, message = runner(config)
    
    return {
        "name": test.get("name", "unnamed"),
        "type": test_type,
        "passed": passed,
        "message": message
    }


def run_all_tests(slug: str) -> dict:
    """Run all integration tests for a build"""
    data = load_tests(slug)
    tests = data.get("tests", [])
    
    if not tests:
        return {
            "slug": slug,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total": 0,
            "passed": 0,
            "failed": 0,
            "results": [],
            "all_passed": True,
            "message": "No integration tests defined"
        }
    
    results = []
    passed = 0
    failed = 0
    
    for test in tests:
        result = run_single_test(test)
        results.append(result)
        if result["passed"]:
            passed += 1
        else:
            failed += 1
    
    return {
        "slug": slug,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        "results": results,
        "all_passed": failed == 0
    }


def generate_tests_from_artifacts(slug: str) -> list:
    """Auto-generate basic tests from build artifacts"""
    tests = []
    deposits_dir = BUILDS_DIR / slug / "deposits"
    
    if not deposits_dir.exists():
        return tests
    
    # Collect all artifacts from deposits
    artifacts = set()
    for deposit_path in deposits_dir.glob("*.json"):
        if "_filter" in deposit_path.name:
            continue
        with open(deposit_path) as f:
            deposit = json.load(f)
        for artifact in deposit.get("artifacts", []):
            if isinstance(artifact, str):
                artifacts.add(artifact)
            elif isinstance(artifact, dict):
                artifacts.add(artifact.get("path", ""))
    
    # Generate file_exists tests for each artifact
    for artifact in artifacts:
        if artifact and not artifact.startswith("/"):
            # Relative path - prepend build artifacts dir or assume workspace-relative
            tests.append({
                "name": f"Artifact exists: {Path(artifact).name}",
                "type": "file_exists",
                "config": {"path": artifact}
            })
    
    return tests


def add_test(slug: str, test_type: str, name: str, config: dict):
    """Add a test to a build"""
    data = load_tests(slug)
    data["tests"].append({
        "name": name,
        "type": test_type,
        "config": config
    })
    save_tests(slug, data)
    print(f"Added test: {name}")


def main():
    parser = argparse.ArgumentParser(description="Pulse Integration Tests")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # run
    run_parser = subparsers.add_parser("run", help="Run integration tests")
    run_parser.add_argument("slug", help="Build slug")
    run_parser.add_argument("--verbose", "-v", action="store_true")
    
    # generate
    gen_parser = subparsers.add_parser("generate", help="Auto-generate tests from artifacts")
    gen_parser.add_argument("slug", help="Build slug")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a test")
    add_parser.add_argument("slug", help="Build slug")
    add_parser.add_argument("--type", required=True, choices=list(TEST_RUNNERS.keys()))
    add_parser.add_argument("--name", required=True, help="Test name")
    add_parser.add_argument("--config", required=True, help="Config as JSON string")
    
    args = parser.parse_args()
    
    if args.command == "run":
        results = run_all_tests(args.slug)
        
        print(f"\n{'='*50}")
        print(f"Integration Tests: {args.slug}")
        print(f"{'='*50}\n")
        
        if results["total"] == 0:
            print("No tests defined. Run 'generate' to auto-create from artifacts.")
        else:
            for r in results["results"]:
                status = "✅" if r["passed"] else "❌"
                print(f"{status} {r['name']}")
                if args.verbose or not r["passed"]:
                    print(f"   {r['message']}")
            
            print(f"\n{'='*50}")
            print(f"Results: {results['passed']}/{results['total']} passed")
            
            if results["all_passed"]:
                print("✅ ALL TESTS PASSED")
            else:
                print(f"❌ {results['failed']} TESTS FAILED")
        
        # Save results
        results_path = BUILDS_DIR / args.slug / "INTEGRATION_RESULTS.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {results_path}")
        
        # Exit with error if tests failed
        if not results["all_passed"]:
            exit(1)
    
    elif args.command == "generate":
        tests = generate_tests_from_artifacts(args.slug)
        if not tests:
            print("No artifacts found to generate tests from.")
        else:
            data = load_tests(args.slug)
            data["tests"].extend(tests)
            save_tests(args.slug, data)
            print(f"Generated {len(tests)} tests:")
            for t in tests:
                print(f"  - {t['name']}")
    
    elif args.command == "add":
        config = json.loads(args.config)
        add_test(args.slug, args.type, args.name, config)


if __name__ == "__main__":
    main()
