#!/bin/sh

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
docker run -v "$SCRIPT_DIR":/mubench svamann/mubench ./mubench.py "$@"
