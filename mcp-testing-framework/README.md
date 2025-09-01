# MCP Testing Framework

A comprehensive testing framework for Model Context Protocol (MCP) servers that ensures reliability, security, and performance across all deployment environments.

![MCP Testing Framework](https://img.shields.io/badge/MCP-Testing%20Framework-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-green)

## 🚀 Features

### Multi-Layer Testing Strategy
- **Unit Tests** - Individual function and method testing
- **Integration Tests** - MCP protocol compliance and server interaction
- **End-to-End Tests** - Full workflow testing with real MCP clients
- **Performance Tests** - Load testing, stress testing, benchmarking
- **Security Tests** - Vulnerability scanning, penetration testing
- **Deployment Tests** - Testing across different deployment environments

### MCP Protocol Compliance
- **Protocol Validation** - Message format, schema compliance
- **Tool Testing** - Tool execution, parameter validation, response format
- **Resource Testing** - Resource access, MIME types, content validation
- **Prompt Testing** - Prompt template rendering, variable substitution
- **Error Handling** - Proper error responses, fault tolerance

### Automated Testing Pipeline
- **Test Discovery** - Automatic test detection and execution
- **Parallel Execution** - Concurrent test running for speed
- **Test Reporting** - Comprehensive reports with metrics and visualizations
- **CI/CD Integration** - Seamless integration with deployment pipelines
- **Test Data Management** - Mock data, fixtures, test databases

### Performance and Load Testing
- **Benchmarking** - Response time, throughput, resource usage metrics
- **Load Testing** - Simulate realistic usage patterns
- **Stress Testing** - Test server limits and failure modes
- **Scalability Testing** - Test auto-scaling and performance under load
- **Resource Monitoring** - Memory, CPU, network usage during tests

### Security Testing Framework
- **Vulnerability Scanning** - Automated security vulnerability detection
- **Authentication Testing** - Test auth mechanisms and access controls
- **Input Validation** - Test for injection attacks, malformed input handling
- **Network Security** - Test TLS, certificate validation, secure communication
- **Compliance Testing** - HIPAA, GDPR, industry-specific requirements

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ (for TypeScript server testing)
- Docker and Docker Compose (for containerized testing)
- Git

### Quick Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-testing-framework

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-test.txt

# Install the framework
pip install -e .
```

### Docker Installation

```bash
# Setup and start the complete testing environment
./docker/docker-test-runner.sh setup
./docker/docker-test-runner.sh start
```

## 🏃 Quick Start

### Basic Testing

```python
from mcp_testing_framework.core.test_runner import MCPTestRunner, TestConfiguration

# Create test configuration
config = TestConfiguration(
    server_path="path/to/your/mcp_server.py",
    server_type="healthcare",
    test_types=["unit", "integration", "protocol"],
    output_dir="test_results"
)

# Run tests
runner = MCPTestRunner(config)
session = await runner.run_all_tests()

print(f"Tests completed: {session.success_rate:.1f}% success rate")
```

### Command Line Usage

```bash
# Run comprehensive test suite
python -m mcp_testing_framework.core.test_runner /path/to/server \
    --server-type healthcare \
    --test-types unit integration protocol performance security \
    --output-dir test_results \
    --report-formats html junit json

# Run only protocol compliance tests
python -m mcp_testing_framework.core.mcp_protocol_tester /path/to/server

# Run performance tests
python -m mcp_testing_framework.core.performance_tester /path/to/server \
    --test-type load \
    --concurrent-users 50 \
    --duration 300

# Run security scan
python -m mcp_testing_framework.core.security_scanner /path/to/server \
    --output security_report.json
```

### Docker Testing

```bash
# Run tests in Docker environment
./docker/docker-test-runner.sh test \
    --server-path /path/to/server.py \
    --server-type healthcare \
    --test-types unit,integration,protocol,performance,security \
    --coverage \
    --html-report \
    --security-scan

# Check testing environment status
./docker/docker-test-runner.sh status

# View test reports
./docker/docker-test-runner.sh report
```

## 📁 Project Structure

```
mcp-testing-framework/
├── core/                   # Core testing components
│   ├── test_runner.py      # Main test execution engine
│   ├── mcp_protocol_tester.py  # MCP protocol compliance
│   ├── performance_tester.py   # Load and performance testing
│   └── security_scanner.py     # Security vulnerability testing
├── fixtures/               # Test fixtures and data
│   ├── mock_servers/       # Mock MCP servers for testing
│   ├── test_data/         # Sample data for various scenarios
│   └── client_mocks/      # Mock MCP clients
├── reporters/              # Test reporting
│   ├── html_reporter.py   # HTML test reports
│   ├── junit_reporter.py  # JUnit XML for CI/CD
│   ├── performance_reporter.py  # Performance metrics reports
│   └── security_reporter.py     # Security scan reports
├── integrations/           # CI/CD integrations
│   ├── github_actions.py  # GitHub Actions integration
│   └── docker_runner.py   # Container-based testing
├── examples/               # Example test implementations
│   ├── healthcare_tests/   # Healthcare FHIR server tests
│   ├── education_tests/    # Education LMS server tests
│   └── iot_tests/         # IoT device server tests
├── docker/                 # Docker environment
│   ├── Dockerfile.test-runner
│   ├── docker-compose.yml
│   └── docker-test-runner.sh
└── docs/                   # Documentation
    ├── user_guide.md
    ├── api_reference.md
    └── examples/
```

## 🔧 Configuration

### Test Configuration

```python
from mcp_testing_framework.core.test_runner import TestConfiguration

config = TestConfiguration(
    server_path="/path/to/server",
    server_type="healthcare",  # healthcare, education, iot, generic
    test_types=[
        "unit",         # Unit tests
        "integration",  # Integration tests
        "protocol",     # MCP protocol compliance
        "performance",  # Performance and load tests
        "security"      # Security vulnerability tests
    ],
    parallel_execution=True,
    max_workers=4,
    timeout=300,
    output_dir="test_results",
    report_formats=["html", "junit", "json"],
    coverage_enabled=True,
    mock_external_services=True,
    environment="test"
)
```

### GitHub Actions Integration

```yaml
# .github/workflows/mcp-testing.yml
name: MCP Server Testing
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install MCP Testing Framework
        run: |
          pip install -r requirements.txt
          pip install mcp-testing-framework
      
      - name: Run MCP Tests
        run: |
          mcp-test server.py \
            --server-type healthcare \
            --test-types unit integration protocol performance security \
            --output-dir test_results \
            --report-formats html junit json
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test_results/
```

## 🏥 Server-Specific Testing

### Healthcare FHIR Server Testing

```python
from mcp_testing_framework.examples.healthcare_tests import HealthcareFHIRTestSuite

# Create healthcare-specific test suite
test_suite = HealthcareFHIRTestSuite()

# Run FHIR compliance tests
fhir_results = await test_suite.test_fhir_compliance()

# Run HIPAA compliance tests
hipaa_results = await test_suite.test_hipaa_compliance()

# Run PHI protection tests
phi_results = await test_suite.test_phi_protection()
```

### Performance Testing

```python
from mcp_testing_framework.core.performance_tester import PerformanceTester, LoadTestConfig

tester = PerformanceTester()

# Basic performance test
basic_results = await tester.run_basic_performance_test()

# Load test with multiple concurrent users
load_config = LoadTestConfig(
    concurrent_users=50,
    requests_per_user=100,
    ramp_up_duration=30,
    test_duration=300
)
load_results = await tester.run_load_test(load_config)

# Stress test to find breaking point
stress_results = await tester.run_stress_test()
```

### Security Testing

```python
from mcp_testing_framework.core.security_scanner import SecurityScanner

scanner = SecurityScanner()

# Run comprehensive security scan
security_results = await scanner.scan_server("path/to/server")

# Static code analysis
static_results = await scanner.run_static_analysis("path/to/server")

# Dependency vulnerability scan
dependency_results = await scanner.scan_dependencies("path/to/server")

# Runtime security testing
runtime_results = await scanner.run_runtime_security_tests("path/to/server")
```

## 📊 Test Reporting

### HTML Reports
Rich, interactive HTML reports with:
- Executive summary with key metrics
- Performance charts and graphs
- Security vulnerability details
- Detailed test results with error traces
- Coverage reports with visual indicators

### JUnit XML Reports
Standard JUnit XML format for CI/CD integration:
- Compatible with Jenkins, GitHub Actions, etc.
- Test suite organization
- Detailed failure information
- Performance metrics

### Performance Reports
Specialized performance analysis:
- Response time distributions
- Throughput over time
- Resource usage charts
- Load test comparisons
- Bottleneck identification

### Security Reports
Comprehensive security analysis:
- Vulnerability severity levels
- Code quality metrics
- Compliance validation results
- Remediation recommendations

## 🔒 Security Testing

### Vulnerability Categories
- **SQL Injection** - Database query vulnerabilities
- **Command Injection** - OS command execution vulnerabilities
- **Path Traversal** - File system access vulnerabilities
- **Cross-Site Scripting (XSS)** - Web application vulnerabilities
- **Authentication Bypass** - Access control vulnerabilities
- **Cryptographic Issues** - Weak encryption and hashing
- **Input Validation** - Data sanitization issues
- **Configuration Security** - Insecure configurations

### Compliance Testing
- **HIPAA** - Healthcare data protection compliance
- **GDPR** - European data protection regulation
- **SOC 2** - Security controls framework
- **OWASP Top 10** - Web application security risks
- **NIST** - Cybersecurity framework compliance

## 🚀 Performance Testing

### Test Types
- **Load Testing** - Normal expected load
- **Stress Testing** - Beyond normal capacity
- **Spike Testing** - Sudden load increases
- **Volume Testing** - Large amounts of data
- **Endurance Testing** - Extended periods

### Metrics Collected
- **Response Time** - Average, median, 95th/99th percentile
- **Throughput** - Requests per second
- **Error Rate** - Percentage of failed requests
- **Resource Usage** - CPU, memory, network
- **Scalability** - Performance vs. load relationship

## 🤝 Contributing

We welcome contributions to the MCP Testing Framework! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd mcp-testing-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\\Scripts\\activate` on Windows

# Install in development mode
pip install -e .
pip install -r requirements-test.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_testing_framework --cov-report=html

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m security    # Run only security tests
pytest -m performance # Run only performance tests
```

## 📚 Documentation

- [User Guide](docs/user_guide.md) - Comprehensive usage guide
- [API Reference](docs/api_reference.md) - Detailed API documentation
- [Examples](docs/examples/) - Example implementations and use cases
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [FAQ](docs/faq.md) - Frequently asked questions

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions
- **Email**: Contact the maintainers at support@mcp-testing.org

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The MCP Protocol specification team
- The open source testing community
- All contributors and testers

## 📈 Roadmap

### Version 2.0 (Planned)
- [ ] Visual test builder interface
- [ ] AI-powered test generation
- [ ] Advanced chaos engineering features
- [ ] Real-time collaborative testing
- [ ] Plugin ecosystem for custom test types

### Version 1.5 (In Progress)
- [ ] Enhanced reporting with custom dashboards
- [ ] Integrated test data generation
- [ ] Advanced performance profiling
- [ ] Multi-language server support
- [ ] Cloud-native testing features

---

**Made with ❤️ for the MCP community**