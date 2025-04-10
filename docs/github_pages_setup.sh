#!/bin/bash

# This script sets up GitHub Pages for your SAGE documentation
# Run this script from your repository root

# 1. Create a gh-pages branch (if it doesn't exist)
git checkout --orphan gh-pages

# 2. Remove everything except the documentation build
git rm -rf .
git clean -fxd

# 3. Copy documentation build to the root of this branch
# (Assuming your docs are built in docs/_build/html)
cp -r docs/_build/html/* .

# 4. Create a .nojekyll file to disable Jekyll processing
touch .nojekyll

# 5. Add all files, commit, and push to GitHub
git add .
git commit -m "Initial documentation deployment"
git push origin gh-pages

# 6. Switch back to your main branch
git checkout main
