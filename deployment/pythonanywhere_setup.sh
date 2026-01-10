#!/bin/bash
# PythonAnywhere Setup Script
# Run this script after uploading files to PythonAnywhere

echo "=========================================="
echo "Mercedes Finder - PythonAnywhere Setup"
echo "=========================================="

# Install dependencies
echo "Installing dependencies..."
pip3 install --user -r requirements.txt

# Create database
echo "Creating database..."
python3 database.py

# Populate with demo data
echo "Adding demo data..."
python3 demo_data.py

# Test the system
echo "Testing system..."
python3 test_system.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure Web App in PythonAnywhere dashboard"
echo "2. Set WSGI file (see pythonanywhere_wsgi.py)"
echo "3. Set working directory to your project path"
echo "4. Reload web app"
echo "5. Configure scheduled task for daily scraping"
echo ""
