#!/bin/bash

# Activate virtual environment
source venv/bin/activate

echo "🔐 Starting OAuth Server..."
echo ""

# Run Flask OAuth server
python -m backend.oauth_server
