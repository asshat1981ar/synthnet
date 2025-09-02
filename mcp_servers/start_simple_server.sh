#!/bin/bash
# Start Simple GitHub MCP Server for SynthNet AI
# Optimized for Termux/Android environments

set -e

echo "🚀 Starting Simple GitHub MCP Server for SynthNet AI..."

# Base directory
BASE_DIR="/data/data/com.termux/files/home/synthnet"
MCP_DIR="$BASE_DIR/mcp_servers"
LOGS_DIR="$BASE_DIR/logs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Check if GitHub token is set
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo -e "${YELLOW}⚠️  Warning: GITHUB_TOKEN not set${NC}"
    echo "Some features will be limited without authentication"
    echo ""
    echo "To set your GitHub token:"
    echo -e "${BLUE}export GITHUB_TOKEN='your_github_token_here'${NC}"
    echo ""
    echo "Get a token from: https://github.com/settings/tokens"
    echo ""
    read -p "Continue without token? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please set GITHUB_TOKEN and try again."
        exit 1
    fi
else
    echo -e "${GREEN}✅ GitHub token configured${NC}"
fi

# Function to start server
start_server() {
    echo "Starting Simple GitHub MCP Server..."
    echo "Logs will be written to: $LOGS_DIR/simple_github_mcp.log"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "=" * 50
    
    # Start server with logging
    python3 "$MCP_DIR/simple_github_mcp_server.py" 2>&1 | tee "$LOGS_DIR/simple_github_mcp.log"
}

# Function to test server
test_server() {
    echo "Running server tests..."
    python3 "$MCP_DIR/simple_github_mcp_server.py" --test
    echo ""
    echo -e "${GREEN}✅ Server tests completed${NC}"
}

# Parse command line arguments
case "${1:-start}" in
    "start")
        start_server
        ;;
    "test")
        test_server
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [start|test|help]"
        echo ""
        echo "Commands:"
        echo "  start  - Start the MCP server (default)"
        echo "  test   - Run server tests"
        echo "  help   - Show this help message"
        echo ""
        echo "Environment variables:"
        echo "  GITHUB_TOKEN - GitHub personal access token (optional but recommended)"
        echo ""
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac