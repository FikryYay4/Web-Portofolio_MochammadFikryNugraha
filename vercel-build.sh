#!/bin/bash
# Vercel build script for Flask app
# Copy templates and static files to output directory

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating output directory..."
mkdir -p .vercel/output

echo "Copying templates..."
cp -r templates .vercel/output/

echo "Copying static files..."
cp -r static .vercel/output/

echo "Copying wsgi.py..."
cp wsgi.py .vercel/output/

echo "Build completed successfully!"