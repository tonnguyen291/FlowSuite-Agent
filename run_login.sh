#!/bin/zsh
set -euo pipefail

if [ -d "/Users/tonnguyen/venv" ]; then
  source /Users/tonnguyen/venv/bin/activate
fi

python /Users/tonnguyen/wordpress_data_agent/login_agent.py

