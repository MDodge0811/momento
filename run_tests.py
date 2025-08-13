#!/usr/bin/env python3
"""
Test runner script for Eidex library.
Run with: python run_tests.py
"""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite using pytest."""
    print("🧪 Running Eidex test suite...")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], check=True)
        print("✅ Test dependencies installed.")
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=eidex",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/ directory")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
