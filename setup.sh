#!/bin/bash
# setup.sh - Setup script for Linux/macOS

set -e

echo "=== Flask Security Audit Setup ==="
echo "OS: $(uname -s)"
echo "Python version:"
python3 --version

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo "=== Setup Complete ==="
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "To deactivate, run: deactivate"
