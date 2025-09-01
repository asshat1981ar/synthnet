#!/usr/bin/env python3
"""
Test suite for MCP Validator
Tests the validation framework for MCP server implementations.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import ast
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from validators.mcp_validator import MCPValidator, ValidationResult, ServerValidationReport

class TestValidationResult:
    """Test ValidationResult dataclass functionality."""
    
    def test_validation_result_creation(self):
        """Test basic validation result creation."""
        result = ValidationResult(
            passed=True,
            message="Test validation passed",
            severity="info",
            category="structure"
        )
        
        assert result.passed == True
        assert result.message == "Test validation passed"
        assert result.severity == "info"
        assert result.category == "structure"
        assert result.details is None
    
    def test_validation_result_with_details(self):
        """Test validation result with additional details."""
        details = {"file": "test.py", "line": 42}
        result = ValidationResult(
            passed=False,
            message="Validation failed",
            severity="error",
            category="security",
            details=details
        )
        
        assert result.details == details
        assert result.severity == "error"

class TestServerValidationReport:
    """Test ServerValidationReport functionality."""
    
    def test_report_creation(self):
        """Test basic report creation."""
        report = ServerValidationReport(
            server_path="/test/path",
            overall_score=0.0,
            passed=False
        )
        
        assert report.server_path == "/test/path"
        assert report.overall_score == 0.0
        assert report.passed == False
        assert len(report.results) == 0
        assert len(report.recommendations) == 0
    
    def test_add_result(self):
        """Test adding validation results to report."""
        report = ServerValidationReport(
            server_path="/test/path",
            overall_score=0.0,
            passed=False
        )
        
        result1 = ValidationResult(True, "Test 1", "info", "structure")
        result2 = ValidationResult(False, "Test 2", "error", "security")
        
        report.add_result(result1)
        report.add_result(result2)
        
        assert len(report.results) == 2
        assert report.results[0] == result1
        assert report.results[1] == result2
    
    def test_get_errors(self):
        """Test getting error-level results."""
        report = ServerValidationReport("/test/path", 0.0, False)
        
        error_result = ValidationResult(False, "Error", "error", "security")
        warning_result = ValidationResult(False, "Warning", "warning", "performance")
        info_result = ValidationResult(True, "Info", "info", "structure")
        
        report.add_result(error_result)
        report.add_result(warning_result)
        report.add_result(info_result)
        
        errors = report.get_errors()
        assert len(errors) == 1
        assert errors[0] == error_result
    
    def test_get_warnings(self):
        """Test getting warning-level results."""
        report = ServerValidationReport("/test/path", 0.0, False)
        
        error_result = ValidationResult(False, "Error", "error", "security")
        warning_result = ValidationResult(False, "Warning", "warning", "performance")
        info_result = ValidationResult(True, "Info", "info", "structure")
        
        report.add_result(error_result)
        report.add_result(warning_result)
        report.add_result(info_result)
        
        warnings = report.get_warnings()
        assert len(warnings) == 1
        assert warnings[0] == warning_result
    
    def test_calculate_score(self):
        """Test score calculation."""
        report = ServerValidationReport("/test/path", 0.0, False)
        
        # Add mixed results
        report.add_result(ValidationResult(True, "Pass 1", "info", "structure"))
        report.add_result(ValidationResult(True, "Pass 2", "info", "structure"))
        report.add_result(ValidationResult(False, "Fail 1", "warning", "performance"))
        report.add_result(ValidationResult(False, "Fail 2", "error", "security"))
        
        report.calculate_score()
        
        # Score should be calculated based on passed checks minus penalties
        assert report.overall_score >= 0.0
        assert report.overall_score <= 100.0
        # With 2 passes out of 4 total, minus penalties, should be lower score
        assert report.overall_score < 50.0

class TestMCPValidator:
    """Test MCPValidator functionality."""
    
    @pytest.fixture
    def validator(self):
        """Create an MCPValidator instance for testing."""
        return MCPValidator()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_validator_initialization(self, validator):
        """Test validator initialization."""
        assert validator is not None
        assert validator.security_patterns is not None
        assert validator.required_methods is not None
        assert validator.best_practices is not None
    
    def test_load_security_patterns(self, validator):
        """Test loading of security vulnerability patterns."""
        patterns = validator.security_patterns
        
        assert "sql_injection" in patterns
        assert "command_injection" in patterns
        assert "path_traversal" in patterns
        assert "hardcoded_secrets" in patterns
        
        # Check that patterns are valid regex patterns
        sql_patterns = patterns["sql_injection"]
        assert len(sql_patterns) > 0
        assert isinstance(sql_patterns, list)
    
    def test_load_required_methods(self, validator):
        """Test loading of required method definitions."""
        methods = validator.required_methods
        
        assert "tools" in methods
        assert "resources" in methods
        assert "prompts" in methods
        assert "common" in methods
        
        # Check common methods
        common_methods = methods["common"]
        assert "__init__" in common_methods
        assert "setup_handlers" in common_methods
        assert "run" in common_methods
        
        # Check capability-specific methods
        tool_methods = methods["tools"]
        assert "list_tools" in tool_methods
        assert "call_tool" in tool_methods
    
    def test_load_best_practices(self, validator):
        """Test loading of best practice guidelines."""
        practices = validator.best_practices
        
        assert "error_handling" in practices
        assert "performance" in practices
        assert "documentation" in practices
        assert "testing" in practices
        
        # Check error handling practices
        error_practices = practices["error_handling"]
        assert "required_exceptions" in error_practices
        assert "logging_required" in error_practices
    
    def test_validate_nonexistent_server(self, validator):
        """Test validation of non-existent server path."""
        report = validator.validate_server("/nonexistent/path")
        
        assert not report.passed
        assert len(report.get_errors()) > 0
        assert any("does not exist" in result.message for result in report.get_errors())
    
    def test_validate_empty_directory(self, validator, temp_dir):
        """Test validation of empty directory."""
        report = validator.validate_server(temp_dir)
        
        assert not report.passed
        # Should have structural errors about missing files
        errors = report.get_errors()
        assert len(errors) > 0
        assert any("server implementation file" in result.message.lower() for result in report.get_errors())

class TestStructureValidation:
    """Test server structure validation."""
    
    @pytest.fixture
    def validator(self):
        return MCPValidator()
    
    @pytest.fixture
    def temp_server_dir(self):
        """Create a temporary directory with basic server structure."""
        temp_dir = tempfile.mkdtemp()
        
        # Create a basic Python server file
        server_file = Path(temp_dir) / "test_server.py"
        server_content = '''
"""Test MCP Server"""
import mcp.server
import mcp.types

class TestServer:
    def __init__(self):
        self.server = mcp.server.Server("test-server")
    
    async def run(self):
        pass
'''
        server_file.write_text(server_content)
        
        # Create README
        readme_file = Path(temp_dir) / "README.md"
        readme_file.write_text("# Test Server\nA test MCP server.")
        
        # Create requirements.txt
        req_file = Path(temp_dir) / "requirements.txt"
        req_file.write_text("mcp>=0.1.0\n")
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_validate_basic_structure_pass(self, validator, temp_server_dir):
        """Test validation of basic server structure that should pass."""
        report = validator.validate_server(temp_server_dir)
        
        # Should find server file and README
        structure_results = [r for r in report.results if r.category == "structure"]
        assert len(structure_results) > 0
        
        # Should have some passing structure checks
        passing_structure = [r for r in structure_results if r.passed]
        assert len(passing_structure) > 0
    
    def test_validate_python_file_syntax(self, validator, temp_server_dir):
        """Test Python file syntax validation."""
        # Create a file with syntax error
        bad_file = Path(temp_server_dir) / "bad_server.py"
        bad_file.write_text("def invalid_syntax(\n    pass")  # Missing closing parenthesis
        
        report = validator.validate_server(temp_server_dir)
        
        # Should detect syntax error
        syntax_errors = [r for r in report.results if r.category == "syntax" and not r.passed]
        assert len(syntax_errors) > 0

class TestSecurityValidation:
    """Test security validation functionality."""
    
    @pytest.fixture
    def validator(self):
        return MCPValidator()
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_detect_sql_injection(self, validator, temp_dir):
        """Test detection of SQL injection vulnerabilities."""
        vulnerable_file = Path(temp_dir) / "vulnerable.py"
        vulnerable_content = '''
def unsafe_query(user_id):
    query = "SELECT * FROM users WHERE id = %s" % user_id
    return execute(query)
'''
        vulnerable_file.write_text(vulnerable_content)
        
        report = validator.validate_server(temp_dir)
        
        # Should detect SQL injection vulnerability
        security_errors = [r for r in report.results if r.category == "security" and not r.passed]
        sql_errors = [r for r in security_errors if "sql injection" in r.message.lower()]
        assert len(sql_errors) > 0
    
    def test_detect_hardcoded_secrets(self, validator, temp_dir):
        """Test detection of hardcoded secrets."""
        secret_file = Path(temp_dir) / "secrets.py"
        secret_content = '''
API_KEY = "sk-1234567890abcdef1234567890abcdef"
PASSWORD = "hardcoded_password"
SECRET_TOKEN = "secret_token_123456789"
'''
        secret_file.write_text(secret_content)
        
        report = validator.validate_server(temp_dir)
        
        # Should detect hardcoded secrets
        security_errors = [r for r in report.results if r.category == "security" and not r.passed]
        secret_errors = [r for r in security_errors if "hardcoded" in r.message.lower()]
        assert len(secret_errors) > 0
    
    def test_detect_command_injection(self, validator, temp_dir):
        """Test detection of command injection vulnerabilities."""
        command_file = Path(temp_dir) / "command.py"
        command_content = '''
import os
import subprocess

def unsafe_command(user_input):
    os.system("echo " + user_input)
    subprocess.call("ls " + user_input, shell=True)
'''
        command_file.write_text(command_content)
        
        report = validator.validate_server(temp_dir)
        
        # Should detect command injection
        security_errors = [r for r in report.results if r.category == "security" and not r.passed]
        command_errors = [r for r in security_errors if "command injection" in r.message.lower()]
        assert len(command_errors) > 0
    
    def test_gitignore_security_check(self, validator, temp_dir):
        """Test .gitignore security validation."""
        # No .gitignore file should trigger warning
        report = validator.validate_server(temp_dir)
        
        gitignore_warnings = [r for r in report.results 
                             if r.category == "security" and "gitignore" in r.message.lower()]
        assert len(gitignore_warnings) > 0
        
        # Create .gitignore without security patterns
        gitignore_file = Path(temp_dir) / ".gitignore"
        gitignore_file.write_text("*.pyc\n__pycache__/\n")
        
        report = validator.validate_server(temp_dir)
        
        # Should suggest adding security patterns
        security_warnings = [r for r in report.results 
                           if r.category == "security" and "consider adding" in r.message.lower()]
        assert len(security_warnings) > 0

class TestPythonCodeValidation:
    """Test Python-specific code validation."""
    
    @pytest.fixture
    def validator(self):
        return MCPValidator()
    
    def test_validate_mcp_imports(self, validator):
        """Test MCP import validation."""
        # Valid MCP imports
        valid_content = '''
from mcp.server import Server
import mcp.types as types
import mcp.server.stdio
'''
        
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_mcp_imports(valid_content, report)
        
        import_results = [r for r in report.results if r.category == "imports"]
        passing_imports = [r for r in import_results if r.passed]
        assert len(passing_imports) > 0
        
        # Missing MCP imports
        invalid_content = '''
import json
import asyncio
'''
        
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_mcp_imports(invalid_content, report)
        
        import_errors = [r for r in report.results if r.category == "imports" and not r.passed]
        assert len(import_errors) > 0
    
    def test_validate_class_structure(self, validator):
        """Test class structure validation."""
        # Valid server class
        valid_code = '''
class TestServer:
    def __init__(self):
        pass
'''
        tree = ast.parse(valid_code)
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_class_structure(tree, report)
        
        structure_results = [r for r in report.results if r.category == "structure"]
        passing_structure = [r for r in structure_results if r.passed]
        assert len(passing_structure) > 0
        
        # No server class
        invalid_code = '''
def some_function():
    pass
'''
        tree = ast.parse(invalid_code)
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_class_structure(tree, report)
        
        structure_errors = [r for r in report.results if r.category == "structure" and not r.passed]
        assert len(structure_errors) > 0
    
    def test_validate_async_usage(self, validator):
        """Test async/await validation."""
        # Valid async code
        async_code = '''
async def async_function():
    await something()

async def another_async():
    pass
'''
        tree = ast.parse(async_code)
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_async_usage(tree, report)
        
        async_results = [r for r in report.results if r.category == "performance" and r.passed]
        assert len(async_results) > 0
        
        # No async code
        sync_code = '''
def sync_function():
    return "hello"
'''
        tree = ast.parse(sync_code)
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_async_usage(tree, report)
        
        async_errors = [r for r in report.results if r.category == "performance" and not r.passed]
        assert len(async_errors) > 0
    
    def test_validate_error_handling(self, validator):
        """Test error handling validation."""
        # Good error handling
        good_code = '''
import logging
logger = logging.getLogger(__name__)

try:
    risky_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    raise
'''
        tree = ast.parse(good_code)
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_error_handling(tree, good_code, report)
        
        error_results = [r for r in report.results if r.category == "error_handling" and r.passed]
        assert len(error_results) > 0
        
        # Poor error handling
        bad_code = '''
def risky_function():
    dangerous_operation()
'''
        tree = ast.parse(bad_code)
        report = ServerValidationReport("/test", 0.0, False)
        validator._validate_error_handling(tree, bad_code, report)
        
        error_warnings = [r for r in report.results if r.category == "error_handling" and not r.passed]
        assert len(error_warnings) > 0

class TestReportGeneration:
    """Test validation report generation."""
    
    @pytest.fixture
    def validator(self):
        return MCPValidator()
    
    def test_generate_markdown_report(self, validator):
        """Test markdown report generation."""
        report = ServerValidationReport("/test/server", 85.5, True)
        
        # Add some test results
        report.add_result(ValidationResult(True, "Structure is valid", "info", "structure"))
        report.add_result(ValidationResult(False, "Missing documentation", "warning", "documentation"))
        report.add_result(ValidationResult(False, "Security issue found", "error", "security"))
        
        report.recommendations = [
            "Fix security vulnerabilities",
            "Improve documentation",
            "Add more tests"
        ]
        
        markdown = validator.generate_report_markdown(report)
        
        assert isinstance(markdown, str)
        assert "# MCP Server Validation Report" in markdown
        assert "Overall Status" in markdown
        assert "Score: 85.5/100" in markdown
        assert "/test/server" in markdown
        
        # Check for results sections
        assert "## Recommendations" in markdown
        assert "Fix security vulnerabilities" in markdown
        
        # Check for detailed results
        assert "Structure is valid" in markdown
        assert "Missing documentation" in markdown
        assert "Security issue found" in markdown

class TestIntegrationTests:
    """Integration tests for complete validation workflow."""
    
    @pytest.fixture
    def validator(self):
        return MCPValidator()
    
    @pytest.fixture
    def complete_server_dir(self):
        """Create a complete server directory for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Main server file
        server_file = Path(temp_dir) / "complete_server.py"
        server_content = '''#!/usr/bin/env python3
"""Complete MCP Server for testing."""
import asyncio
import logging
from typing import Dict, List, Any, Optional

from mcp.server import Server
from mcp.server.models import InitializeResult
import mcp.server.stdio
import mcp.types as types

logger = logging.getLogger(__name__)

class CompleteServer:
    """Complete MCP server implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the server."""
        self.config = config or {}
        self.server = Server("complete-server")
        self.setup_handlers()
        logger.info("Server initialized")
    
    def setup_handlers(self):
        """Setup MCP handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="example-tool",
                    description="Example tool implementation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input": {"type": "string", "description": "Input parameter"}
                        },
                        "required": ["input"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
            """Execute a tool."""
            try:
                if name == "example-tool":
                    return await self.example_tool(**arguments or {})
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def example_tool(self, input: str) -> List[types.TextContent]:
        """Example tool implementation."""
        try:
            result = f"Processed: {input}"
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Example tool error: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate configuration."""
        return True
    
    async def run(self):
        """Run the server."""
        logger.info("Starting server...")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializeResult(
                    protocolVersion="2024-11-05",
                    capabilities=types.ServerCapabilities(
                        tools={},
                        logging={}
                    ),
                    serverInfo=types.Implementation(
                        name="complete-server",
                        version="1.0.0"
                    )
                )
            )

async def main():
    """Main entry point."""
    server = CompleteServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
'''
        server_file.write_text(server_content)
        
        # Configuration files
        pyproject_file = Path(temp_dir) / "pyproject.toml"
        pyproject_file.write_text('''[project]
name = "complete-server"
version = "1.0.0"
dependencies = ["mcp>=0.1.0"]
''')
        
        requirements_file = Path(temp_dir) / "requirements.txt"
        requirements_file.write_text("mcp>=0.1.0\nhttpx>=0.24.0\n")
        
        # README
        readme_file = Path(temp_dir) / "README.md"
        readme_content = '''# Complete Server

## Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the server:
```bash
python complete_server.py
```

## Configuration

Configure the server by setting environment variables or using a config file.
'''
        readme_file.write_text(readme_content)
        
        # Tests
        test_dir = Path(temp_dir) / "tests"
        test_dir.mkdir()
        
        test_file = test_dir / "test_complete_server.py"
        test_content = '''import pytest
from complete_server import CompleteServer

@pytest.mark.asyncio
async def test_server_creation():
    """Test server can be created."""
    server = CompleteServer()
    assert server is not None

@pytest.mark.asyncio
async def test_example_tool():
    """Test example tool."""
    server = CompleteServer()
    result = await server.example_tool("test input")
    assert len(result) == 1
    assert "Processed: test input" in result[0].text
'''
        test_file.write_text(test_content)
        
        # .gitignore
        gitignore_file = Path(temp_dir) / ".gitignore"
        gitignore_file.write_text('''*.pyc
__pycache__/
.env
*.key
*.pem
config.json
.pytest_cache/
''')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_complete_server_validation(self, validator, complete_server_dir):
        """Test validation of complete, well-structured server."""
        report = validator.validate_server(complete_server_dir)
        
        # Should have a good score
        assert report.overall_score > 70.0
        
        # Should pass overall
        assert report.passed or len(report.get_errors()) == 0  # Might have warnings but no errors
        
        # Check that various validation categories were tested
        categories = {result.category for result in report.results}
        expected_categories = {"structure", "imports", "methods", "error_handling", "performance", "documentation"}
        assert len(categories.intersection(expected_categories)) >= 4
        
        # Should have some passing results
        passing_results = [r for r in report.results if r.passed]
        assert len(passing_results) > 0
        
        # Check for specific validations
        structure_results = [r for r in report.results if r.category == "structure" and r.passed]
        assert len(structure_results) > 0
        
        import_results = [r for r in report.results if r.category == "imports" and r.passed]
        assert len(import_results) > 0

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])