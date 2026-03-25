#!/bin/sh

export PYTHONPATH="/app/src:$PYTHONPATH"
cd /app/src
python3 runner.py
