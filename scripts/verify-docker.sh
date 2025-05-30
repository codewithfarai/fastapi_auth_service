#!/bin/bash

# Docker Setup Verification Script
# This script verifies that Docker is properly installed and configured

set -e

echo "🐳 Docker Setup Verification"
echo "============================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker installation
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    docker --version
else
    echo -e "${RED}✗ Docker is not installed or not in PATH${NC}"
    echo "Please install Docker Desktop and enable WSL2 integration"
    echo "Visit: https://docs.docker.com/desktop/wsl/"
    exit 1
fi

echo ""

# Check Docker Compose
echo "2. Checking Docker Compose..."
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose (plugin) is available${NC}"
    docker compose version
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose (standalone) is available${NC}"
    docker-compose --version
else
    echo -e "${RED}✗ Docker Compose is not available${NC}"
    exit 1
fi

echo ""

# Check Docker daemon
echo "3. Checking Docker daemon..."
if docker info &> /dev/null; then
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
else
    echo -e "${RED}✗ Docker daemon is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi

echo ""

# Check if we can pull images
echo "4. Testing Docker connectivity..."
if docker pull alpine:latest &> /dev/null; then
    echo -e "${GREEN}✓ Can pull Docker images${NC}"
else
    echo -e "${RED}✗ Cannot pull Docker images${NC}"
    echo "Check your internet connection and Docker Hub access"
    exit 1
fi

echo ""

# Check Make
echo "5. Checking Make installation..."
if command -v make &> /dev/null; then
    echo -e "${GREEN}✓ Make is installed${NC}"
    make --version | head -n1
else
    echo -e "${YELLOW}⚠ Make is not installed${NC}"
    echo "You can install it with: sudo apt-get install make"
    echo "Or use docker compose commands directly"
fi

echo ""

# Check project files
echo "6. Checking project files..."
files=("Dockerfile" "docker-compose.yml" "docker-compose.dev.yml" ".dockerignore" "Makefile")
all_exist=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file is missing${NC}"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo -e "${RED}Some required files are missing${NC}"
    exit 1
fi

echo ""

# Check environment file
echo "7. Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
elif [ -f ".env.example" ]; then
    echo -e "${YELLOW}⚠ .env file missing, but .env.example exists${NC}"
    echo "Run: cp .env.example .env"
else
    echo -e "${YELLOW}⚠ No .env file found${NC}"
    echo "Run: make env-example && cp .env.example .env"
fi

echo ""

# Final summary
echo "============================"
echo "🎉 Docker setup verification complete!"
echo ""
echo "Next steps:"
echo "1. If you haven't already, create your .env file:"
echo "   make env-example && cp .env.example .env"
echo ""
echo "2. Build and start the development environment:"
echo "   make dev"
echo ""
echo "3. Or manually:"
echo "   docker compose -f docker-compose.dev.yml build"
echo "   docker compose -f docker-compose.dev.yml up -d"
echo ""
echo "Happy coding! 🚀"
