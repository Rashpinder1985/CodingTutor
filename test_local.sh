#!/bin/bash
# Quick local testing script

echo "=========================================="
echo "Local Testing Setup"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check dependencies
echo ""
echo "Checking dependencies..."
python3 -c "import flask, flask_sqlalchemy, cryptography" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "⚠️  Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Check database
echo ""
echo "Database setup:"
if [ -z "$DATABASE_URL" ]; then
    echo "✓ Using SQLite (default) - will create app.db"
else
    echo "✓ Using PostgreSQL: $DATABASE_URL"
fi

# Generate encryption key if needed
echo ""
if [ -z "$API_KEY_ENCRYPTION_KEY" ]; then
    echo "⚠️  API_KEY_ENCRYPTION_KEY not set (will auto-generate)"
    echo "   To set manually, run:"
    echo "   export API_KEY_ENCRYPTION_KEY=\$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
else
    echo "✓ API_KEY_ENCRYPTION_KEY is set"
fi

echo ""
echo "=========================================="
echo "Starting server..."
echo "=========================================="
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Open http://localhost:5000 in your browser"
echo "Press CTRL+C to stop"
echo ""

python app.py
