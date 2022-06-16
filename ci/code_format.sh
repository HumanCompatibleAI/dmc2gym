#!/usr/bin/env bash

# If you change these, also change .circle/config.yml.
SRC_FILES=(src/ tests/ setup.py)

set -x  # echo commands
set -e  # quit immediately on error

echo "Source code formatting"
isort ${SRC_FILES[@]}
black ${SRC_FILES[@]} 