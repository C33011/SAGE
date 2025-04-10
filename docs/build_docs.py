"""
Script to build the SAGE documentation.
Run this script from the docs directory to generate HTML documentation.
"""

import os
import subprocess
import sys
import shutil

# Create necessary directories
os.makedirs('_build/html', exist_ok=True)
os.makedirs('modules', exist_ok=True)

# Generate module documentation
if not os.path.exists('modules/index.rst'):
    with open('modules/index.rst', 'w') as f:
        f.write('''API Reference
============

.. toctree::
   :maxdepth: 2

   sage
''')

# Generate the API documentation using sphinx-apidoc
subprocess.run([
    'sphinx-apidoc',
    '-o',
    'modules',
    '--force',
    '--module-first',
    '../src/sage'
])

# Build the HTML documentation
build_result = subprocess.run(['sphinx-build', '-b', 'html', '.', '_build/html'])

if build_result.returncode == 0:
    print("\nDocumentation built successfully! Open _build/html/index.html to view it.")
else:
    print("\nError building documentation. Check the output above for details.")
    sys.exit(1)
