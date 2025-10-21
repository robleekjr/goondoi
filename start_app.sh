#!/bin/bash
# Goondoi Wetlands Application Startup Script
# This script ensures environment variables are loaded and starts the application

echo "Starting Goondoi Wetlands Application..."

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | xargs)
else
    echo "Warning: .env file not found. Make sure environment variables are set."
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL not set. Please check your .env file."
    exit 1
fi

if [ -z "$AWS_S3_BUCKET" ]; then
    echo "Warning: AWS_S3_BUCKET not set. File uploads will use local storage."
fi

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
gunicorn -w 4 -b 0.0.0.0:8000 run:app --log-level info
