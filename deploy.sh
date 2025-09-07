#!/bin/bash

# Lead Nurturing System Deployment Script
# This script sets up the 24/7 MCP server for lead nurturing

set -e

echo "🚀 Deploying Lead Nurturing MCP Server..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

# Check for required files
echo "🔍 Checking required files..."
required_files=("credentials.json" "contacts.csv" "body.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file $file not found!"
        exit 1
    fi
done

# Create nurturing_config.json if it doesn't exist
if [ ! -f "nurturing_config.json" ]; then
    echo "📝 Creating default nurturing_config.json..."
    cat > nurturing_config.json << EOF
{
  "sender_email": "brandon@quantralabs.com",
  "sender_name": "Brandon",
  "company_name": "Quantra Labs",
  "follow_up_schedule": {
    "followup_1_days": 3,
    "followup_2_days": 7,
    "max_follow_ups": 2
  },
  "response_keywords": {
    "interested": ["interested", "yes", "demo", "call", "meeting", "schedule", "book"],
    "not_interested": ["not interested", "no thanks", "stop", "unsubscribe", "remove"]
  },
  "lead_scoring": {
    "response_bonus": 10,
    "interest_bonus": 5,
    "follow_up_penalty": -1
  },
  "automation": {
    "check_responses_interval_hours": 4,
    "auto_respond_to_interest": true,
    "auto_send_follow_ups": true
  }
}
EOF
fi

# Build and start the service
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting Lead Nurturing MCP Server..."
docker-compose up -d

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check if service is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Lead Nurturing MCP Server is running!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "📋 Logs:"
    docker-compose logs --tail=20
    echo ""
    echo "🎯 Your lead nurturing system is now running 24/7!"
    echo "📱 Use the MCP client to control and monitor the system."
    echo ""
    echo "🔧 Useful commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop service: docker-compose down"
    echo "  Restart service: docker-compose restart"
    echo "  Update service: docker-compose pull && docker-compose up -d"
else
    echo "❌ Failed to start the service. Check logs:"
    docker-compose logs
    exit 1
fi
