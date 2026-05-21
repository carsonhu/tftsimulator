#!/usr/bin/env bash
set -e

# Move into the deployment directory
cd /root/tftsimulator

# Cleanly sync with GitHub, forcing local files to mirror origin/main exactly
git fetch origin main
git reset --hard origin/main

# Activate the virtual environment and sync dependencies
source fastapi-venv/bin/activate
pip install -r requirements.txt

# Restart systemd services (using sudo to guarantee it doesn't hang or fail)
sudo systemctl restart fastapi
sudo systemctl restart streamlit