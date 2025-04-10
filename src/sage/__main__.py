"""
Main entry point for the SAGE command-line interface.

This module allows SAGE to be run from the command line with:
    python -m sage <command> [options]
"""

import sys
from sage.cli.commands import main

if __name__ == "__main__":
    sys.exit(main())
