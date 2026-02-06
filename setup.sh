#!/bin/bash

# Quick start script for Seller Intelligence Copilot

echo "🚀 Starting Seller Intelligence Copilot..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "⚠️  Warning: Ollama is not running or not accessible at http://localhost:11434"
    echo "   Please start Ollama before running this script."
    echo "   Install: https://ollama.com"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the services, run in separate terminals:"
echo ""
echo "  Terminal 1 (Mock Services):"
echo "  $ source venv/bin/activate"
echo "  $ python mock_services_app.py"
echo ""
echo "  Terminal 2 (Main API):"
echo "  $ source venv/bin/activate"
echo "  $ python main.py"
echo ""
echo "Then visit: http://localhost:8000/docs"
echo ""
