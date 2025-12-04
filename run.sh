#!/bin/bash
# Run script for AI Task Assignment System

echo "🚀 Starting AI Task Assignment System..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Check if .env exists and has API key
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with your OPENAI_API_KEY"
    exit 1
fi

# Run Streamlit
echo "✓ Virtual environment activated"
echo "✓ Starting Streamlit server..."
echo ""
streamlit run frontend/app.py
