#!/bin/bash
# Startup script for Email Data Generation application

cd ~/email-data-generation
export PYTHONPATH=.:$PYTHONPATH
python3 backend/app.py

