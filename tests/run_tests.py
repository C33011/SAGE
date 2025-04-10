"""
Test runner for SAGE project.

This module discovers and runs all tests in the tests directory.
"""

import unittest
import os
import sys
from pathlib import Path

def run_all_tests(test_pattern=None, stop_on_failure=False):
    """
    Discover and run all tests in the tests directory.
    
    Args:
        test_pattern: Optional pattern to filter test names
        stop_on_failure: If True, stop on first test failure
    
    Returns:
        True if all tests passed, False otherwise
    """
    # Get the directory containing this file
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get project root directory
    project_dir = Path(tests_dir).parent
    
    # Clear any existing import cache for sage modules
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('sage.'):
            del sys.modules[module_name]
    
    # Add src directory to the Python path
    # This is the standard structure for packages
    src_dir = project_dir / 'src'
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
        print(f"Added src to Python path: {src_dir}")
    
    # Add project root to path as well
    sys.path.insert(0, str(project_dir))
    print(f"Added project root to Python path: {project_dir}")
    
    # Print project structure to help debug
    print("\nProject structure:")
    print(f"Project root: {project_dir}")
    
    # Check src directory structure
    if src_dir.exists():
        print(f"Found src directory")
        sage_dir = src_dir / 'sage'
        if sage_dir.exists():
            print(f"Found sage package at {sage_dir}")
            # List contents to help with debugging
            print("Sage package contains:")
            for item in sage_dir.glob('*'):
                if item.is_dir():
                    print(f"  - Directory: {item.name}")
                elif item.is_file() and item.name.endswith('.py'):
                    print(f"  - Module: {item.name}")
        else:
            print(f"Warning: sage package not found in src directory")
    
    # Create __init__.py file in tests dir if it doesn't exist
    tests_init = os.path.join(tests_dir, "__init__.py")
    if not os.path.exists(tests_init):
        with open(tests_init, 'w') as f:
            f.write("# Test package initialization")
        print(f"Created tests/__init__.py file for proper test discovery")
    
    # Check if required packages are installed
    missing_packages = []
    for package in ['pandas', 'numpy', 'sqlalchemy', 'jinja2', 'matplotlib']:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"✗ Missing required packages: {', '.join(missing_packages)}")
        print(f"Please install required packages with: pip install {' '.join(missing_packages)}")
    else:
        print("✓ All required packages are installed")
    
    print(f"Current Python path (first 5 entries): {sys.path[:5]}")
    
    # Try importing a key module to verify imports are working
    print("\nTesting imports:")
    import_success = True
    for module_name in ["sage", "sage.graders", "sage.metrics", "sage.reports"]:
        try:
            module = __import__(module_name, fromlist=["dummy"])
            print(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")
            import_success = False
    
    if not import_success:
        print("\nWARNING: Some imports failed. Tests may not run correctly.")
    
    # Discover and run tests
    print("\nDiscovering tests...")
    loader = unittest.TestLoader()
    
    # If a test pattern is provided, use it to filter tests
    if test_pattern:
        print(f"Filtering tests using pattern: {test_pattern}")
        suite = loader.discover(tests_dir, pattern=test_pattern)
    else:
        suite = loader.discover(tests_dir)
    
    # Get test count
    test_count = suite.countTestCases()
    print(f"Found {test_count} tests")
    
    if test_count == 0:
        print("No tests found! Check your test files and patterns.")
        return False
    
    # Create a test runner and run the tests
    if stop_on_failure:
        runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    else:
        runner = unittest.TextTestRunner(verbosity=2)
    
    print("\nRunning tests...")
    result = runner.run(suite)
    
    # Print summary
    print("\nTest Results Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    # If there were failures or errors, print them in a more readable format
    if result.failures or result.errors:
        print("\nFailed Tests:")
        
        for i, (test, traceback) in enumerate(result.failures, 1):
            test_name = str(test)
            # Extract just the test method name for clearer output
            method_name = test_name.split(' ')[0]
            print(f"  {i}. FAIL: {method_name}")
            # Get the first line of the traceback that's not part of unittest
            error_lines = [line for line in traceback.split('\n') 
                          if 'File "' in line and 'unittest' not in line]
            if error_lines:
                print(f"     {error_lines[0].strip()}")
            else:
                print(f"     See full traceback for details")
        
        for i, (test, traceback) in enumerate(result.errors, 1):
            test_name = str(test)
            # Extract just the test method name for clearer output
            method_name = test_name.split(' ')[0]
            print(f"  {i}. ERROR: {method_name}")
            # Get the first line of the traceback that's not part of unittest
            error_lines = [line for line in traceback.split('\n') 
                          if 'File "' in line and 'unittest' not in line]
            if error_lines:
                print(f"     {error_lines[0].strip()}")
            else:
                print(f"     See full traceback for details")
        
        print("\nRun specific failed tests with:")
        print(f"  python {__file__} -p test_*.py -n TestClass.test_method")
    
    # Return True if all tests passed, False otherwise
    return result.wasSuccessful()

if __name__ == '__main__':
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Run SAGE tests')
    parser.add_argument('-p', '--pattern', help='Pattern for test files (e.g., "test_*.py")')
    parser.add_argument('-n', '--name', help='Specific test name to run (e.g., "TestClass.test_method")')
    parser.add_argument('-f', '--failfast', action='store_true', help='Stop on first failure')
    
    args = parser.parse_args()
    
    # Build test pattern based on arguments
    test_pattern = None
    if args.pattern:
        test_pattern = args.pattern
    elif args.name:
        # If only a test name is provided, discover all test files but filter by name
        loader = unittest.TestLoader()
        if '.' in args.name:
            # If class.method format is provided
            class_name, method_name = args.name.split('.')
            loader.testMethodPrefix = method_name
        else:
            # If only class name is provided
            loader.testMethodPrefix = args.name
    
    # Run tests with the specified pattern and options
    success = run_all_tests(test_pattern=test_pattern, stop_on_failure=args.failfast)
    
    # Exit with an appropriate status code
    sys.exit(0 if success else 1)
