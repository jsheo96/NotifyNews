#!/usr/bin/env python3
"""
Test runner script for NotifyNews project.
This script provides an easy way to run all tests and generate coverage reports.
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests with coverage."""
    print("Running NotifyNews test suite...")
    print("=" * 50)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--cov=.',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--tb=short'
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("Coverage report generated in htmlcov/index.html")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return e.returncode


def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"Running specific test: {test_file}")
    print("=" * 50)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run specific test
    cmd = [
        sys.executable, '-m', 'pytest',
        f'tests/{test_file}',
        '-v',
        '--tb=short'
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {test_file} passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_file} failed with exit code {e.returncode}")
        return e.returncode


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) == 1:
        # Run all tests
        return run_tests()
    elif len(sys.argv) == 2:
        # Run specific test file
        test_file = sys.argv[1]
        if not test_file.startswith('test_'):
            test_file = f'test_{test_file}'
        if not test_file.endswith('.py'):
            test_file = f'{test_file}.py'
        return run_specific_test(test_file)
    else:
        print("Usage:")
        print("  python run_tests.py                 # Run all tests")
        print("  python run_tests.py <test_file>     # Run specific test file")
        print("")
        print("Examples:")
        print("  python run_tests.py                 # Run all tests")
        print("  python run_tests.py googlewebhook   # Run test_googlewebhook.py")
        print("  python run_tests.py integration     # Run test_integration.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())