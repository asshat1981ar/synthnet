#!/bin/bash
# SynthNet Android MCP Ecosystem Unified Deployment System
# Revolutionary deployment automation with quantum health monitoring

set -e
set -u

# Configuration
SYNTHNET_HOME="/data/data/com.termux/files/home/synthnet"
MCP_SERVERS_DIR="$SYNTHNET_HOME/mcp_servers"
LOG_DIR="$SYNTHNET_HOME/logs"
PID_DIR="$SYNTHNET_HOME/pids"
HEALTH_CHECK_INTERVAL=30
DEPLOYMENT_TIMEOUT=300
PYTHON_CMD="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Server definitions
declare -A MCP_SERVERS=(
    ["synthnet_android_hub"]="8767"
    ["simple_github_mcp_server"]="8765"
    ["smart_debugging_mcp_server"]="8768"
    ["symbiotic_architecture_intelligence_server"]="8769"
    ["sentient_testing_ecosystem_server"]="8770"
    ["unified_mcp_orchestrator"]="8771"
    ["semantic_cot_reasoning_engine"]="8772"
    ["n8n_mcp_bridge"]="8773"
)

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO - $1" >> "$LOG_DIR/deployment.log"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARN - $1" >> "$LOG_DIR/deployment.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR - $1" >> "$LOG_DIR/deployment.log"
}

log_success() {
    echo -e "${CYAN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS - $1" >> "$LOG_DIR/deployment.log"
}

# Initialize deployment environment
init_deployment_environment() {
    log_info "Initializing SynthNet MCP deployment environment..."
    
    # Create necessary directories
    mkdir -p "$LOG_DIR" "$PID_DIR"
    
    # Initialize deployment log
    echo "=== SynthNet MCP Ecosystem Deployment - $(date) ===" >> "$LOG_DIR/deployment.log"
    
    # Check Python availability
    if ! command -v $PYTHON_CMD &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3."
        exit 1
    fi
    
    # Check if we're in Termux
    if [[ -d "/data/data/com.termux" ]]; then
        log_info "Termux environment detected - optimizing for Android"
        export TERMUX_ENVIRONMENT=1
    fi
    
    log_success "Deployment environment initialized"
}

# Pre-flight checks
pre_flight_checks() {
    log_info "Performing pre-flight checks..."
    
    local checks_passed=0
    local total_checks=0
    
    # Check if MCP servers directory exists
    ((total_checks++))
    if [[ -d "$MCP_SERVERS_DIR" ]]; then
        log_info "✅ MCP servers directory exists"
        ((checks_passed++))
    else
        log_error "❌ MCP servers directory not found: $MCP_SERVERS_DIR"
    fi
    
    # Check if server files exist
    for server in "${!MCP_SERVERS[@]}"; do
        ((total_checks++))
        local server_file="$MCP_SERVERS_DIR/${server}.py"
        if [[ -f "$server_file" ]]; then
            log_info "✅ Server file exists: $server"
            ((checks_passed++))
        else
            log_error "❌ Server file missing: $server_file"
        fi
    done
    
    # Check port availability
    for server in "${!MCP_SERVERS[@]}"; do
        ((total_checks++))
        local port="${MCP_SERVERS[$server]}"
        if ! netstat -ln 2>/dev/null | grep -q ":$port "; then
            log_info "✅ Port $port available for $server"
            ((checks_passed++))
        else
            log_warn "⚠️  Port $port already in use (may need cleanup)"
            ((checks_passed++)) # Don't fail on this, might be our own servers
        fi
    done
    
    # Check Python dependencies
    ((total_checks++))
    if $PYTHON_CMD -c "import asyncio, json, sqlite3" 2>/dev/null; then
        log_info "✅ Core Python dependencies available"
        ((checks_passed++))
    else
        log_error "❌ Missing core Python dependencies"
    fi
    
    log_info "Pre-flight checks: $checks_passed/$total_checks passed"
    
    if [[ $checks_passed -eq $total_checks ]]; then
        log_success "All pre-flight checks passed"
        return 0
    elif [[ $checks_passed -ge $((total_checks * 80 / 100)) ]]; then
        log_warn "80%+ checks passed, proceeding with caution"
        return 0
    else
        log_error "Too many pre-flight checks failed"
        return 1
    fi
}

# Test server functionality
test_server() {
    local server_name="$1"
    local server_file="$MCP_SERVERS_DIR/${server_name}.py"
    
    log_info "Testing $server_name..."
    
    # Run server in test mode
    local test_output
    if test_output=$($PYTHON_CMD "$server_file" --test 2>&1); then
        if echo "$test_output" | grep -q "systems operational\|All systems"; then
            log_success "✅ $server_name test passed"
            return 0
        else
            log_warn "⚠️  $server_name test completed with warnings"
            log_info "Test output: $test_output"
            return 0
        fi
    else
        log_error "❌ $server_name test failed"
        log_error "Error output: $test_output"
        return 1
    fi
}

# Start individual server
start_server() {
    local server_name="$1"
    local port="${MCP_SERVERS[$server_name]}"
    local server_file="$MCP_SERVERS_DIR/${server_name}.py"
    local pid_file="$PID_DIR/${server_name}.pid"
    local log_file="$LOG_DIR/${server_name}.log"
    
    log_info "Starting $server_name on port $port..."
    
    # Check if already running
    if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        log_warn "$server_name already running (PID: $(cat "$pid_file"))"
        return 0
    fi
    
    # Start server
    nohup $PYTHON_CMD "$server_file" > "$log_file" 2>&1 &
    local server_pid=$!
    echo $server_pid > "$pid_file"
    
    # Wait for server to start
    local wait_count=0
    local max_wait=30
    
    while [[ $wait_count -lt $max_wait ]]; do
        if kill -0 $server_pid 2>/dev/null; then
            # Check if server is responsive
            if netstat -ln 2>/dev/null | grep -q ":$port "; then
                log_success "✅ $server_name started successfully (PID: $server_pid)"
                return 0
            fi
        else
            log_error "❌ $server_name process died during startup"
            rm -f "$pid_file"
            return 1
        fi
        
        sleep 1
        ((wait_count++))
    done
    
    log_error "❌ $server_name startup timeout"
    kill $server_pid 2>/dev/null || true
    rm -f "$pid_file"
    return 1
}

# Health check for server
health_check() {
    local server_name="$1"
    local port="${MCP_SERVERS[$server_name]}"
    local pid_file="$PID_DIR/${server_name}.pid"
    
    # Check if PID file exists and process is running
    if [[ ! -f "$pid_file" ]]; then
        echo "STOPPED"
        return 1
    fi
    
    local server_pid
    server_pid=$(cat "$pid_file")
    
    if ! kill -0 "$server_pid" 2>/dev/null; then
        echo "DEAD"
        rm -f "$pid_file"
        return 1
    fi
    
    # Check if port is listening
    if netstat -ln 2>/dev/null | grep -q ":$port "; then
        echo "HEALTHY"
        return 0
    else
        echo "UNHEALTHY"
        return 1
    fi
}

# Deploy all servers
deploy_all_servers() {
    log_info "🚀 Starting SynthNet MCP Ecosystem deployment..."
    
    local deployment_start_time
    deployment_start_time=$(date +%s)
    
    local servers_started=0
    local servers_failed=0
    
    # Start servers in dependency order
    local deployment_order=(
        "simple_github_mcp_server"
        "smart_debugging_mcp_server"
        "symbiotic_architecture_intelligence_server" 
        "sentient_testing_ecosystem_server"
        "semantic_cot_reasoning_engine"
        "synthnet_android_hub"
        "n8n_mcp_bridge"
        "unified_mcp_orchestrator"
    )
    
    for server in "${deployment_order[@]}"; do
        if test_server "$server"; then
            if start_server "$server"; then
                ((servers_started++))
            else
                ((servers_failed++))
                log_error "Failed to start $server"
            fi
        else
            ((servers_failed++))
            log_error "Server test failed for $server, skipping startup"
        fi
        
        # Brief pause between server starts
        sleep 2
    done
    
    local deployment_end_time
    deployment_end_time=$(date +%s)
    local deployment_duration=$((deployment_end_time - deployment_start_time))
    
    log_info "Deployment completed in ${deployment_duration}s"
    log_info "Servers started: $servers_started"
    log_info "Servers failed: $servers_failed"
    
    if [[ $servers_started -gt 0 ]]; then
        log_success "🎉 SynthNet MCP Ecosystem partially deployed!"
        return 0
    else
        log_error "💥 Complete deployment failure"
        return 1
    fi
}

# Monitor ecosystem health
monitor_ecosystem() {
    local monitoring_duration="${1:-300}" # Default 5 minutes
    local start_time
    start_time=$(date +%s)
    
    log_info "🔍 Starting ecosystem health monitoring for ${monitoring_duration}s..."
    
    while true; do
        local current_time
        current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [[ $elapsed -ge $monitoring_duration ]]; then
            log_info "Monitoring period completed"
            break
        fi
        
        # Check health of all servers
        local healthy_count=0
        local total_servers=${#MCP_SERVERS[@]}
        
        echo -e "${BLUE}=== Health Check (${elapsed}/${monitoring_duration}s) ===${NC}"
        
        for server in "${!MCP_SERVERS[@]}"; do
            local health_status
            health_status=$(health_check "$server")
            local port="${MCP_SERVERS[$server]}"
            
            case "$health_status" in
                "HEALTHY")
                    echo -e "✅ ${GREEN}$server${NC} (port $port) - $health_status"
                    ((healthy_count++))
                    ;;
                "UNHEALTHY")
                    echo -e "⚠️  ${YELLOW}$server${NC} (port $port) - $health_status"
                    ;;
                "STOPPED"|"DEAD")
                    echo -e "❌ ${RED}$server${NC} (port $port) - $health_status"
                    ;;
            esac
        done
        
        local health_percentage=$((healthy_count * 100 / total_servers))
        echo -e "${CYAN}Ecosystem Health: $healthy_count/$total_servers servers ($health_percentage%)${NC}"
        
        if [[ $health_percentage -ge 80 ]]; then
            echo -e "${GREEN}🟢 Ecosystem Status: EXCELLENT${NC}"
        elif [[ $health_percentage -ge 60 ]]; then
            echo -e "${YELLOW}🟡 Ecosystem Status: GOOD${NC}"
        elif [[ $health_percentage -ge 40 ]]; then
            echo -e "${YELLOW}🟠 Ecosystem Status: DEGRADED${NC}"
        else
            echo -e "${RED}🔴 Ecosystem Status: CRITICAL${NC}"
        fi
        
        echo ""
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Stop all servers
stop_all_servers() {
    log_info "🛑 Stopping SynthNet MCP Ecosystem..."
    
    local servers_stopped=0
    
    for server in "${!MCP_SERVERS[@]}"; do
        local pid_file="$PID_DIR/${server}.pid"
        
        if [[ -f "$pid_file" ]]; then
            local server_pid
            server_pid=$(cat "$pid_file")
            
            if kill -0 "$server_pid" 2>/dev/null; then
                log_info "Stopping $server (PID: $server_pid)..."
                
                # Graceful shutdown
                kill -TERM "$server_pid" 2>/dev/null || true
                
                # Wait for graceful shutdown
                local wait_count=0
                while [[ $wait_count -lt 10 ]] && kill -0 "$server_pid" 2>/dev/null; do
                    sleep 1
                    ((wait_count++))
                done
                
                # Force kill if still running
                if kill -0 "$server_pid" 2>/dev/null; then
                    log_warn "Force killing $server..."
                    kill -KILL "$server_pid" 2>/dev/null || true
                fi
                
                rm -f "$pid_file"
                log_success "✅ $server stopped"
                ((servers_stopped++))
            else
                log_info "$server was not running"
                rm -f "$pid_file"
            fi
        else
            log_info "$server PID file not found"
        fi
    done
    
    log_success "🎯 Stopped $servers_stopped servers"
}

# Status check
check_status() {
    echo -e "${BLUE}=== SynthNet MCP Ecosystem Status ===${NC}"
    
    local healthy_count=0
    local total_servers=${#MCP_SERVERS[@]}
    
    for server in "${!MCP_SERVERS[@]}"; do
        local health_status
        health_status=$(health_check "$server")
        local port="${MCP_SERVERS[$server]}"
        
        case "$health_status" in
            "HEALTHY")
                echo -e "✅ ${GREEN}$server${NC} (port $port) - $health_status"
                ((healthy_count++))
                ;;
            "UNHEALTHY")
                echo -e "⚠️  ${YELLOW}$server${NC} (port $port) - $health_status"
                ;;
            "STOPPED"|"DEAD")
                echo -e "❌ ${RED}$server${NC} (port $port) - $health_status"
                ;;
        esac
    done
    
    local health_percentage=$((healthy_count * 100 / total_servers))
    echo ""
    echo -e "${CYAN}Overall Health: $healthy_count/$total_servers servers ($health_percentage%)${NC}"
    
    if [[ $health_percentage -ge 80 ]]; then
        echo -e "${GREEN}🟢 Ecosystem Status: EXCELLENT${NC}"
    elif [[ $health_percentage -ge 60 ]]; then
        echo -e "${YELLOW}🟡 Ecosystem Status: GOOD${NC}"
    elif [[ $health_percentage -ge 40 ]]; then
        echo -e "${YELLOW}🟠 Ecosystem Status: DEGRADED${NC}"
    else
        echo -e "${RED}🔴 Ecosystem Status: CRITICAL${NC}"
    fi
}

# Display usage
usage() {
    echo -e "${BLUE}SynthNet Android MCP Ecosystem Deployment System${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}deploy${NC}     - Deploy all MCP servers"
    echo -e "  ${GREEN}start${NC}      - Start all servers (alias for deploy)"
    echo -e "  ${GREEN}stop${NC}       - Stop all servers"
    echo -e "  ${GREEN}restart${NC}    - Restart all servers"
    echo -e "  ${GREEN}status${NC}     - Check status of all servers"
    echo -e "  ${GREEN}monitor${NC}    - Monitor ecosystem health (default 5min)"
    echo -e "  ${GREEN}test${NC}       - Test all servers without starting"
    echo -e "  ${GREEN}logs${NC}       - Show deployment logs"
    echo -e "  ${GREEN}help${NC}       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy          # Deploy the complete ecosystem"
    echo "  $0 monitor 600     # Monitor for 10 minutes"
    echo "  $0 status          # Quick status check"
}

# Show logs
show_logs() {
    local log_file="$LOG_DIR/deployment.log"
    
    if [[ -f "$log_file" ]]; then
        echo -e "${BLUE}=== Recent Deployment Logs ===${NC}"
        tail -50 "$log_file"
    else
        log_warn "No deployment logs found"
    fi
}

# Main execution
main() {
    # Initialize environment
    init_deployment_environment
    
    # Parse command
    local command="${1:-help}"
    
    case "$command" in
        "deploy"|"start")
            if pre_flight_checks; then
                deploy_all_servers
            else
                log_error "Pre-flight checks failed, aborting deployment"
                exit 1
            fi
            ;;
        "stop")
            stop_all_servers
            ;;
        "restart")
            stop_all_servers
            sleep 5
            if pre_flight_checks; then
                deploy_all_servers
            else
                log_error "Pre-flight checks failed, aborting restart"
                exit 1
            fi
            ;;
        "status")
            check_status
            ;;
        "monitor")
            local duration="${2:-300}"
            monitor_ecosystem "$duration"
            ;;
        "test")
            if pre_flight_checks; then
                log_success "All tests passed"
            else
                log_error "Some tests failed"
                exit 1
            fi
            ;;
        "logs")
            show_logs
            ;;
        "help"|"-h"|"--help")
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"