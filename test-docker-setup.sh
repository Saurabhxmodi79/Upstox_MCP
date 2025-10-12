#!/bin/bash

# Test script to validate Docker setup
echo "🧪 Testing Upstox MCP Docker Setup"
echo "=================================="

# Check if all required files exist
files=(
    "Dockerfile"
    "docker-compose.yml"
    "env.example"
    "setup.sh"
    "upstox_server.py"
    "upstox_auth.py"
    "authenticate.py"
    "config.py"
    "pyproject.toml"
)

echo "📁 Checking required files..."
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done

# Check if gitignore includes sensitive files
echo ""
echo "🔒 Checking .gitignore..."
if grep -q "upstox_token.json" .gitignore; then
    echo "✅ upstox_token.json is ignored"
else
    echo "❌ upstox_token.json should be in .gitignore"
fi

if grep -q ".env" .gitignore; then
    echo "✅ .env is ignored"
else
    echo "❌ .env should be in .gitignore"
fi

# Validate Dockerfile syntax
echo ""
echo "🐳 Validating Dockerfile..."
if [ -f "Dockerfile" ]; then
    if grep -q "FROM python:" Dockerfile; then
        echo "✅ Dockerfile has valid Python base image"
    else
        echo "❌ Dockerfile missing Python base image"
    fi
    
    if grep -q "WORKDIR" Dockerfile; then
        echo "✅ Dockerfile sets working directory"
    else
        echo "❌ Dockerfile missing WORKDIR"
    fi
fi

# Validate docker-compose.yml
echo ""
echo "🐙 Validating docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    if grep -q "version:" docker-compose.yml; then
        echo "✅ docker-compose.yml has version specified"
    else
        echo "❌ docker-compose.yml missing version"
    fi
    
    if grep -q "upstox-mcp:" docker-compose.yml; then
        echo "✅ docker-compose.yml defines upstox-mcp service"
    else
        echo "❌ docker-compose.yml missing upstox-mcp service"
    fi
fi

echo ""
echo "🎯 Setup validation complete!"
echo ""
echo "📋 To use this Docker setup:"
echo "1. Install Docker and Docker Compose"
echo "2. Get Upstox API credentials"
echo "3. Run: ./setup.sh"
echo "4. Configure Claude Desktop with the provided config"
