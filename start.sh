#!/bin/bash
# Render deployment script
echo "Starting IPL Mock Auction deployment..."

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py