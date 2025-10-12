#!/bin/bash

# Upstox MCP Server Setup Script
echo "🚀 Setting up Upstox MCP Server with Docker"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Create data directory
mkdir -p data

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your Upstox API credentials:"
    echo "   - Get API credentials from: https://upstox.com/developer/apps"
    echo "   - Edit .env file and add your API_KEY and API_SECRET"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
fi

# Source the .env file to check credentials
source .env

if [ "$UPSTOX_API_KEY" = "your_api_key_here" ] || [ -z "$UPSTOX_API_KEY" ]; then
    echo "❌ Please update your .env file with actual Upstox API credentials"
    exit 1
fi

echo "✅ Configuration looks good!"

# Build and start the container
echo "🏗️  Building Docker image..."
docker-compose build

echo "🔐 Starting authentication helper..."
echo "📱 This will help you authenticate with Upstox"
echo "🌐 Open http://localhost:8081 in your browser"

# Run authentication helper
docker-compose --profile auth up upstox-auth-helper

# Check if token was created
if [ -f "upstox_token.json" ]; then
    echo "✅ Authentication successful!"
    echo "🚀 Starting Upstox MCP server..."
    docker-compose up -d upstox-mcp
    echo ""
    echo "🎉 Upstox MCP Server is now running!"
    echo "📋 Add this to your Claude Desktop config:"
    echo ""
    echo '{
  "mcpServers": {
    "upstox-mcp": {
      "command": "docker",
      "args": [
        "exec",
        "upstox-mcp-server",
        "uv",
        "run",
        "upstox_server.py"
      ]
    }
  }
}'
    echo ""
    echo "🔍 To view logs: docker-compose logs -f upstox-mcp"
    echo "🛑 To stop: docker-compose down"
else
    echo "❌ Authentication failed. Please try again."
fi
