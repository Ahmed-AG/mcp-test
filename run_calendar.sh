#!/bin/bash
cd /Users/aag/Downloads/CalMCP/
source venv/bin/activate
export GOOGLE_SERVICE_ACCOUNT_KEY=$(cat aviata-426903-42b52c15666d.json)
# export GOOGLE_SERVICE_ACCOUNT_KEY=$1
python main.py
