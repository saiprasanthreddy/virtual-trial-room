#!/bin/bash

echo "================================"
echo "Virtual Trial Room Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your GEMINI_API_KEY"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
else
    echo "✓ .env file found"
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To start the application:"
echo "  python app.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:5000"
echo ""
