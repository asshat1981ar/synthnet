# MCP Server Creation System - Developer Guide

This guide provides comprehensive documentation for developers who want to use, extend, or contribute to the MCP Server Creation System.

## Table of Contents

1. [Getting Started](#getting-started)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Creating New Servers](#creating-new-servers)
5. [Extending Templates](#extending-templates)
6. [Validation and Testing](#validation-and-testing)
7. [Best Practices](#best-practices)
8. [Contributing](#contributing)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 18+ (for TypeScript servers)
- Git
- Basic understanding of MCP (Model Context Protocol)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/mcp-server-creation-system.git
cd mcp-server-creation-system

# Install Python dependencies
pip install -r requirements.txt

# For TypeScript development
npm install -g typescript tsx

# Run tests to verify installation
python -m pytest tests/ -v
```

### Quick Start Example

```python
from generators.server_generator import create_server_from_category, ServerGenerator

# Create a new API integration server
config = create_server_from_category("my-api-server", "api_integration", "python")

# Generate the server
generator = ServerGenerator()
output_path = generator.generate_server(config)

print(f"Server generated at: {output_path}")
```

## System Architecture

### Component Overview

```
MCP Server Creation System
├── Templates Layer      # Base templates and patterns
├── Generation Layer     # Code generation and customization
├── Analysis Layer       # Ecosystem gap analysis
├── Validation Layer     # Quality assurance and compliance
└── Example Layer        # Production-ready implementations
```

### Data Flow

1. **Input**: Server specification (category, language, requirements)
2. **Analysis**: Gap analysis identifies opportunities and patterns
3. **Generation**: Templates are customized and code is generated
4. **Validation**: Generated code is validated for compliance and quality
5. **Output**: Production-ready MCP server with documentation and tests

### Key Design Principles

- **Template-driven**: Reusable templates for common patterns
- **Specification-based**: Generate from declarative configurations
- **Quality-first**: Built-in validation and best practices
- **Multi-language**: Support for Python and TypeScript
- **Production-ready**: Complete with Docker, tests, and documentation

## Core Components

### 1. Server Generator (`generators/server_generator.py`)

The main component for creating new MCP servers.

```python
class ServerGenerator:
    """Generates MCP servers from templates and configurations."""
    
    def generate_server(self, config: ServerConfig) -> str:
        """Generate a complete MCP server from configuration."""
        # Implementation details...
```

**Key Features:**
- Multi-language support (Python, TypeScript)
- Category-based templates
- Customizable tools, resources, and prompts
- Automatic Docker and test generation

**Usage Examples:**

```python
# Basic server generation
config = ServerConfig(
    name="weather-api-server",
    description="Weather API integration server",
    language="python",
    category="api_integration"
)

generator = ServerGenerator()
server_path = generator.generate_server(config)
```

```python
# Advanced server with custom tools
config = ServerConfig(
    name="custom-server",
    description="Custom server with specific tools",
    language="typescript",
    category="database",
    tools=[{
        "name": "query-users",
        "description": "Query user database",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 10}
            }
        }
    }],
    resources=[{
        "name": "user-data",
        "uri": "db://users",
        "description": "User database access",
        "mimeType": "application/json"
    }]
)
```

### 2. Gap Analyzer (`analyzers/gap_analyzer.py`)

Identifies opportunities in the MCP ecosystem.

```python
class GapAnalyzer:
    """Analyzes the MCP ecosystem to identify gaps and opportunities."""
    
    def identify_opportunities(self) -> List[GapOpportunity]:
        """Identify gaps and opportunities in the MCP ecosystem."""
        # Analysis implementation...
```

**Key Features:**
- Analysis of 200+ existing MCP servers
- Industry-specific gap identification
- Technology trend analysis
- Prioritized opportunity ranking

**Usage Examples:**

```python
from analyzers.gap_analyzer import GapAnalyzer

analyzer = GapAnalyzer()

# Get all opportunities
opportunities = analyzer.identify_opportunities()
print(f"Found {len(opportunities)} opportunities")

# Get healthcare-specific opportunities
healthcare_ops = analyzer.get_server_suggestions_for_industry("healthcare")

# Generate comprehensive report
report = analyzer.generate_gap_report(opportunities)
with open("gap_analysis.md", "w") as f:
    f.write(report)
```

### 3. MCP Validator (`validators/mcp_validator.py`)

Validates MCP server implementations for compliance and quality.

```python
class MCPValidator:
    """Validates MCP server implementations for compliance and best practices."""
    
    def validate_server(self, server_path: str) -> ServerValidationReport:
        """Perform comprehensive validation of an MCP server."""
        # Validation implementation...
```

**Key Features:**
- MCP protocol compliance checking
- Security vulnerability scanning
- Code quality analysis
- Best practices validation

**Usage Examples:**

```python
from validators.mcp_validator import MCPValidator

validator = MCPValidator()

# Validate a server implementation
report = validator.validate_server("/path/to/server")

print(f"Validation Score: {report.overall_score}/100")
print(f"Status: {'PASSED' if report.passed else 'FAILED'}")

# Generate detailed report
markdown_report = validator.generate_report_markdown(report)
with open("validation_report.md", "w") as f:
    f.write(markdown_report)

# Get specific issues
errors = report.get_errors()
warnings = report.get_warnings()
```

### 4. Code Generator (`generators/code_generator.py`)

Advanced code generation with custom specifications.

```python
class CodeGenerator:
    """Generates production-ready code for MCP servers."""
    
    def generate_custom_server(self, server_spec: Dict[str, Any]) -> str:
        """Generate a custom MCP server from detailed specifications."""
        # Generation implementation...
```

**Key Features:**
- Specification-driven generation
- OpenAPI integration
- Custom tool/resource templates
- Production-ready output

## Creating New Servers

### Method 1: Category-based Generation

The easiest way to create a new server is using predefined categories:

```python
from generators.server_generator import create_server_from_category, ServerGenerator

# Available categories:
# - api_integration
# - database
# - file_system
# - web_scraping
# - ai_service
# - business_tool

config = create_server_from_category("my-server", "api_integration", "python")
generator = ServerGenerator()
server_path = generator.generate_server(config)
```

### Method 2: Custom Specification

For more control, create a custom specification:

```python
from generators.code_generator import CodeGenerator

spec = {
    "name": "healthcare-integration-server",
    "description": "Healthcare system integration server",
    "language": "python",
    "category": "healthcare",
    "required_config": ["api_key", "endpoint_url"],
    "tools": [
        {
            "name": "get-patient-data",
            "description": "Retrieve patient information",
            "type": "api_get",
            "input_schema": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string", "description": "Patient ID"},
                    "include_history": {"type": "boolean", "default": False}
                },
                "required": ["patient_id"]
            }
        },
        {
            "name": "create-appointment",
            "description": "Schedule patient appointment",
            "type": "api_post",
            "input_schema": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "provider_id": {"type": "string"},
                    "datetime": {"type": "string", "format": "date-time"},
                    "reason": {"type": "string"}
                },
                "required": ["patient_id", "provider_id", "datetime"]
            }
        }
    ],
    "resources": [
        {
            "name": "patient-records",
            "description": "Patient medical records",
            "type": "api_resource",
            "uri": "api://patients"
        }
    ],
    "prompts": [
        {
            "name": "medical-summary",
            "description": "Generate medical summary",
            "type": "analysis_prompt",
            "arguments": [
                {"name": "patient_data", "description": "Patient medical data", "required": True}
            ]
        }
    ]
}

generator = CodeGenerator()
server_path = generator.generate_custom_server(spec)
```

### Method 3: OpenAPI Integration

Generate from existing OpenAPI specifications:

```python
import json
from generators.code_generator import CodeGenerator

# Load OpenAPI specification
with open("healthcare_api.json", "r") as f:
    openapi_spec = json.load(f)

generator = CodeGenerator()
server_path = generator.generate_server_from_openapi(
    openapi_spec, 
    "healthcare-api-server"
)
```

## Extending Templates

### Adding New Server Categories

1. **Define the category in `server_generator.py`:**

```python
def load_categories(self) -> Dict[str, Dict[str, Any]]:
    return {
        # Existing categories...
        "custom_category": {
            "description": "Custom category description",
            "has_tools": True,
            "has_resources": True,
            "has_prompts": False,
            "common_tools": ["tool1", "tool2"],
            "python_dependencies": ["mcp", "custom-lib"],
            "typescript_dependencies": ["@modelcontextprotocol/sdk", "custom-package"]
        }
    }
```

2. **Create specific tool implementations in `code_generator.py`:**

```python
def load_tool_templates(self) -> Dict[str, ToolSchema]:
    return {
        # Existing templates...
        "custom_tool": ToolSchema(
            name="custom-tool",
            description="Custom tool implementation",
            input_schema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Custom parameter"}
                },
                "required": ["param"]
            },
            implementation_template="""
async def custom_tool(self, param: str) -> List[types.TextContent]:
    \"\"\"Custom tool implementation.\"\"\"
    try:
        # Custom logic here
        result = f"Custom processing: {param}"
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"Custom tool error: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
""",
            required_imports=["custom_lib"]
        )
    }
```

### Creating Custom Templates

1. **Create a new template file:**

```python
# templates/custom_server_template.py
"""
Custom MCP Server Template
Specialized for specific use case
"""

# Template content with placeholder variables
class {ServerClassName}:
    def __init__(self):
        self.server = Server("{server_name}")
        # Custom initialization
```

2. **Register the template:**

```python
# In server_generator.py
def _generate_custom_server(self, config: ServerConfig, server_dir: Path):
    """Generate custom server implementation."""
    template_path = self.template_dir / "custom_server_template.py"
    # Template processing logic
```

### Adding New Tool Types

```python
# In code_generator.py
def load_tool_templates(self):
    return {
        # Add new tool type
        "websocket_tool": ToolSchema(
            name="websocket-connection",
            description="WebSocket connection tool",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "WebSocket URL"},
                    "message": {"type": "string", "description": "Message to send"}
                },
                "required": ["url"]
            },
            implementation_template="""
async def websocket_connection(self, url: str, message: Optional[str] = None) -> List[types.TextContent]:
    \"\"\"Establish WebSocket connection and send message.\"\"\"
    try:
        import websockets
        
        async with websockets.connect(url) as websocket:
            if message:
                await websocket.send(message)
                response = await websocket.recv()
                return [types.TextContent(type="text", text=response)]
            else:
                return [types.TextContent(type="text", text="Connected successfully")]
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        return [types.TextContent(type="text", text=f"Connection failed: {str(e)}")]
""",
            required_imports=["websockets"]
        )
    }
```

## Validation and Testing

### Running Validation

```python
from validators.mcp_validator import MCPValidator

# Validate generated server
validator = MCPValidator()
report = validator.validate_server("path/to/generated/server")

# Check specific aspects
if report.overall_score < 80:
    print("Server needs improvement:")
    for error in report.get_errors():
        print(f"- {error.message}")
    for warning in report.get_warnings():
        print(f"- {warning.message}")
```

### Custom Validation Rules

```python
# Extend MCPValidator for custom rules
class CustomMCPValidator(MCPValidator):
    
    def _validate_custom_requirements(self, server_path: Path, report: ServerValidationReport):
        """Add custom validation rules."""
        
        # Custom validation logic
        server_files = list(server_path.glob("*.py"))
        
        for file_path in server_files:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for custom requirements
            if "custom_requirement" not in content:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Missing custom requirement in {file_path.name}",
                    severity="warning",
                    category="custom"
                ))
```

### Automated Testing

```python
# tests/test_custom_server.py
import pytest
from pathlib import Path
from generators.server_generator import create_server_from_category, ServerGenerator
from validators.mcp_validator import MCPValidator

@pytest.mark.integration
def test_generated_server_quality():
    """Test that generated servers meet quality standards."""
    
    # Generate server
    config = create_server_from_category("test-server", "api_integration", "python")
    generator = ServerGenerator()
    server_path = generator.generate_server(config)
    
    # Validate server
    validator = MCPValidator()
    report = validator.validate_server(server_path)
    
    # Quality checks
    assert report.overall_score >= 80, f"Server quality too low: {report.overall_score}"
    assert len(report.get_errors()) == 0, f"Server has errors: {[e.message for e in report.get_errors()]}"
    
    # Cleanup
    import shutil
    shutil.rmtree(server_path)
```

## Best Practices

### 1. Server Design

**Follow MCP Conventions:**
- Use clear, descriptive tool names (kebab-case)
- Provide comprehensive input schemas
- Include proper error handling
- Use appropriate HTTP status codes

**Example:**
```python
# Good
types.Tool(
    name="get-user-profile",
    description="Retrieve detailed user profile information",
    inputSchema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string", 
                "description": "Unique user identifier",
                "minLength": 1
            },
            "include_preferences": {
                "type": "boolean",
                "description": "Include user preferences in response",
                "default": False
            }
        },
        "required": ["user_id"]
    }
)

# Avoid
types.Tool(
    name="getuser",  # Poor naming
    description="Get user",  # Vague description
    inputSchema={}  # No input validation
)
```

### 2. Error Handling

**Implement Comprehensive Error Handling:**

```python
async def api_call_tool(self, endpoint: str, **kwargs) -> List[types.TextContent]:
    """Make API call with proper error handling."""
    try:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint, params=kwargs)
            response.raise_for_status()
            
            return [types.TextContent(
                type="text",
                text=json.dumps(response.json(), indent=2)
            )]
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        return [types.TextContent(
            type="text",
            text=f"API Error {e.response.status_code}: {e.response.text}"
        )]
    except httpx.TimeoutException:
        logger.error(f"Timeout calling {endpoint}")
        return [types.TextContent(
            type="text",
            text=f"Request timeout for {endpoint}"
        )]
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Unexpected error: {str(e)}"
        )]
```

### 3. Security

**Implement Security Best Practices:**

```python
class SecureServer:
    def __init__(self, config: Dict[str, Any]):
        # Never hardcode secrets
        self.api_key = config.get('api_key') or os.environ.get('API_KEY')
        if not self.api_key:
            raise ValueError("API key is required")
        
        # Validate configuration
        self.validate_config()
    
    def validate_input(self, user_input: str) -> str:
        """Validate and sanitize user input."""
        # Input validation
        if not user_input or len(user_input.strip()) == 0:
            raise ValueError("Input cannot be empty")
        
        # Sanitization
        sanitized = user_input.strip()[:1000]  # Limit length
        
        # Check for injection attempts
        dangerous_patterns = ['<script', '${', '`', 'eval(']
        for pattern in dangerous_patterns:
            if pattern in sanitized.lower():
                raise ValueError("Potentially dangerous input detected")
        
        return sanitized
    
    async def safe_file_access(self, file_path: str) -> str:
        """Safely access files with path validation."""
        # Prevent directory traversal
        if '..' in file_path or file_path.startswith('/'):
            raise ValueError("Invalid file path")
        
        # Construct safe path
        safe_path = Path(self.config.get('base_path', '.')) / file_path
        
        # Check if file exists and is readable
        if not safe_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        async with aiofiles.open(safe_path, mode='r') as f:
            return await f.read()
```

### 4. Performance

**Optimize for Performance:**

```python
class PerformantServer:
    def __init__(self, config: Dict[str, Any]):
        # Connection pooling
        self.http_client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=httpx.Timeout(10.0)
        )
        
        # Caching
        self.cache = {}
        self.cache_ttl = config.get('cache_ttl', 300)  # 5 minutes
    
    async def cached_api_call(self, endpoint: str) -> Any:
        """Make API call with caching."""
        cache_key = f"api:{endpoint}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        # Make API call
        async with self.http_client.get(endpoint) as response:
            response.raise_for_status()
            data = response.json()
        
        # Cache result
        self.cache[cache_key] = (data, time.time())
        
        return data
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
```

### 5. Documentation

**Provide Comprehensive Documentation:**

```python
class DocumentedServer:
    """
    Comprehensive MCP Server with full documentation.
    
    This server provides integration with Example API service,
    offering tools for data retrieval, processing, and analysis.
    
    Configuration:
        api_key (str): API authentication key
        base_url (str): API base URL (default: https://api.example.com)
        timeout (int): Request timeout in seconds (default: 30)
        
    Tools:
        - fetch-data: Retrieve data from API
        - process-data: Process and analyze data
        - export-results: Export processed results
        
    Resources:
        - api-status: Current API status and health
        - rate-limits: Current rate limit status
        
    Example:
        server = DocumentedServer({
            'api_key': 'your-api-key',
            'base_url': 'https://api.example.com',
            'timeout': 30
        })
        await server.run()
    """
    
    async def fetch_data(self, query: str, limit: int = 10) -> List[types.TextContent]:
        """
        Fetch data from the API based on query parameters.
        
        Args:
            query (str): Search query string
            limit (int): Maximum number of results to return (default: 10)
            
        Returns:
            List[types.TextContent]: Formatted API response data
            
        Raises:
            ValueError: If query is empty or invalid
            httpx.HTTPStatusError: If API request fails
            
        Example:
            result = await server.fetch_data("user data", limit=5)
        """
        # Implementation...
```

## Contributing

### Development Setup

1. **Fork and clone the repository**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Contribution Guidelines

1. **Code Style:**
   - Follow PEP 8 for Python code
   - Use type hints for all function parameters and return values
   - Add comprehensive docstrings
   - Format code with Black: `black .`

2. **Testing:**
   - Write tests for all new functionality
   - Maintain >80% code coverage
   - Run tests before submitting: `pytest tests/ -v`

3. **Documentation:**
   - Update relevant documentation
   - Add examples for new features
   - Update the changelog

4. **Pull Request Process:**
   - Create feature branch from main
   - Write clear, descriptive commit messages
   - Submit PR with detailed description
   - Ensure all CI checks pass

### Adding New Features

1. **New Server Categories:**
   - Add category definition to `server_generator.py`
   - Create category-specific templates
   - Add validation rules
   - Write comprehensive tests
   - Update documentation

2. **New Tool Types:**
   - Define tool schema in `code_generator.py`
   - Implement template with error handling
   - Add security considerations
   - Create usage examples
   - Add validation tests

3. **New Validation Rules:**
   - Extend `MCPValidator` class
   - Add rule-specific tests
   - Document the rule purpose and behavior
   - Consider performance impact

### Release Process

1. **Version Bump:**
   - Update version numbers in relevant files
   - Update CHANGELOG.md with new features and fixes

2. **Testing:**
   - Run full test suite
   - Test generated servers manually
   - Validate example implementations

3. **Documentation:**
   - Update API documentation
   - Refresh examples and tutorials
   - Update installation instructions

4. **Release:**
   - Create release tag
   - Build and test packages
   - Update deployment documentation

---

## Support and Resources

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Community questions and discussions
- **Documentation**: Comprehensive guides and API reference
- **Examples**: Production-ready server implementations

For more information, see the [main README](../README.md) and [System Overview](SYSTEM_OVERVIEW.md).