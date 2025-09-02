#!/bin/bash
# Setup script for GitHub MCP Servers on Termux/Android
# Author: SynthNet AI Team
# Version: 1.0.0

set -e

echo "🚀 Setting up GitHub MCP Servers for SynthNet AI..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/data/data/com.termux/files/home/synthnet"
MCP_DIR="$BASE_DIR/mcp_servers"
LOGS_DIR="$BASE_DIR/logs"
WORKSPACE_DIR="$BASE_DIR/workspace"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if we're running on Termux
check_termux() {
    if [[ ! -d "/data/data/com.termux" ]]; then
        print_error "This script is designed for Termux on Android"
        exit 1
    fi
    print_status "Termux environment detected"
}

# Create necessary directories
setup_directories() {
    print_header "Creating Directory Structure"
    
    directories=("$MCP_DIR" "$LOGS_DIR" "$WORKSPACE_DIR" "$BASE_DIR/repositories")
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
}

# Install Python dependencies
install_dependencies() {
    print_header "Installing Python Dependencies"
    
    # Update pip first
    print_status "Updating pip..."
    python3 -m pip install --upgrade pip
    
    # Install requirements
    if [[ -f "$MCP_DIR/requirements.txt" ]]; then
        print_status "Installing MCP server dependencies..."
        python3 -m pip install -r "$MCP_DIR/requirements.txt"
    else
        print_warning "requirements.txt not found, installing basic dependencies..."
        python3 -m pip install mcp aiohttp aiofiles pydantic PyYAML
    fi
    
    print_status "Dependencies installed successfully"
}

# Install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_status "Installing git..."
        pkg install git -y
    else
        print_status "Git already installed"
    fi
    
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        print_status "Installing curl..."
        pkg install curl -y
    else
        print_status "Curl already installed"
    fi
}

# Setup environment variables
setup_environment() {
    print_header "Environment Configuration"
    
    ENV_FILE="$BASE_DIR/.env"
    
    if [[ ! -f "$ENV_FILE" ]]; then
        print_status "Creating environment file..."
        cat > "$ENV_FILE" << 'EOF'
# GitHub MCP Server Environment Configuration
# Copy this file and update with your actual values

# GitHub API Token (required)
# Get from: https://github.com/settings/tokens
export GITHUB_TOKEN="your_github_token_here"

# GitHub Username (optional but recommended)
export GITHUB_USERNAME="your_github_username"

# Custom GitHub API URL (optional)
# export GITHUB_API_URL="https://api.github.com"

# Workspace directory (optional)
# export SYNTHNET_WORKSPACE="/data/data/com.termux/files/home/synthnet/workspace"

# Logging level (optional)
# export LOG_LEVEL="INFO"
EOF
        print_warning "Environment file created at $ENV_FILE"
        print_warning "Please edit this file and add your GitHub token"
    else
        print_status "Environment file already exists"
    fi
}

# Make scripts executable
make_executable() {
    print_header "Setting File Permissions"
    
    chmod +x "$MCP_DIR/github_copilot_mcp_server.py"
    chmod +x "$MCP_DIR/github_tools_mcp_server.py"
    chmod +x "$MCP_DIR/setup_mcp_servers.sh"
    
    print_status "Scripts made executable"
}

# Test MCP servers
test_servers() {
    print_header "Testing MCP Servers"
    
    # Test Python import
    print_status "Testing Python imports..."
    if python3 -c "import mcp; import aiohttp; import aiofiles" 2>/dev/null; then
        print_status "Core dependencies available"
    else
        print_error "Some dependencies are missing"
        return 1
    fi
    
    # Test server files exist and are valid Python
    servers=("github_copilot_mcp_server.py" "github_tools_mcp_server.py")
    
    for server in "${servers[@]}"; do
        server_path="$MCP_DIR/$server"
        if [[ -f "$server_path" ]]; then
            if python3 -m py_compile "$server_path" 2>/dev/null; then
                print_status "✓ $server syntax is valid"
            else
                print_error "✗ $server has syntax errors"
            fi
        else
            print_error "✗ $server not found"
        fi
    done
}

# Create VS Code configuration (if VS Code is available)
create_vscode_config() {
    print_header "VS Code Integration Setup"
    
    VSCODE_DIR="$BASE_DIR/.vscode"
    
    if [[ -d "$VSCODE_DIR" ]] || command -v code &> /dev/null; then
        mkdir -p "$VSCODE_DIR"
        
        # Create MCP configuration for VS Code
        cat > "$VSCODE_DIR/mcp.json" << EOF
{
  "mcpServers": {
    "github-copilot": {
      "command": "python3",
      "args": ["$MCP_DIR/github_copilot_mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "\${GITHUB_TOKEN}",
        "GITHUB_USERNAME": "\${GITHUB_USERNAME}"
      }
    },
    "github-tools": {
      "command": "python3",
      "args": ["$MCP_DIR/github_tools_mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "\${GITHUB_TOKEN}",
        "GITHUB_USERNAME": "\${GITHUB_USERNAME}",
        "SYNTHNET_WORKSPACE": "$WORKSPACE_DIR"
      }
    }
  }
}
EOF
        print_status "VS Code MCP configuration created"
    else
        print_status "VS Code not detected, skipping VS Code configuration"
    fi
}

# Create startup script
create_startup_script() {
    print_header "Creating Startup Scripts"
    
    # MCP server startup script
    cat > "$MCP_DIR/start_mcp_servers.sh" << 'EOF'
#!/bin/bash
# Start all GitHub MCP servers

BASE_DIR="/data/data/com.termux/files/home/synthnet"
MCP_DIR="$BASE_DIR/mcp_servers"

# Load environment variables
if [[ -f "$BASE_DIR/.env" ]]; then
    source "$BASE_DIR/.env"
fi

echo "Starting GitHub MCP Servers..."

# Start GitHub Copilot MCP Server
echo "Starting GitHub Copilot MCP Server..."
python3 "$MCP_DIR/github_copilot_mcp_server.py" &
COPILOT_PID=$!

# Start GitHub Tools MCP Server  
echo "Starting GitHub Tools MCP Server..."
python3 "$MCP_DIR/github_tools_mcp_server.py" &
TOOLS_PID=$!

echo "MCP Servers started:"
echo "- GitHub Copilot MCP Server (PID: $COPILOT_PID)"
echo "- GitHub Tools MCP Server (PID: $TOOLS_PID)"

# Wait for servers to start
sleep 2

# Keep script running
wait
EOF

    chmod +x "$MCP_DIR/start_mcp_servers.sh"
    
    # Stop script
    cat > "$MCP_DIR/stop_mcp_servers.sh" << 'EOF'
#!/bin/bash
# Stop all GitHub MCP servers

echo "Stopping GitHub MCP servers..."

# Kill Python MCP server processes
pkill -f "github_copilot_mcp_server.py"
pkill -f "github_tools_mcp_server.py"

echo "MCP servers stopped"
EOF

    chmod +x "$MCP_DIR/stop_mcp_servers.sh"
    
    print_status "Startup scripts created"
}

# Print usage instructions
print_usage() {
    print_header "Setup Complete! 🎉"
    
    echo ""
    echo -e "${GREEN}Next Steps:${NC}"
    echo "1. Edit the environment file:"
    echo -e "   ${BLUE}nano $BASE_DIR/.env${NC}"
    echo "   Add your GitHub token and username"
    echo ""
    echo "2. Load environment variables:"
    echo -e "   ${BLUE}source $BASE_DIR/.env${NC}"
    echo ""
    echo "3. Start MCP servers:"
    echo -e "   ${BLUE}$MCP_DIR/start_mcp_servers.sh${NC}"
    echo ""
    echo "4. Test the servers:"
    echo -e "   ${BLUE}curl http://localhost:8000/health${NC} (if implemented)"
    echo ""
    echo -e "${GREEN}Available Scripts:${NC}"
    echo -e "   ${BLUE}$MCP_DIR/start_mcp_servers.sh${NC}  - Start all MCP servers"
    echo -e "   ${BLUE}$MCP_DIR/stop_mcp_servers.sh${NC}   - Stop all MCP servers"
    echo ""
    echo -e "${GREEN}Log Files:${NC}"
    echo -e "   ${BLUE}$LOGS_DIR/github_mcp.log${NC}        - GitHub Copilot server logs"
    echo -e "   ${BLUE}$LOGS_DIR/github_tools_mcp.log${NC}  - GitHub Tools server logs"
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo "- Make sure to keep your GitHub token secure"
    echo "- The servers will run in the background"
    echo "- Check log files for any issues"
    echo ""
}

# Main setup function
main() {
    print_header "SynthNet GitHub MCP Servers Setup"
    
    check_termux
    setup_directories
    install_system_deps
    install_dependencies
    setup_environment
    make_executable
    test_servers
    create_vscode_config
    create_startup_script
    
    print_usage
}

# Run main function
main "$@"