#!/usr/bin/env bash

# If you change these, also change .circleci/config.yml.
SRC_FILES=(src/ tests/ setup.py)

set -x  # echo commands
set -e  # quit immediately on error

echo "Source format checking"
flake8 "${SRC_FILES[@]}"
black --check --diff "${SRC_FILES[@]}"
codespell "${SRC_FILES[@]}"

echo "Type checking"
pytype -j auto ${SRC_FILES[@]}