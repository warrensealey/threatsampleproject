#!/bin/bash
# Startup script for Email Data Generation application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

export PYTHONPATH=.:$PYTHONPATH
python3 backend/app.py

