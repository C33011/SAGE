#!/usr/bin/env python
"""
A script to fix imports in test files.

This script scans all Python files in the tests directory and
replaces any instances of 'from src.sage' with 'from sage'.
"""
import os
import sys
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace imports
    modified_content = re.sub(
        r'from\s+src\.sage\b', 
        'from sage', 
        content
    )
    modified_content = re.sub(
        r'import\s+src\.sage\b', 
        'import sage', 
        content
    )
    
    # Check if file was modified
    if content != modified_content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        return True
    return False

def main():
    """Main function to fix imports in all test files."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    tests_dir = project_dir / 'tests'
    
    if not tests_dir.exists() or not tests_dir.is_dir():
        print(f"Tests directory not found at {tests_dir}")
        return
    
    # Find all Python files
    python_files = list(tests_dir.glob('**/*.py'))
    print(f"Found {len(python_files)} Python files in tests directory")
    
    # Fix imports in each file
    modified_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            modified_count += 1
            print(f"Fixed imports in {file_path.relative_to(project_dir)}")
    
    print(f"Completed! Modified {modified_count} files.")

if __name__ == '__main__':
    main()
