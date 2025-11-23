#!/bin/bash
# Startup script for Question Generator with environment variables

# Set working directory
cd /Users/rashpinderkaur/Desktop/Agent_Compute

# Set environment variables
export GEMINI_API_KEY="AIzaSyDsw7PUW8xj5Qgyv4CCnfMMrXowCtkMEpk"

# Optional: Set OpenAI API key if you have one
# export OPENAI_API_KEY="your-openai-api-key-here"

# Check if Gemini API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set"
else
    echo "✓ GEMINI_API_KEY is set"
fi

# Kill any existing server on port 5000
echo "Stopping any existing server on port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null

# Wait a moment
sleep 2

# Start the Flask server
echo "Starting Flask server..."
echo "  URL: http://localhost:5000"
echo "  Press Ctrl+C to stop"
echo ""

python3 app.py

