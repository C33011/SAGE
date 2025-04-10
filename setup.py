"""
Setup script for SAGE package.
"""

import setuptools
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="sage-data-quality",
    version="0.1.0",
    author="Tate Matthews",
    author_email="your.email@example.com",
    description="Spreadsheet Analysis Grading Engine for data quality assessment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sage",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/sage/issues",
        "Documentation": "https://github.com/yourusername/sage#readme",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "matplotlib>=3.4.0",
        "sqlalchemy>=1.4.0",
        "openpyxl>=3.0.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "sphinx",
            "sphinx_rtd_theme",
        ],
        "viz": [
            "plotly>=5.0.0",
        ],
    },
)
