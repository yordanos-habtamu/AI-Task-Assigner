#!/bin/bash
# Run backend CLI for AI Task Assignment System

echo "🚀 Running AI Task Assignment (CLI mode)..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with your OPENAI_API_KEY"
    exit 1
fi

# Run backend
cd backend
echo "✓ Virtual environment activated"
echo "✓ Running assignment workflow..."
echo ""
python main.py
