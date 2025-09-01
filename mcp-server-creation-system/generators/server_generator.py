#!/usr/bin/env python3
"""
MCP Server Generator
Generates complete MCP servers from templates and configurations.
"""

import os
import json
import yaml
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ServerConfig:
    """Configuration for generating an MCP server."""
    name: str
    description: str
    language: str  # 'python' or 'typescript'
    category: str
    
    # Capabilities
    has_tools: bool = True
    has_resources: bool = False
    has_prompts: bool = False
    
    # Tools configuration
    tools: List[Dict[str, Any]] = field(default_factory=list)
    resources: List[Dict[str, Any]] = field(default_factory=list)
    prompts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Configuration requirements
    required_config: List[str] = field(default_factory=list)
    
    # API/Integration specific
    api_endpoint: Optional[str] = None
    auth_method: Optional[str] = None
    rate_limits: Optional[Dict[str, int]] = None
    
    # Dependencies
    python_dependencies: List[str] = field(default_factory=lambda: ['mcp'])
    typescript_dependencies: List[str] = field(default_factory=lambda: ['@modelcontextprotocol/sdk'])
    
    # Docker and deployment
    include_docker: bool = True
    include_tests: bool = True
    include_docs: bool = True

class ServerGenerator:
    """Generates MCP servers from templates and configurations."""
    
    def __init__(self, template_dir: Optional[str] = None, output_dir: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = Path(template_dir) if template_dir else self.base_dir / "templates"
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / "generated_servers"
        self.output_dir.mkdir(exist_ok=True)
        
        # Load server category configurations
        self.categories = self.load_categories()
    
    def load_categories(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined server category configurations."""
        return {
            "api_integration": {
                "description": "REST/GraphQL API integration server",
                "has_tools": True,
                "has_resources": True,
                "common_tools": ["fetch_data", "post_data", "list_endpoints"],
                "python_dependencies": ["mcp", "httpx", "pydantic"],
                "typescript_dependencies": ["@modelcontextprotocol/sdk", "axios", "zod"]
            },
            "database": {
                "description": "Database connector server", 
                "has_tools": True,
                "has_resources": True,
                "common_tools": ["query", "insert", "update", "delete", "list_tables"],
                "python_dependencies": ["mcp", "sqlalchemy", "asyncpg"],
                "typescript_dependencies": ["@modelcontextprotocol/sdk", "pg", "@types/pg"]
            },
            "file_system": {
                "description": "File system access server",
                "has_tools": True,
                "has_resources": True,
                "common_tools": ["read_file", "write_file", "list_directory", "create_directory"],
                "python_dependencies": ["mcp", "aiofiles"],
                "typescript_dependencies": ["@modelcontextprotocol/sdk", "fs-extra"]
            },
            "web_scraping": {
                "description": "Web scraping and content extraction server",
                "has_tools": True,
                "has_resources": False,
                "common_tools": ["scrape_url", "extract_links", "get_page_content"],
                "python_dependencies": ["mcp", "httpx", "beautifulsoup4", "lxml"],
                "typescript_dependencies": ["@modelcontextprotocol/sdk", "puppeteer", "cheerio"]
            },
            "ai_service": {
                "description": "AI service integration server",
                "has_tools": True,
                "has_prompts": True,
                "common_tools": ["generate_text", "classify", "embed"],
                "python_dependencies": ["mcp", "httpx", "openai"],
                "typescript_dependencies": ["@modelcontextprotocol/sdk", "openai"]
            },
            "business_tool": {
                "description": "Business tool integration server",
                "has_tools": True,
                "has_resources": True,
                "common_tools": ["create_task", "update_record", "get_analytics"],
                "python_dependencies": ["mcp", "httpx", "pydantic"],
                "typescript_dependencies": ["@modelcontextprotocol/sdk", "axios", "zod"]
            }
        }
    
    def generate_server(self, config: ServerConfig) -> str:
        """Generate a complete MCP server from configuration."""
        server_dir = self.output_dir / config.name
        server_dir.mkdir(exist_ok=True)
        
        # Generate main server file
        if config.language == "python":
            self._generate_python_server(config, server_dir)
        elif config.language == "typescript":
            self._generate_typescript_server(config, server_dir)
        else:
            raise ValueError(f"Unsupported language: {config.language}")
        
        # Generate configuration files
        self._generate_config_files(config, server_dir)
        
        # Generate Docker files
        if config.include_docker:
            self._generate_docker_files(config, server_dir)
        
        # Generate tests
        if config.include_tests:
            self._generate_test_files(config, server_dir)
        
        # Generate documentation
        if config.include_docs:
            self._generate_documentation(config, server_dir)
        
        logger.info(f"Generated MCP server '{config.name}' at {server_dir}")
        return str(server_dir)
    
    def _generate_python_server(self, config: ServerConfig, server_dir: Path):
        """Generate Python MCP server implementation."""
        template_path = self.template_dir / "base_python_server.py"
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Prepare template variables
        class_name = self._to_class_name(config.name)
        
        # Generate tools list
        tools_list = self._generate_tools_list_python(config.tools)
        tool_handlers = self._generate_tool_handlers_python(config.tools)
        
        # Generate resources list
        resources_list = self._generate_resources_list_python(config.resources)
        resource_handlers = self._generate_resource_handlers_python(config.resources)
        
        # Generate prompts list
        prompts_list = self._generate_prompts_list_python(config.prompts)
        prompt_handlers = self._generate_prompt_handlers_python(config.prompts)
        
        # Template substitutions
        substitutions = {
            'ServerClassName': class_name,
            'ServerDescription': config.description,
            'server_name': config.name,
            'ToolsDescription': f"Tools: {', '.join(tool['name'] for tool in config.tools)}" if config.tools else "No tools",
            'ResourcesDescription': f"Resources: {', '.join(res['name'] for res in config.resources)}" if config.resources else "No resources", 
            'PromptsDescription': f"Prompts: {', '.join(prompt['name'] for prompt in config.prompts)}" if config.prompts else "No prompts",
            'has_tools': str(config.has_tools).lower(),
            'has_resources': str(config.has_resources).lower(),
            'has_prompts': str(config.has_prompts).lower(),
            'tools_list': tools_list,
            'tool_handlers': tool_handlers,
            'resources_list': resources_list,
            'resource_handlers': resource_handlers,
            'prompts_list': prompts_list,
            'prompt_handlers': prompt_handlers,
            'required_config_keys': str(config.required_config),
            'example_tool_method': config.tools[0]['name'].replace('-', '_') if config.tools else 'example_tool',
            'example_resource_method': f"read_{config.resources[0]['name'].replace('-', '_')}" if config.resources else 'read_example_resource',
            'example_prompt_method': f"get_{config.prompts[0]['name'].replace('-', '_')}_prompt" if config.prompts else 'get_example_prompt'
        }
        
        # Apply substitutions
        server_code = template.format(**substitutions)
        
        # Write server file
        server_file = server_dir / f"{config.name.replace('-', '_')}_server.py"
        with open(server_file, 'w') as f:
            f.write(server_code)
        
        # Make executable
        server_file.chmod(0o755)
    
    def _generate_typescript_server(self, config: ServerConfig, server_dir: Path):
        """Generate TypeScript/Node.js MCP server implementation."""
        template_path = self.template_dir / "base_typescript_server.ts"
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Prepare template variables
        class_name = self._to_class_name(config.name)
        
        # Generate tools, resources, and prompts
        tools_list = self._generate_tools_list_typescript(config.tools)
        tool_handlers = self._generate_tool_handlers_typescript(config.tools)
        resources_list = self._generate_resources_list_typescript(config.resources)
        resource_handlers = self._generate_resource_handlers_typescript(config.resources)
        prompts_list = self._generate_prompts_list_typescript(config.prompts)
        prompt_handlers = self._generate_prompt_handlers_typescript(config.prompts)
        
        # Template substitutions
        substitutions = {
            'ServerClassName': class_name,
            'ServerDescription': config.description,
            'server_name': config.name,
            'ToolsDescription': f"Tools: {', '.join(tool['name'] for tool in config.tools)}" if config.tools else "No tools",
            'ResourcesDescription': f"Resources: {', '.join(res['name'] for res in config.resources)}" if config.resources else "No resources",
            'PromptsDescription': f"Prompts: {', '.join(prompt['name'] for prompt in config.prompts)}" if config.prompts else "No prompts",
            'has_tools': str(config.has_tools).lower(),
            'has_resources': str(config.has_resources).lower(), 
            'has_prompts': str(config.has_prompts).lower(),
            'tools_list': tools_list,
            'tool_handlers': tool_handlers,
            'resources_list': resources_list,
            'resource_handlers': resource_handlers,
            'prompts_list': prompts_list,
            'prompt_handlers': prompt_handlers,
            'required_config_keys': json.dumps(config.required_config),
            'example_tool_method': self._to_camel_case(config.tools[0]['name']) if config.tools else 'exampleTool',
            'example_resource_method': f"read{self._to_pascal_case(config.resources[0]['name'])}" if config.resources else 'readExampleResource',
            'example_prompt_method': f"get{self._to_pascal_case(config.prompts[0]['name'])}Prompt" if config.prompts else 'getExamplePrompt'
        }
        
        # Apply substitutions
        server_code = template.format(**substitutions)
        
        # Write server file
        server_file = server_dir / f"{config.name}.ts"
        with open(server_file, 'w') as f:
            f.write(server_code)
        
        # Make executable
        server_file.chmod(0o755)
    
    def _generate_config_files(self, config: ServerConfig, server_dir: Path):
        """Generate configuration files for the server."""
        if config.language == "python":
            self._generate_python_config(config, server_dir)
        elif config.language == "typescript":
            self._generate_typescript_config(config, server_dir)
    
    def _generate_python_config(self, config: ServerConfig, server_dir: Path):
        """Generate Python-specific configuration files."""
        # pyproject.toml
        pyproject = {
            "build-system": {
                "requires": ["setuptools>=61.0", "wheel"],
                "build-backend": "setuptools.build_meta"
            },
            "project": {
                "name": config.name,
                "version": "1.0.0",
                "description": config.description,
                "authors": [{"name": "Generated by MCP Server Creation System"}],
                "dependencies": config.python_dependencies,
                "requires-python": ">=3.8",
                "scripts": {
                    config.name: f"{config.name.replace('-', '_')}_server:main"
                }
            }
        }
        
        with open(server_dir / "pyproject.toml", 'w') as f:
            import tomli_w
            tomli_w.dump(pyproject, f)
        
        # requirements.txt
        with open(server_dir / "requirements.txt", 'w') as f:
            for dep in config.python_dependencies:
                f.write(f"{dep}\n")
    
    def _generate_typescript_config(self, config: ServerConfig, server_dir: Path):
        """Generate TypeScript/Node.js configuration files."""
        # package.json
        package_json = {
            "name": config.name,
            "version": "1.0.0",
            "description": config.description,
            "type": "module",
            "main": f"{config.name}.js",
            "bin": {
                config.name: f"./{config.name}.js"
            },
            "scripts": {
                "build": "tsc",
                "start": f"node {config.name}.js",
                "dev": f"tsx {config.name}.ts"
            },
            "dependencies": dict.fromkeys(config.typescript_dependencies, "latest"),
            "devDependencies": {
                "typescript": "^5.0.0",
                "tsx": "^4.0.0",
                "@types/node": "^20.0.0"
            },
            "engines": {
                "node": ">=18.0.0"
            }
        }
        
        with open(server_dir / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "ESNext",
                "moduleResolution": "bundler",
                "allowSyntheticDefaultImports": True,
                "esModuleInterop": True,
                "allowJs": True,
                "strict": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "outDir": "./dist"
            },
            "include": ["*.ts"],
            "exclude": ["node_modules", "dist"]
        }
        
        with open(server_dir / "tsconfig.json", 'w') as f:
            json.dump(tsconfig, f, indent=2)
    
    def _generate_docker_files(self, config: ServerConfig, server_dir: Path):
        """Generate Docker configuration files."""
        if config.language == "python":
            dockerfile = f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "{config.name.replace('-', '_')}_server.py"]
"""
        else:  # typescript
            dockerfile = f"""FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 8000

CMD ["npm", "start"]
"""
        
        with open(server_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile)
        
        # Docker Compose
        docker_compose = f"""version: '3.8'

services:
  {config.name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./config:/app/config:ro
"""
        
        with open(server_dir / "docker-compose.yml", 'w') as f:
            f.write(docker_compose)
    
    def _generate_test_files(self, config: ServerConfig, server_dir: Path):
        """Generate test files for the server."""
        test_dir = server_dir / "tests"
        test_dir.mkdir(exist_ok=True)
        
        if config.language == "python":
            self._generate_python_tests(config, test_dir)
        else:
            self._generate_typescript_tests(config, test_dir)
    
    def _generate_python_tests(self, config: ServerConfig, test_dir: Path):
        """Generate Python test files."""
        test_content = f'''import pytest
import asyncio
from {config.name.replace("-", "_")}_server import {self._to_class_name(config.name)}

@pytest.fixture
async def server():
    """Create a test server instance."""
    return {self._to_class_name(config.name)}()

@pytest.mark.asyncio
async def test_server_initialization(server):
    """Test server initializes correctly."""
    assert server is not None
    health = await server.health_check()
    assert health["status"] == "healthy"

@pytest.mark.asyncio  
async def test_config_validation(server):
    """Test configuration validation."""
    assert server.validate_config() == True

# Add specific tests for your tools, resources, and prompts
'''
        
        with open(test_dir / f"test_{config.name.replace('-', '_')}_server.py", 'w') as f:
            f.write(test_content)
    
    def _generate_typescript_tests(self, config: ServerConfig, test_dir: Path):
        """Generate TypeScript test files."""
        test_content = f'''import {{ describe, it, expect, beforeEach }} from 'vitest';
import {{ {self._to_class_name(config.name)} }} from '../{config.name}.js';

describe('{self._to_class_name(config.name)}', () => {{
  let server: {self._to_class_name(config.name)};

  beforeEach(() => {{
    server = new {self._to_class_name(config.name)}();
  }});

  it('should initialize correctly', async () => {{
    expect(server).toBeDefined();
    const health = await server.healthCheck();
    expect(health.status).toBe('healthy');
  }});

  // Add specific tests for your tools, resources, and prompts
}});
'''
        
        with open(test_dir / f"{config.name}.test.ts", 'w') as f:
            f.write(test_content)
    
    def _generate_documentation(self, config: ServerConfig, server_dir: Path):
        """Generate documentation files."""
        readme_content = f"""# {config.name}

{config.description}

## Overview

This MCP server provides:
{'- **Tools**: ' + ', '.join(tool['name'] for tool in config.tools) if config.tools else ''}
{'- **Resources**: ' + ', '.join(res['name'] for res in config.resources) if config.resources else ''}
{'- **Prompts**: ' + ', '.join(prompt['name'] for prompt in config.prompts) if config.prompts else ''}

## Installation

### Python
```bash
pip install -r requirements.txt
```

### Node.js/TypeScript
```bash
npm install
npm run build
```

## Configuration

Required configuration keys:
{chr(10).join(f'- `{key}`' for key in config.required_config)}

## Usage

### Running the Server
```bash
# Python
python {config.name.replace('-', '_')}_server.py

# TypeScript
npm start
```

### With Configuration File
```bash
# Python
python {config.name.replace('-', '_')}_server.py --config config.json

# TypeScript  
npm start -- --config config.json
```

## API Reference

### Tools
{chr(10).join(f"- **{tool['name']}**: {tool.get('description', 'No description')}" for tool in config.tools)}

### Resources
{chr(10).join(f"- **{res['name']}**: {res.get('description', 'No description')}" for res in config.resources)}

### Prompts
{chr(10).join(f"- **{prompt['name']}**: {prompt.get('description', 'No description')}" for prompt in config.prompts)}

## Docker

```bash
docker build -t {config.name} .
docker run -p 8000:8000 {config.name}
```

## Testing

```bash
# Python
pytest tests/

# TypeScript
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
"""
        
        with open(server_dir / "README.md", 'w') as f:
            f.write(readme_content)
    
    def _generate_tools_list_python(self, tools: List[Dict[str, Any]]) -> str:
        """Generate Python tools list code."""
        if not tools:
            return ""
        
        tool_definitions = []
        for tool in tools:
            tool_def = f"""types.Tool(
                    name="{tool['name']}",
                    description="{tool.get('description', '')}",
                    inputSchema={json.dumps(tool.get('inputSchema', {}))}
                )"""
            tool_definitions.append(tool_def)
        
        return ",\n                ".join(tool_definitions)
    
    def _generate_tool_handlers_python(self, tools: List[Dict[str, Any]]) -> str:
        """Generate Python tool handler code."""
        if not tools:
            return 'pass'
        
        handlers = []
        for i, tool in enumerate(tools):
            if_statement = "if" if i == 0 else "elif"
            handler = f"""{if_statement} name == "{tool['name']}":
                    return await self.{tool['name'].replace('-', '_')}(**arguments or {{}})"""
            handlers.append(handler)
        
        return "\n                ".join(handlers)
    
    def _generate_resources_list_python(self, resources: List[Dict[str, Any]]) -> str:
        """Generate Python resources list code."""
        if not resources:
            return ""
        
        resource_definitions = []
        for resource in resources:
            resource_def = f"""types.Resource(
                    uri="{resource.get('uri', resource['name'])}",
                    name="{resource['name']}",
                    description="{resource.get('description', '')}",
                    mimeType="{resource.get('mimeType', 'text/plain')}"
                )"""
            resource_definitions.append(resource_def)
        
        return ",\n                ".join(resource_definitions)
    
    def _generate_resource_handlers_python(self, resources: List[Dict[str, Any]]) -> str:
        """Generate Python resource handler code.""" 
        if not resources:
            return 'pass'
        
        handlers = []
        for i, resource in enumerate(resources):
            if_statement = "if" if i == 0 else "elif"
            uri_pattern = resource.get('uri', resource['name'])
            method_name = f"read_{resource['name'].replace('-', '_')}"
            handler = f"""{if_statement} uri.startswith("{uri_pattern}"):
                    return await self.{method_name}(uri)"""
            handlers.append(handler)
        
        return "\n                ".join(handlers)
    
    def _generate_prompts_list_python(self, prompts: List[Dict[str, Any]]) -> str:
        """Generate Python prompts list code."""
        if not prompts:
            return ""
        
        prompt_definitions = []
        for prompt in prompts:
            prompt_def = f"""types.Prompt(
                    name="{prompt['name']}",
                    description="{prompt.get('description', '')}",
                    arguments={json.dumps(prompt.get('arguments', []))}
                )"""
            prompt_definitions.append(prompt_def)
        
        return ",\n                ".join(prompt_definitions)
    
    def _generate_prompt_handlers_python(self, prompts: List[Dict[str, Any]]) -> str:
        """Generate Python prompt handler code."""
        if not prompts:
            return 'pass'
        
        handlers = []
        for i, prompt in enumerate(prompts):
            if_statement = "if" if i == 0 else "elif"
            method_name = f"get_{prompt['name'].replace('-', '_')}_prompt"
            handler = f"""{if_statement} name == "{prompt['name']}":
                    return await self.{method_name}(arguments or {{}})"""
            handlers.append(handler)
        
        return "\n                ".join(handlers)
    
    def _generate_tools_list_typescript(self, tools: List[Dict[str, Any]]) -> str:
        """Generate TypeScript tools list code."""
        if not tools:
            return ""
        
        tool_definitions = []
        for tool in tools:
            tool_def = f"""{{
          name: '{tool['name']}',
          description: '{tool.get('description', '')}',
          inputSchema: {json.dumps(tool.get('inputSchema', {}))}
        }}"""
            tool_definitions.append(tool_def)
        
        return ",\n        ".join(tool_definitions)
    
    def _generate_tool_handlers_typescript(self, tools: List[Dict[str, Any]]) -> str:
        """Generate TypeScript tool handler code."""
        if not tools:
            return 'break;'
        
        handlers = []
        for tool in tools:
            method_name = self._to_camel_case(tool['name'])
            handler = f"""if (name === '{tool['name']}') {{
          return await this.{method_name}(args || {{}});
        }}"""
            handlers.append(handler)
        
        return "\n        ".join(handlers)
    
    def _generate_resources_list_typescript(self, resources: List[Dict[str, Any]]) -> str:
        """Generate TypeScript resources list code."""
        if not resources:
            return ""
        
        resource_definitions = []
        for resource in resources:
            resource_def = f"""{{
          uri: '{resource.get('uri', resource['name'])}',
          name: '{resource['name']}',
          description: '{resource.get('description', '')}',
          mimeType: '{resource.get('mimeType', 'text/plain')}'
        }}"""
            resource_definitions.append(resource_def)
        
        return ",\n        ".join(resource_definitions)
    
    def _generate_resource_handlers_typescript(self, resources: List[Dict[str, Any]]) -> str:
        """Generate TypeScript resource handler code."""
        if not resources:
            return 'break;'
        
        handlers = []
        for resource in resources:
            uri_pattern = resource.get('uri', resource['name'])
            method_name = f"read{self._to_pascal_case(resource['name'])}"
            handler = f"""if (uri.startsWith('{uri_pattern}')) {{
          return await this.{method_name}(uri);
        }}"""
            handlers.append(handler)
        
        return "\n        ".join(handlers)
    
    def _generate_prompts_list_typescript(self, prompts: List[Dict[str, Any]]) -> str:
        """Generate TypeScript prompts list code."""
        if not prompts:
            return ""
        
        prompt_definitions = []
        for prompt in prompts:
            prompt_def = f"""{{
          name: '{prompt['name']}',
          description: '{prompt.get('description', '')}',
          arguments: {json.dumps(prompt.get('arguments', []))}
        }}"""
            prompt_definitions.append(prompt_def)
        
        return ",\n        ".join(prompt_definitions)
    
    def _generate_prompt_handlers_typescript(self, prompts: List[Dict[str, Any]]) -> str:
        """Generate TypeScript prompt handler code."""
        if not prompts:
            return 'break;'
        
        handlers = []
        for prompt in prompts:
            method_name = f"get{self._to_pascal_case(prompt['name'])}Prompt"
            handler = f"""if (name === '{prompt['name']}') {{
          return await this.{method_name}(args || {{}});
        }}"""
            handlers.append(handler)
        
        return "\n        ".join(handlers)
    
    def _to_class_name(self, name: str) -> str:
        """Convert kebab-case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('-'))
    
    def _to_camel_case(self, name: str) -> str:
        """Convert kebab-case to camelCase.""" 
        words = name.split('-')
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert kebab-case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('-'))

def create_server_from_category(name: str, category: str, language: str = "python") -> ServerConfig:
    """Create a server configuration from a predefined category."""
    generator = ServerGenerator()
    category_config = generator.categories.get(category, {})
    
    if not category_config:
        raise ValueError(f"Unknown category: {category}")
    
    tools = []
    for tool_name in category_config.get('common_tools', []):
        tools.append({
            'name': tool_name.replace('_', '-'),
            'description': f"{tool_name.replace('_', ' ').title()} operation",
            'inputSchema': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        })
    
    return ServerConfig(
        name=name,
        description=category_config['description'],
        language=language,
        category=category,
        has_tools=category_config.get('has_tools', True),
        has_resources=category_config.get('has_resources', False),
        has_prompts=category_config.get('has_prompts', False),
        tools=tools,
        python_dependencies=category_config.get('python_dependencies', ['mcp']),
        typescript_dependencies=category_config.get('typescript_dependencies', ['@modelcontextprotocol/sdk'])
    )

if __name__ == "__main__":
    # Example usage
    config = create_server_from_category("example-api-server", "api_integration", "python")
    generator = ServerGenerator()
    output_path = generator.generate_server(config)
    print(f"Generated server at: {output_path}")