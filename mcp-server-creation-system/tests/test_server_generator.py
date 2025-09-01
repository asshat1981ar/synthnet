#!/usr/bin/env python3
"""
Test suite for MCP Server Generator
Tests the server generation functionality and template system.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generators.server_generator import ServerGenerator, ServerConfig, create_server_from_category

class TestServerConfig:
    """Test ServerConfig dataclass functionality."""
    
    def test_server_config_creation(self):
        """Test basic server config creation."""
        config = ServerConfig(
            name="test-server",
            description="Test server description",
            language="python",
            category="api_integration"
        )
        
        assert config.name == "test-server"
        assert config.description == "Test server description"
        assert config.language == "python"
        assert config.category == "api_integration"
        assert config.has_tools == True  # default
        assert config.has_resources == False  # default
        assert config.has_prompts == False  # default
    
    def test_server_config_with_custom_capabilities(self):
        """Test server config with custom capabilities."""
        config = ServerConfig(
            name="custom-server",
            description="Custom server",
            language="typescript",
            category="database",
            has_tools=True,
            has_resources=True,
            has_prompts=True
        )
        
        assert config.has_tools == True
        assert config.has_resources == True
        assert config.has_prompts == True
    
    def test_server_config_with_dependencies(self):
        """Test server config with custom dependencies."""
        python_deps = ["mcp", "httpx", "pydantic"]
        ts_deps = ["@modelcontextprotocol/sdk", "axios", "zod"]
        
        config = ServerConfig(
            name="dep-server",
            description="Server with dependencies",
            language="python",
            category="api_integration",
            python_dependencies=python_deps,
            typescript_dependencies=ts_deps
        )
        
        assert config.python_dependencies == python_deps
        assert config.typescript_dependencies == ts_deps

class TestServerGenerator:
    """Test ServerGenerator functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create a ServerGenerator instance for testing."""
        return ServerGenerator(output_dir=temp_dir)
    
    def test_generator_initialization(self, generator):
        """Test generator initialization."""
        assert generator is not None
        assert generator.categories is not None
        assert "api_integration" in generator.categories
        assert "database" in generator.categories
    
    def test_load_categories(self, generator):
        """Test category loading functionality."""
        categories = generator.categories
        
        # Check that essential categories are present
        assert "api_integration" in categories
        assert "database" in categories
        assert "file_system" in categories
        assert "ai_service" in categories
        
        # Check category structure
        api_cat = categories["api_integration"]
        assert "description" in api_cat
        assert "has_tools" in api_cat
        assert "common_tools" in api_cat
        assert "python_dependencies" in api_cat
    
    def test_generate_python_server_basic(self, generator, temp_dir):
        """Test generating a basic Python server."""
        config = ServerConfig(
            name="test-python-server",
            description="Test Python server",
            language="python",
            category="api_integration",
            tools=[{
                "name": "test-tool",
                "description": "Test tool",
                "inputSchema": {"type": "object", "properties": {}}
            }]
        )
        
        output_path = generator.generate_server(config)
        
        # Check that output directory was created
        assert Path(output_path).exists()
        assert Path(output_path).is_dir()
        
        # Check for essential files
        server_file = Path(output_path) / "test_python_server_server.py"
        assert server_file.exists()
        
        pyproject_file = Path(output_path) / "pyproject.toml"
        assert pyproject_file.exists()
        
        readme_file = Path(output_path) / "README.md"
        assert readme_file.exists()
    
    def test_generate_typescript_server_basic(self, generator, temp_dir):
        """Test generating a basic TypeScript server."""
        config = ServerConfig(
            name="test-ts-server",
            description="Test TypeScript server",
            language="typescript",
            category="database",
            tools=[{
                "name": "query-data",
                "description": "Query database",
                "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}}
            }]
        )
        
        output_path = generator.generate_server(config)
        
        # Check that output directory was created
        assert Path(output_path).exists()
        
        # Check for essential files
        server_file = Path(output_path) / "test-ts-server.ts"
        assert server_file.exists()
        
        package_file = Path(output_path) / "package.json"
        assert package_file.exists()
        
        tsconfig_file = Path(output_path) / "tsconfig.json"
        assert tsconfig_file.exists()
    
    def test_generate_server_with_docker(self, generator, temp_dir):
        """Test generating server with Docker support."""
        config = ServerConfig(
            name="docker-server",
            description="Server with Docker",
            language="python",
            category="api_integration",
            include_docker=True
        )
        
        output_path = generator.generate_server(config)
        
        # Check for Docker files
        dockerfile = Path(output_path) / "Dockerfile"
        assert dockerfile.exists()
        
        docker_compose = Path(output_path) / "docker-compose.yml"
        assert docker_compose.exists()
    
    def test_generate_server_with_tests(self, generator, temp_dir):
        """Test generating server with test files."""
        config = ServerConfig(
            name="tested-server",
            description="Server with tests",
            language="python",
            category="api_integration",
            include_tests=True
        )
        
        output_path = generator.generate_server(config)
        
        # Check for test directory and files
        test_dir = Path(output_path) / "tests"
        assert test_dir.exists()
        
        test_file = test_dir / "test_tested_server_server.py"
        assert test_file.exists()
    
    def test_generate_server_with_resources(self, generator, temp_dir):
        """Test generating server with resources."""
        config = ServerConfig(
            name="resource-server",
            description="Server with resources",
            language="python",
            category="file_system",
            has_resources=True,
            resources=[{
                "name": "test-resource",
                "uri": "resource://test",
                "description": "Test resource",
                "mimeType": "text/plain"
            }]
        )
        
        output_path = generator.generate_server(config)
        
        # Check that server file was created and contains resource code
        server_file = Path(output_path) / "resource_server_server.py"
        assert server_file.exists()
        
        with open(server_file, 'r') as f:
            content = f.read()
            assert "list_resources" in content
            assert "read_resource" in content
            assert "test-resource" in content
    
    def test_generate_server_with_prompts(self, generator, temp_dir):
        """Test generating server with prompts."""
        config = ServerConfig(
            name="prompt-server",
            description="Server with prompts",
            language="python",
            category="ai_service",
            has_prompts=True,
            prompts=[{
                "name": "test-prompt",
                "description": "Test prompt",
                "arguments": [{"name": "topic", "description": "Topic to analyze", "required": True}]
            }]
        )
        
        output_path = generator.generate_server(config)
        
        # Check that server file contains prompt code
        server_file = Path(output_path) / "prompt_server_server.py"
        assert server_file.exists()
        
        with open(server_file, 'r') as f:
            content = f.read()
            assert "list_prompts" in content
            assert "get_prompt" in content
            assert "test-prompt" in content
    
    def test_to_class_name_conversion(self, generator):
        """Test class name conversion utility."""
        assert generator._to_class_name("test-server") == "TestServer"
        assert generator._to_class_name("my-api-server") == "MyApiServer"
        assert generator._to_class_name("simple") == "Simple"
    
    def test_to_camel_case_conversion(self, generator):
        """Test camel case conversion utility."""
        assert generator._to_camel_case("test-method") == "testMethod"
        assert generator._to_camel_case("get-user-data") == "getUserData"
        assert generator._to_camel_case("simple") == "simple"
    
    def test_generate_tools_list_python(self, generator):
        """Test Python tools list generation."""
        tools = [{
            "name": "test-tool",
            "description": "Test tool description",
            "inputSchema": {
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": ["param"]
            }
        }]
        
        result = generator._generate_tools_list_python(tools)
        
        assert "test-tool" in result
        assert "Test tool description" in result
        assert "param" in result
    
    def test_generate_tools_list_typescript(self, generator):
        """Test TypeScript tools list generation."""
        tools = [{
            "name": "fetch-data",
            "description": "Fetch data from API",
            "inputSchema": {
                "type": "object",
                "properties": {"endpoint": {"type": "string"}},
                "required": ["endpoint"]
            }
        }]
        
        result = generator._generate_tools_list_typescript(tools)
        
        assert "fetch-data" in result
        assert "Fetch data from API" in result
        assert "endpoint" in result

class TestCategoryBasedGeneration:
    """Test category-based server generation."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_create_server_from_category_api(self, temp_dir):
        """Test creating API integration server from category."""
        config = create_server_from_category("test-api-server", "api_integration", "python")
        
        assert config.name == "test-api-server"
        assert config.category == "api_integration"
        assert config.language == "python"
        assert config.has_tools == True
        assert len(config.tools) > 0
        
        # Check that common API tools are present
        tool_names = [tool["name"] for tool in config.tools]
        assert "fetch-data" in tool_names
        assert "post-data" in tool_names
    
    def test_create_server_from_category_database(self, temp_dir):
        """Test creating database server from category."""
        config = create_server_from_category("test-db-server", "database", "typescript")
        
        assert config.category == "database"
        assert config.language == "typescript"
        assert config.has_tools == True
        assert config.has_resources == True
        
        # Check for database-specific tools
        tool_names = [tool["name"] for tool in config.tools]
        assert "query" in tool_names
        assert "insert" in tool_names
    
    def test_create_server_from_invalid_category(self, temp_dir):
        """Test error handling for invalid category."""
        with pytest.raises(ValueError) as exc_info:
            create_server_from_category("test-server", "invalid_category", "python")
        
        assert "Unknown category" in str(exc_info.value)
    
    def test_create_server_from_category_file_system(self, temp_dir):
        """Test creating file system server from category."""
        config = create_server_from_category("file-server", "file_system", "python")
        
        assert config.category == "file_system"
        assert config.has_tools == True
        assert config.has_resources == True
        
        # Check for file system tools
        tool_names = [tool["name"] for tool in config.tools]
        assert "read-file" in tool_names
        assert "write-file" in tool_names
        assert "list-directory" in tool_names

class TestValidationAndErrorHandling:
    """Test validation and error handling in server generation."""
    
    @pytest.fixture
    def generator(self):
        """Create a ServerGenerator instance."""
        return ServerGenerator()
    
    def test_generate_server_invalid_language(self, generator):
        """Test error handling for invalid language."""
        config = ServerConfig(
            name="test-server",
            description="Test server",
            language="invalid_language",
            category="api_integration"
        )
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate_server(config)
        
        assert "Unsupported language" in str(exc_info.value)
    
    def test_generate_server_missing_name(self, generator):
        """Test error handling for missing server name."""
        config = ServerConfig(
            name="",
            description="Test server",
            language="python",
            category="api_integration"
        )
        
        # Should handle empty name gracefully or raise appropriate error
        # This depends on the specific validation logic implemented
        try:
            result = generator.generate_server(config)
            # If it succeeds, check that some default name was used
            assert result is not None
        except Exception as e:
            # If it fails, should be a clear validation error
            assert "name" in str(e).lower()

class TestIntegrationTests:
    """Integration tests for the complete server generation workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_complete_python_server_generation(self, temp_dir):
        """Test complete Python server generation workflow."""
        # Create configuration
        config = create_server_from_category("integration-test-server", "api_integration", "python")
        config.include_docker = True
        config.include_tests = True
        config.include_docs = True
        
        # Generate server
        generator = ServerGenerator(output_dir=temp_dir)
        output_path = generator.generate_server(config)
        
        # Verify all expected files are created
        base_path = Path(output_path)
        
        # Core files
        assert (base_path / "integration_test_server_server.py").exists()
        assert (base_path / "pyproject.toml").exists()
        assert (base_path / "requirements.txt").exists()
        assert (base_path / "README.md").exists()
        
        # Docker files
        assert (base_path / "Dockerfile").exists()
        assert (base_path / "docker-compose.yml").exists()
        
        # Test files
        assert (base_path / "tests").exists()
        assert (base_path / "tests" / "test_integration_test_server_server.py").exists()
        
        # Check that the generated Python file is valid syntax
        server_file = base_path / "integration_test_server_server.py"
        with open(server_file, 'r') as f:
            content = f.read()
        
        # Basic syntax check - should be able to compile
        try:
            compile(content, str(server_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Generated Python file has syntax errors: {e}")
    
    def test_complete_typescript_server_generation(self, temp_dir):
        """Test complete TypeScript server generation workflow."""
        # Create configuration
        config = create_server_from_category("ts-integration-test", "database", "typescript")
        config.include_docker = True
        config.include_tests = True
        
        # Generate server
        generator = ServerGenerator(output_dir=temp_dir)
        output_path = generator.generate_server(config)
        
        # Verify all expected files are created
        base_path = Path(output_path)
        
        # Core files
        assert (base_path / "ts-integration-test.ts").exists()
        assert (base_path / "package.json").exists()
        assert (base_path / "tsconfig.json").exists()
        assert (base_path / "README.md").exists()
        
        # Docker files
        assert (base_path / "Dockerfile").exists()
        
        # Test files
        assert (base_path / "tests").exists()
        assert (base_path / "tests" / "ts-integration-test.test.ts").exists()
        
        # Check package.json structure
        with open(base_path / "package.json", 'r') as f:
            package_data = json.load(f)
        
        assert package_data["name"] == "ts-integration-test"
        assert "@modelcontextprotocol/sdk" in package_data["dependencies"]
        assert "typescript" in package_data["devDependencies"]

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])