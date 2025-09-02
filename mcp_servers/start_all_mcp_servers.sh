#!/bin/bash
# Start All MCP Servers for SynthNet AI
# Comprehensive MCP server orchestration script

set -e

echo "🚀 Starting All SynthNet MCP Servers..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/data/data/com.termux/files/home/synthnet"
MCP_DIR="$BASE_DIR/mcp_servers"
LOGS_DIR="$BASE_DIR/logs"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Load environment variables
if [[ -f "$BASE_DIR/.env" ]]; then
    source "$BASE_DIR/.env"
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
fi

# Function to start a server
start_server() {
    local server_name=$1
    local server_file=$2
    local port=$3
    local description=$4
    
    echo -e "\n${BLUE}Starting $server_name...${NC}"
    echo "Description: $description"
    echo "Port: $port"
    echo "Log file: $LOGS_DIR/${server_name,,}_mcp.log"
    
    # Start server in background
    cd "$MCP_DIR"
    nohup python3 "$server_file" > "$LOGS_DIR/${server_name,,}_mcp.log" 2>&1 &
    local pid=$!
    
    # Wait a moment to see if server starts successfully
    sleep 2
    
    if kill -0 $pid 2>/dev/null; then
        echo -e "${GREEN}✅ $server_name started successfully (PID: $pid)${NC}"
        echo "$pid" > "$LOGS_DIR/${server_name,,}_mcp.pid"
    else
        echo -e "${RED}❌ $server_name failed to start${NC}"
        echo "Check log: tail -f $LOGS_DIR/${server_name,,}_mcp.log"
    fi
}

# Function to test server availability
test_server() {
    local server_name=$1
    local server_file=$2
    
    echo -e "\n${BLUE}Testing $server_name...${NC}"
    
    cd "$MCP_DIR"
    if python3 "$server_file" --test >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $server_name tests passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $server_name tests failed${NC}"
        return 1
    fi
}

echo -e "\n${BLUE}=== Pre-flight Checks ===${NC}"

# Check Python availability
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python 3 available${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check GitHub token
if [[ -n "$GITHUB_TOKEN" ]]; then
    echo -e "${GREEN}✅ GitHub token configured${NC}"
else
    echo -e "${YELLOW}⚠️  GitHub token not set (some features limited)${NC}"
fi

echo -e "\n${BLUE}=== Running Server Tests ===${NC}"

# Test each server before starting
declare -A servers=(
    ["Simple GitHub"]="simple_github_mcp_server.py"
    ["Smart Debugging"]="smart_debugging_mcp_server.py"
)

working_servers=()

for server_name in "${!servers[@]}"; do
    server_file="${servers[$server_name]}"
    if test_server "$server_name" "$server_file"; then
        working_servers+=("$server_name")
    fi
done

if [[ ${#working_servers[@]} -eq 0 ]]; then
    echo -e "\n${RED}❌ No servers passed tests. Exiting.${NC}"
    exit 1
fi

echo -e "\n${BLUE}=== Starting Servers ===${NC}"

# Start working servers
for server_name in "${working_servers[@]}"; do
    case "$server_name" in
        "Simple GitHub")
            start_server "Simple GitHub" "simple_github_mcp_server.py" "8765" "GitHub repository management and operations"
            ;;
        "Smart Debugging")  
            start_server "Smart Debugging" "smart_debugging_mcp_server.py" "8768" "Intelligent bug analysis and debugging assistance"
            ;;
    esac
done

echo -e "\n${BLUE}=== Server Status Summary ===${NC}"

# Check which servers are running
running_count=0
for server_name in "${working_servers[@]}"; do
    pid_file="$LOGS_DIR/${server_name,,}_mcp.pid"
    if [[ -f "$pid_file" ]]; then
        pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo -e "${GREEN}✅ $server_name (PID: $pid)${NC}"
            ((running_count++))
        else
            echo -e "${RED}❌ $server_name (not running)${NC}"
        fi
    fi
done

echo -e "\n${GREEN}🎉 Started $running_count MCP servers successfully!${NC}"

echo -e "\n${BLUE}=== Available Services ===${NC}"
echo "• Simple GitHub MCP     - Repository operations, file browsing, issue management"
echo "• Smart Debugging MCP   - Error analysis, bug pattern recognition, fix suggestions"

echo -e "\n${BLUE}=== Management Commands ===${NC}"
echo "• Check status:  ps aux | grep mcp_server"
echo "• View logs:     tail -f $LOGS_DIR/*_mcp.log"
echo "• Stop all:      pkill -f mcp_server"
echo "• Stop specific: kill \$(cat $LOGS_DIR/server_name_mcp.pid)"

echo -e "\n${BLUE}=== VS Code Integration ===${NC}"
echo "Add to your .vscode/mcp.json:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"simple-github\": {"
echo "      \"command\": \"python3\","
echo "      \"args\": [\"$MCP_DIR/simple_github_mcp_server.py\"],"
echo "      \"env\": {\"GITHUB_TOKEN\": \"\${GITHUB_TOKEN}\"}"
echo "    },"
echo "    \"smart-debugging\": {"
echo "      \"command\": \"python3\","
echo "      \"args\": [\"$MCP_DIR/smart_debugging_mcp_server.py\"]"
echo "    }"
echo "  }"
echo "}"

echo -e "\n${GREEN}🚀 All MCP servers are ready for action!${NC}"