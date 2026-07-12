#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Done. Run 'python Big_movers_server.py' to start."
