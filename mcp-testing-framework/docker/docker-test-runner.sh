#!/bin/bash
# MCP Testing Framework Docker Test Runner
# Comprehensive script for running MCP server tests in Docker environment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
DEFAULT_SERVER_TYPE="generic"
DEFAULT_OUTPUT_DIR="/app/test_results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
MCP Testing Framework Docker Test Runner

Usage: $0 [OPTIONS] COMMAND [ARGS...]

Commands:
    setup           Setup the testing environment
    start           Start all testing services
    stop            Stop all testing services
    test            Run tests on MCP server
    clean           Clean up all containers and volumes
    logs            Show logs from services
    status          Show status of all services
    shell           Open shell in test runner container
    report          Generate and serve test reports

Test Options:
    --server-path PATH        Path to MCP server to test (required for test command)
    --server-type TYPE        Server type (healthcare, education, iot, generic) [default: generic]
    --test-types TYPES        Comma-separated test types (unit,integration,protocol,performance,security)
    --output-dir DIR          Output directory for test results [default: test_results]
    --parallel                Run tests in parallel
    --coverage                Generate coverage report
    --html-report             Generate HTML test report
    --junit-report            Generate JUnit XML report
    --performance-report      Generate performance report
    --security-scan           Run security vulnerability scan

Environment Options:
    --env-file FILE          Load environment variables from file
    --compose-file FILE      Use custom docker-compose file [default: docker-compose.yml]
    --project-name NAME      Docker Compose project name [default: mcp-testing]

Examples:
    # Setup and start testing environment
    $0 setup
    $0 start

    # Run comprehensive tests on healthcare server
    $0 test --server-path /path/to/healthcare-server.py \\
            --server-type healthcare \\
            --test-types unit,integration,protocol,performance,security \\
            --coverage \\
            --html-report

    # Run only protocol compliance tests
    $0 test --server-path /path/to/server.py --test-types protocol

    # Check service status
    $0 status

    # View logs from specific service
    $0 logs mcp-test-runner

    # Clean up everything
    $0 clean

EOF
}

# Parse command line arguments
parse_args() {
    COMMAND=""
    SERVER_PATH=""
    SERVER_TYPE="$DEFAULT_SERVER_TYPE"
    TEST_TYPES=""
    OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
    PARALLEL=false
    COVERAGE=false
    HTML_REPORT=false
    JUNIT_REPORT=false
    PERFORMANCE_REPORT=false
    SECURITY_SCAN=false
    ENV_FILE=""
    PROJECT_NAME="mcp-testing"
    COMPOSE_ARGS=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --server-path)
                SERVER_PATH="$2"
                shift 2
                ;;
            --server-type)
                SERVER_TYPE="$2"
                shift 2
                ;;
            --test-types)
                TEST_TYPES="$2"
                shift 2
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --parallel)
                PARALLEL=true
                shift
                ;;
            --coverage)
                COVERAGE=true
                shift
                ;;
            --html-report)
                HTML_REPORT=true
                shift
                ;;
            --junit-report)
                JUNIT_REPORT=true
                shift
                ;;
            --performance-report)
                PERFORMANCE_REPORT=true
                shift
                ;;
            --security-scan)
                SECURITY_SCAN=true
                shift
                ;;
            --env-file)
                ENV_FILE="$2"
                COMPOSE_ARGS="$COMPOSE_ARGS --env-file $ENV_FILE"
                shift 2
                ;;
            --compose-file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            --project-name)
                PROJECT_NAME="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$COMMAND" ]]; then
                    COMMAND="$1"
                else
                    log_error "Multiple commands specified: $COMMAND and $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    COMPOSE_ARGS="$COMPOSE_ARGS --project-name $PROJECT_NAME -f $COMPOSE_FILE"
}

# Docker Compose wrapper
docker_compose() {
    docker-compose $COMPOSE_ARGS "$@"
}

# Check if Docker and Docker Compose are available
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
}

# Setup testing environment
setup_environment() {
    log_info "Setting up MCP testing environment..."

    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/test_results"
    mkdir -p "$PROJECT_ROOT/test_data"
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/docker/mock-data"

    # Create requirements files if they don't exist
    if [[ ! -f "$PROJECT_ROOT/requirements.txt" ]]; then
        log_info "Creating requirements.txt..."
        cat > "$PROJECT_ROOT/requirements.txt" << 'EOF'
mcp>=1.0.0
httpx>=0.25.0
asyncio-mqtt>=0.13.0
pydantic>=2.0.0
jsonschema>=4.0.0
PyYAML>=6.0.0
jinja2>=3.1.0
aiofiles>=23.0.0
psutil>=5.9.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
sqlite3
EOF
    fi

    if [[ ! -f "$PROJECT_ROOT/requirements-test.txt" ]]; then
        log_info "Creating requirements-test.txt..."
        cat > "$PROJECT_ROOT/requirements-test.txt" << 'EOF'
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-html>=3.0.0
pytest-json-report>=1.5.0
pytest-xdist>=3.0.0
coverage>=7.0.0
bandit>=1.7.0
safety>=2.3.0
flake8>=6.0.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
pre-commit>=3.0.0
requests>=2.31.0
responses>=0.23.0
freezegun>=1.2.0
EOF
    fi

    # Create nginx config for report server
    if [[ ! -f "$SCRIPT_DIR/nginx.conf" ]]; then
        log_info "Creating nginx configuration..."
        cat > "$SCRIPT_DIR/nginx.conf" << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }

    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    fi

    # Create Prometheus config
    if [[ ! -f "$SCRIPT_DIR/prometheus.yml" ]]; then
        log_info "Creating Prometheus configuration..."
        cat > "$SCRIPT_DIR/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'mcp-servers'
    static_configs:
      - targets: ['mcp-test-runner:8000']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
    fi

    # Create PostgreSQL initialization script
    if [[ ! -f "$SCRIPT_DIR/init-postgres.sql" ]]; then
        log_info "Creating PostgreSQL initialization script..."
        cat > "$SCRIPT_DIR/init-postgres.sql" << 'EOF'
-- MCP Testing Framework Database Schema

-- Test results table
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    duration FLOAT NOT NULL,
    message TEXT,
    error_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Test sessions table
CREATE TABLE IF NOT EXISTS test_sessions (
    id SERIAL PRIMARY KEY,
    session_name VARCHAR(255) NOT NULL,
    server_type VARCHAR(50) NOT NULL,
    server_path VARCHAR(500) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_tests INTEGER DEFAULT 0,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    test_session_id INTEGER REFERENCES test_sessions(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Security scan results table
CREATE TABLE IF NOT EXISTS security_scan_results (
    id SERIAL PRIMARY KEY,
    test_session_id INTEGER REFERENCES test_sessions(id),
    vulnerability_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    line_number INTEGER,
    description TEXT,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_test_results_status ON test_results(status);
CREATE INDEX IF NOT EXISTS idx_test_results_type ON test_results(test_type);
CREATE INDEX IF NOT EXISTS idx_test_results_created ON test_results(created_at);
CREATE INDEX IF NOT EXISTS idx_test_sessions_created ON test_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_session ON performance_metrics(test_session_id);
CREATE INDEX IF NOT EXISTS idx_security_scan_session ON security_scan_results(test_session_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mcp_test;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mcp_test;
EOF
    fi

    log_success "Environment setup completed"
}

# Start all services
start_services() {
    log_info "Starting MCP testing services..."
    
    docker_compose up -d
    
    log_info "Waiting for services to be ready..."
    
    # Wait for critical services
    local services=("redis" "postgres" "mock-fhir-server")
    for service in "${services[@]}"; do
        log_info "Waiting for $service to be healthy..."
        local timeout=60
        local count=0
        
        while ! docker_compose ps "$service" | grep -q "healthy\|Up"; do
            if [[ $count -ge $timeout ]]; then
                log_error "$service failed to start within $timeout seconds"
                docker_compose logs "$service"
                exit 1
            fi
            sleep 1
            ((count++))
        done
        log_success "$service is ready"
    done
    
    log_success "All services are running"
    log_info "Test reports available at: http://localhost:8090"
    log_info "Grafana dashboard available at: http://localhost:3000 (admin/admin)"
    log_info "Kibana available at: http://localhost:5601"
}

# Stop all services
stop_services() {
    log_info "Stopping MCP testing services..."
    docker_compose down
    log_success "Services stopped"
}

# Run tests
run_tests() {
    if [[ -z "$SERVER_PATH" ]]; then
        log_error "Server path is required for testing. Use --server-path option."
        exit 1
    fi
    
    if [[ ! -f "$SERVER_PATH" && ! -d "$SERVER_PATH" ]]; then
        log_error "Server path does not exist: $SERVER_PATH"
        exit 1
    fi
    
    log_info "Running tests for MCP server: $SERVER_PATH"
    log_info "Server type: $SERVER_TYPE"
    
    # Ensure services are running
    if ! docker_compose ps | grep -q "Up"; then
        log_info "Starting testing services..."
        start_services
    fi
    
    # Build test command
    local test_cmd="python -m mcp_testing_framework.core.test_runner"
    test_cmd="$test_cmd $SERVER_PATH"
    test_cmd="$test_cmd --server-type $SERVER_TYPE"
    test_cmd="$test_cmd --output-dir $OUTPUT_DIR"
    test_cmd="$test_cmd --environment docker"
    
    if [[ -n "$TEST_TYPES" ]]; then
        test_cmd="$test_cmd --test-types ${TEST_TYPES//,/ }"
    fi
    
    if [[ "$PARALLEL" == "true" ]]; then
        test_cmd="$test_cmd --parallel"
    fi
    
    # Build report formats
    local report_formats=()
    if [[ "$HTML_REPORT" == "true" ]]; then
        report_formats+=("html")
    fi
    if [[ "$JUNIT_REPORT" == "true" ]]; then
        report_formats+=("junit")
    fi
    if [[ "$PERFORMANCE_REPORT" == "true" ]]; then
        report_formats+=("performance")
    fi
    
    if [[ ${#report_formats[@]} -gt 0 ]]; then
        test_cmd="$test_cmd --report-formats ${report_formats[*]}"
    fi
    
    # Copy server to container
    local server_basename=$(basename "$SERVER_PATH")
    docker cp "$SERVER_PATH" mcp-test-runner:/app/test_server/
    
    # Run the test command
    log_info "Executing: $test_cmd"
    docker_compose exec -T mcp-test-runner bash -c "$test_cmd"
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Tests completed successfully"
    else
        log_error "Tests failed with exit code $exit_code"
    fi
    
    # Run additional scans if requested
    if [[ "$SECURITY_SCAN" == "true" ]]; then
        log_info "Running security vulnerability scan..."
        docker_compose exec -T mcp-test-runner bash -c \
            "python -m mcp_testing_framework.core.security_scanner /app/test_server/$server_basename --output $OUTPUT_DIR/security_scan.json"
    fi
    
    if [[ "$COVERAGE" == "true" ]]; then
        log_info "Generating coverage report..."
        docker_compose exec -T mcp-test-runner bash -c \
            "coverage html -d $OUTPUT_DIR/coverage_html && coverage xml -o $OUTPUT_DIR/coverage.xml"
    fi
    
    # Copy results from container
    log_info "Copying test results..."
    docker cp mcp-test-runner:$OUTPUT_DIR "$PROJECT_ROOT/"
    
    log_success "Test results available in: $PROJECT_ROOT/test_results"
    
    return $exit_code
}

# Clean up environment
clean_environment() {
    log_info "Cleaning up MCP testing environment..."
    
    docker_compose down --volumes --remove-orphans
    docker system prune -f
    
    # Remove generated files (optional)
    read -p "Remove test results and data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_ROOT/test_results"
        rm -rf "$PROJECT_ROOT/test_data"
        rm -rf "$PROJECT_ROOT/logs"
        log_success "Test data cleaned up"
    fi
    
    log_success "Environment cleaned up"
}

# Show service logs
show_logs() {
    local service="${1:-}"
    if [[ -n "$service" ]]; then
        docker_compose logs -f "$service"
    else
        docker_compose logs -f
    fi
}

# Show service status
show_status() {
    log_info "MCP Testing Environment Status:"
    docker_compose ps
    
    echo
    log_info "Service Health Checks:"
    
    # Check each service
    local services=("redis" "postgres" "mock-fhir-server" "elasticsearch")
    for service in "${services[@]}"; do
        if docker_compose ps "$service" | grep -q "Up"; then
            if docker_compose ps "$service" | grep -q "healthy"; then
                echo -e "  $service: ${GREEN}Healthy${NC}"
            else
                echo -e "  $service: ${YELLOW}Running (no health check)${NC}"
            fi
        else
            echo -e "  $service: ${RED}Down${NC}"
        fi
    done
}

# Open shell in test runner
open_shell() {
    log_info "Opening shell in test runner container..."
    docker_compose exec mcp-test-runner bash
}

# Generate and serve reports
serve_reports() {
    log_info "Starting report server..."
    
    # Ensure report server is running
    if ! docker_compose ps report-server | grep -q "Up"; then
        docker_compose up -d report-server
    fi
    
    log_success "Report server is running at: http://localhost:8090"
    
    # Generate index page if it doesn't exist
    docker_compose exec -T report-server sh -c '
        if [ ! -f /usr/share/nginx/html/index.html ]; then
            cat > /usr/share/nginx/html/index.html << '\''EOF'\''
<!DOCTYPE html>
<html>
<head>
    <title>MCP Test Reports</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .service { margin: 20px 0; }
        .service a { color: #0066cc; text-decoration: none; }
        .service a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>MCP Testing Framework - Reports Dashboard</h1>
    <div class="service">
        <h3><a href="/test_results/">Test Results</a></h3>
        <p>Browse test execution results and reports</p>
    </div>
    <div class="service">
        <h3><a href="http://localhost:3000" target="_blank">Grafana</a></h3>
        <p>Performance metrics and monitoring dashboards</p>
    </div>
    <div class="service">
        <h3><a href="http://localhost:5601" target="_blank">Kibana</a></h3>
        <p>Log analysis and visualization</p>
    </div>
    <div class="service">
        <h3><a href="http://localhost:16686" target="_blank">Jaeger</a></h3>
        <p>Distributed tracing and request analysis</p>
    </div>
</body>
</html>
EOF
        fi
    '
}

# Main execution
main() {
    parse_args "$@"
    
    if [[ -z "$COMMAND" ]]; then
        log_error "No command specified"
        show_help
        exit 1
    fi
    
    check_dependencies
    
    case "$COMMAND" in
        setup)
            setup_environment
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        test)
            run_tests
            ;;
        clean)
            clean_environment
            ;;
        logs)
            shift  # Remove 'logs' from arguments
            show_logs "$@"
            ;;
        status)
            show_status
            ;;
        shell)
            open_shell
            ;;
        report)
            serve_reports
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"