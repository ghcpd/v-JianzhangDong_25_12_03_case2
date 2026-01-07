#!/bin/bash

# Environment Setup Script for Linux/macOS
# This script sets up the Python virtual environment and installs dependencies

set -e

echo "=========================================="
echo "Setting up Python environment..."
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Display Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p configs
mkdir -p logs

# Set environment variables (for development/testing only)
echo ""
echo "=========================================="
echo "Setting environment variables..."
echo "=========================================="
export PAYMENT_TOKEN="test_token_123"
export MAIL_SERVER_KEY="test_mail_key_456"
export INTERNAL_AUTH="test_auth_789"
export ALLOWED_DOMAINS="localhost,127.0.0.1"
export ALLOWED_CONFIG_DIR="./configs"
export FLASK_DEBUG="False"

echo "Environment variables set (test values)."
echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment manually, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python inputs.py"
echo ""
