#!/bin/bash
# Setup script for Adaptive Question Generator

echo "================================================"
echo "Adaptive Question Generator - Setup"
echo "================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Check for Ollama
echo "🤖 Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found"
    echo ""
    echo "📥 Pulling llama3.2 model (this may take a few minutes)..."
    ollama pull llama3.2
    echo "✓ Model downloaded"
else
    echo "⚠️  Ollama not found"
    echo ""
    echo "To use local AI (recommended):"
    echo "  1. Install Ollama from: https://ollama.ai/download"
    echo "  2. Run: ollama pull llama3.2"
    echo ""
    echo "Or use OpenAI instead:"
    echo "  1. Edit config.yaml and set provider to 'openai'"
    echo "  2. Set your OPENAI_API_KEY in environment"
fi

echo ""
echo "================================================"
echo "✓ Setup Complete!"
echo "================================================"
echo ""
echo "To start the server:"
echo "  python3 app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""

