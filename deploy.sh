#!/usr/bin/env bash
set -e

cd /root/tftsimulator

# Pull latest code
git fetch origin
git checkout fastapi        # or main
git pull origin fastapi

# Update deps in the venv you use for the app/API
source fastapi-venv/bin/activate   # or whatever your venv is
pip install -r requirements.txt

# Restart services
systemctl restart fastapi
systemctl restart streamlit