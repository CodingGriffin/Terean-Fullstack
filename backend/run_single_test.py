#!/usr/bin/env python
"""
Simple script to test if the test environment is set up correctly.
"""
import subprocess
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run a simple test
cmd = [sys.executable, "-m", "pytest", "-xvs", "tests/test_auth.py::TestPasswordHashing::test_password_hash_verification"]
print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd)
sys.exit(result.returncode) 