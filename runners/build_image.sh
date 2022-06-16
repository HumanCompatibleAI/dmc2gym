#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

__usage="build_image.sh - Building and pushing Docker image
Usage: build_image.sh [options] [tags]
options:
  -h, --help                show brief help
tags:
  base                      base stage image
  dev                       dev stage image
"

KEYS=""
PUSH=0

while test $# -gt 0; do
  case "$1" in
  base)
    KEYS+="base "
    shift
    ;;
  dev)
    KEYS+="dev "
    shift
    ;;
  -h | --help)
    echo "${__usage}"
    exit 0
    ;;
  *)
    echo "Unrecognized flag $1" >&2
    exit 1
    ;;
  esac
done

if [[ -z $KEYS ]]; then
  KEYS="base"
  echo "No tag found in the arguments! Building default image kmdanielduan/dmc2gym:${KEYS}"
fi

for key in $KEYS; do
  # Build image
  echo "----- Building kmdanielduan/dmc2gym:${key} ..."
  docker build --target ${key} -t kmdanielduan/dmc2gym:${key} .
done