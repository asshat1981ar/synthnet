#!/usr/bin/env python3
"""
MCP Server Code Generation System
Automates the creation of complete MCP servers with boilerplate code.
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import logging
from datetime import datetime
import re

from server_generator import ServerConfig, ServerGenerator

logger = logging.getLogger(__name__)

@dataclass
class ToolSchema:
    """Schema definition for MCP tools."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    implementation_template: str
    required_imports: List[str] = field(default_factory=list)
    error_handling: Dict[str, str] = field(default_factory=dict)

@dataclass
class ResourceSchema:
    """Schema definition for MCP resources."""
    name: str
    uri_pattern: str
    description: str
    mime_type: str
    implementation_template: str
    required_imports: List[str] = field(default_factory=list)

@dataclass
class PromptSchema:
    """Schema definition for MCP prompts."""
    name: str
    description: str
    arguments: List[Dict[str, Any]]
    template: str
    implementation_template: str

class CodeGenerator:
    """Generates production-ready code for MCP servers."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = Path(templates_dir) if templates_dir else self.base_dir / "generators" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Load code generation templates
        self.tool_templates = self.load_tool_templates()
        self.resource_templates = self.load_resource_templates()
        self.prompt_templates = self.load_prompt_templates()
        
        self.server_generator = ServerGenerator()
    
    def load_tool_templates(self) -> Dict[str, ToolSchema]:
        """Load tool implementation templates."""
        return {
            "api_get": ToolSchema(
                name="api-get",
                description="Make GET request to API endpoint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string", "description": "API endpoint URL"},
                        "headers": {"type": "object", "description": "Optional headers"},
                        "params": {"type": "object", "description": "Query parameters"}
                    },
                    "required": ["endpoint"]
                },
                implementation_template="""
async def api_get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> List[types.TextContent]:
    \"\"\"Make GET request to API endpoint.\"\"\"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                headers=headers or {},
                params=params or {}
            )
            response.raise_for_status()
            
            result = response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
            )]
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        return [types.TextContent(
            type="text",
            text=f"HTTP Error {e.response.status_code}: {e.response.text}"
        )]
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return [types.TextContent(
            type="text", 
            text=f"Request failed: {str(e)}"
        )]
""",
                required_imports=["httpx", "json"],
                error_handling={
                    "http_error": "Handle HTTP status errors with detailed response",
                    "network_error": "Handle network connectivity issues",
                    "timeout_error": "Handle request timeouts"
                }
            ),
            
            "api_post": ToolSchema(
                name="api-post",
                description="Make POST request to API endpoint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string", "description": "API endpoint URL"},
                        "data": {"type": "object", "description": "Request body data"},
                        "headers": {"type": "object", "description": "Optional headers"}
                    },
                    "required": ["endpoint", "data"]
                },
                implementation_template="""
async def api_post(self, endpoint: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> List[types.TextContent]:
    \"\"\"Make POST request to API endpoint.\"\"\"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=data,
                headers={**{'Content-Type': 'application/json'}, **(headers or {})}
            )
            response.raise_for_status()
            
            result = response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
            )]
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        return [types.TextContent(
            type="text",
            text=f"HTTP Error {e.response.status_code}: {e.response.text}"
        )]
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Request failed: {str(e)}"
        )]
""",
                required_imports=["httpx", "json"]
            ),
            
            "database_query": ToolSchema(
                name="database-query",
                description="Execute database query",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to execute"},
                        "params": {"type": "array", "description": "Query parameters"}
                    },
                    "required": ["query"]
                },
                implementation_template="""
async def database_query(self, query: str, params: Optional[List[Any]] = None) -> List[types.TextContent]:
    \"\"\"Execute database query.\"\"\"
    try:
        async with self.db_pool.acquire() as conn:
            result = await conn.fetch(query, *(params or []))
            
            # Convert result to JSON-serializable format
            data = []
            for row in result:
                data.append(dict(row))
            
            return [types.TextContent(
                type="text",
                text=json.dumps(data, indent=2, default=str)
            )]
            
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Database error: {str(e)}"
        )]
""",
                required_imports=["asyncpg", "json"]
            ),
            
            "file_read": ToolSchema(
                name="file-read",
                description="Read file content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"},
                        "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                    },
                    "required": ["path"]
                },
                implementation_template="""
async def file_read(self, path: str, encoding: str = "utf-8") -> List[types.TextContent]:
    \"\"\"Read file content.\"\"\"
    try:
        # Security check - prevent directory traversal
        if ".." in path or path.startswith("/"):
            raise ValueError("Invalid file path")
        
        file_path = Path(self.config.get('base_path', '.')) / path
        
        async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
            content = await f.read()
        
        return [types.TextContent(
            type="text",
            text=content
        )]
        
    except FileNotFoundError:
        return [types.TextContent(
            type="text",
            text=f"File not found: {path}"
        )]
    except PermissionError:
        return [types.TextContent(
            type="text",
            text=f"Permission denied: {path}"
        )]
    except Exception as e:
        logger.error(f"File read error: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error reading file: {str(e)}"
        )]
""",
                required_imports=["aiofiles", "pathlib.Path"]
            ),
            
            "web_scrape": ToolSchema(
                name="web-scrape",
                description="Scrape web page content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape"},
                        "selector": {"type": "string", "description": "CSS selector for content extraction"},
                        "timeout": {"type": "number", "description": "Request timeout in seconds", "default": 30}
                    },
                    "required": ["url"]
                },
                implementation_template="""
async def web_scrape(self, url: str, selector: Optional[str] = None, timeout: int = 30) -> List[types.TextContent]:
    \"\"\"Scrape web page content.\"\"\"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            if selector:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                elements = soup.select(selector)
                content = '\\n'.join(element.get_text(strip=True) for element in elements)
            else:
                content = response.text
            
            return [types.TextContent(
                type="text",
                text=content
            )]
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error scraping {url}: {e.response.status_code}")
        return [types.TextContent(
            type="text",
            text=f"HTTP Error {e.response.status_code} scraping {url}"
        )]
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Scraping failed: {str(e)}"
        )]
""",
                required_imports=["httpx", "bs4.BeautifulSoup"]
            )
        }
    
    def load_resource_templates(self) -> Dict[str, ResourceSchema]:
        """Load resource implementation templates."""
        return {
            "file_resource": ResourceSchema(
                name="file-resource",
                uri_pattern="file://",
                description="File system resource access",
                mime_type="text/plain",
                implementation_template="""
async def read_file_resource(self, uri: str) -> str:
    \"\"\"Read file resource content.\"\"\"
    try:
        # Extract file path from URI
        file_path = uri.replace("file://", "")
        
        # Security check
        if ".." in file_path or file_path.startswith("/"):
            raise ValueError("Invalid file path")
        
        base_path = Path(self.config.get('base_path', '.'))
        full_path = base_path / file_path
        
        async with aiofiles.open(full_path, mode='r') as f:
            content = await f.read()
        
        return content
        
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"File resource error: {str(e)}")
        raise
""",
                required_imports=["aiofiles", "pathlib.Path"]
            ),
            
            "api_resource": ResourceSchema(
                name="api-resource", 
                uri_pattern="api://",
                description="API endpoint resource access",
                mime_type="application/json",
                implementation_template="""
async def read_api_resource(self, uri: str) -> str:
    \"\"\"Read API resource content.\"\"\"
    try:
        # Extract endpoint from URI
        endpoint = uri.replace("api://", "")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint)
            response.raise_for_status()
            
            return response.text
            
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"API resource error: {str(e)}")
        raise
""",
                required_imports=["httpx"]
            ),
            
            "database_resource": ResourceSchema(
                name="database-resource",
                uri_pattern="db://",
                description="Database table/view resource access", 
                mime_type="application/json",
                implementation_template="""
async def read_database_resource(self, uri: str) -> str:
    \"\"\"Read database resource content.\"\"\"
    try:
        # Parse URI: db://table_name or db://table_name/id
        path_parts = uri.replace("db://", "").split("/")
        table_name = path_parts[0]
        record_id = path_parts[1] if len(path_parts) > 1 else None
        
        async with self.db_pool.acquire() as conn:
            if record_id:
                query = f"SELECT * FROM {table_name} WHERE id = $1"
                result = await conn.fetchrow(query, record_id)
                data = dict(result) if result else None
            else:
                query = f"SELECT * FROM {table_name} LIMIT 100"
                result = await conn.fetch(query)
                data = [dict(row) for row in result]
            
            return json.dumps(data, indent=2, default=str)
            
    except Exception as e:
        logger.error(f"Database resource error: {str(e)}")
        raise
""",
                required_imports=["asyncpg", "json"]
            )
        }
    
    def load_prompt_templates(self) -> Dict[str, PromptSchema]:
        """Load prompt implementation templates."""
        return {
            "analysis_prompt": PromptSchema(
                name="analysis-prompt",
                description="Generate analysis prompt with context",
                arguments=[
                    {"name": "topic", "description": "Topic to analyze", "required": True},
                    {"name": "context", "description": "Additional context", "required": False}
                ],
                template="Analyze the following topic: {topic}\n\nContext: {context}",
                implementation_template="""
async def get_analysis_prompt(self, arguments: Dict[str, str]) -> types.GetPromptResult:
    \"\"\"Generate analysis prompt with context.\"\"\"
    topic = arguments.get('topic', '')
    context = arguments.get('context', 'No additional context provided')
    
    if not topic:
        raise ValueError("Topic is required for analysis prompt")
    
    prompt_text = f\"\"\"Analyze the following topic: {topic}

Context: {context}

Please provide:
1. Key insights and observations
2. Potential implications
3. Recommended actions
4. Areas for further investigation
\"\"\"
    
    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=prompt_text
            )
        )
    ]
    
    return types.GetPromptResult(messages=messages)
"""
            ),
            
            "code_review_prompt": PromptSchema(
                name="code-review-prompt",
                description="Generate code review prompt",
                arguments=[
                    {"name": "code", "description": "Code to review", "required": True},
                    {"name": "language", "description": "Programming language", "required": False}
                ],
                template="Review the following {language} code: {code}",
                implementation_template="""
async def get_code_review_prompt(self, arguments: Dict[str, str]) -> types.GetPromptResult:
    \"\"\"Generate code review prompt.\"\"\"
    code = arguments.get('code', '')
    language = arguments.get('language', 'code')
    
    if not code:
        raise ValueError("Code is required for review prompt")
    
    prompt_text = f\"\"\"Review the following {language} code for:

```{language}
{code}
```

Please evaluate:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations  
4. Security concerns
5. Maintainability and readability
6. Suggestions for improvement
\"\"\"
    
    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=prompt_text
            )
        )
    ]
    
    return types.GetPromptResult(messages=messages)
"""
            )
        }
    
    def generate_custom_server(self, server_spec: Dict[str, Any]) -> str:
        """Generate a custom MCP server from detailed specifications."""
        
        # Parse server specification
        config = self._parse_server_spec(server_spec)
        
        # Generate tools implementations
        tools = []
        for tool_spec in server_spec.get('tools', []):
            tool = self._generate_tool_from_spec(tool_spec)
            tools.append(tool)
        
        # Generate resources implementations
        resources = []
        for resource_spec in server_spec.get('resources', []):
            resource = self._generate_resource_from_spec(resource_spec)
            resources.append(resource)
        
        # Generate prompts implementations
        prompts = []
        for prompt_spec in server_spec.get('prompts', []):
            prompt = self._generate_prompt_from_spec(prompt_spec)
            prompts.append(prompt)
        
        # Update config with generated components
        config.tools = tools
        config.resources = resources
        config.prompts = prompts
        
        # Generate the complete server
        return self.server_generator.generate_server(config)
    
    def _parse_server_spec(self, spec: Dict[str, Any]) -> ServerConfig:
        """Parse server specification into ServerConfig."""
        return ServerConfig(
            name=spec['name'],
            description=spec['description'],
            language=spec.get('language', 'python'),
            category=spec.get('category', 'custom'),
            has_tools=len(spec.get('tools', [])) > 0,
            has_resources=len(spec.get('resources', [])) > 0,
            has_prompts=len(spec.get('prompts', [])) > 0,
            required_config=spec.get('required_config', []),
            api_endpoint=spec.get('api_endpoint'),
            auth_method=spec.get('auth_method'),
            python_dependencies=spec.get('python_dependencies', ['mcp']),
            typescript_dependencies=spec.get('typescript_dependencies', ['@modelcontextprotocol/sdk'])
        )
    
    def _generate_tool_from_spec(self, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tool implementation from specification."""
        tool_type = tool_spec.get('type', 'custom')
        
        if tool_type in self.tool_templates:
            template = self.tool_templates[tool_type]
            return {
                'name': tool_spec['name'],
                'description': tool_spec.get('description', template.description),
                'inputSchema': tool_spec.get('input_schema', template.input_schema),
                'implementation': template.implementation_template,
                'imports': template.required_imports
            }
        else:
            # Generate custom tool
            return {
                'name': tool_spec['name'],
                'description': tool_spec.get('description', ''),
                'inputSchema': tool_spec.get('input_schema', {'type': 'object', 'properties': {}}),
                'implementation': self._generate_custom_tool_implementation(tool_spec),
                'imports': []
            }
    
    def _generate_resource_from_spec(self, resource_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resource implementation from specification."""
        resource_type = resource_spec.get('type', 'custom')
        
        if resource_type in self.resource_templates:
            template = self.resource_templates[resource_type]
            return {
                'name': resource_spec['name'],
                'uri': resource_spec.get('uri', template.uri_pattern + resource_spec['name']),
                'description': resource_spec.get('description', template.description),
                'mimeType': resource_spec.get('mime_type', template.mime_type),
                'implementation': template.implementation_template,
                'imports': template.required_imports
            }
        else:
            # Generate custom resource
            return {
                'name': resource_spec['name'],
                'uri': resource_spec.get('uri', f"resource://{resource_spec['name']}"),
                'description': resource_spec.get('description', ''),
                'mimeType': resource_spec.get('mime_type', 'text/plain'),
                'implementation': self._generate_custom_resource_implementation(resource_spec),
                'imports': []
            }
    
    def _generate_prompt_from_spec(self, prompt_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate prompt implementation from specification."""
        prompt_type = prompt_spec.get('type', 'custom')
        
        if prompt_type in self.prompt_templates:
            template = self.prompt_templates[prompt_type]
            return {
                'name': prompt_spec['name'],
                'description': prompt_spec.get('description', template.description),
                'arguments': prompt_spec.get('arguments', template.arguments),
                'implementation': template.implementation_template
            }
        else:
            # Generate custom prompt
            return {
                'name': prompt_spec['name'],
                'description': prompt_spec.get('description', ''),
                'arguments': prompt_spec.get('arguments', []),
                'implementation': self._generate_custom_prompt_implementation(prompt_spec)
            }
    
    def _generate_custom_tool_implementation(self, tool_spec: Dict[str, Any]) -> str:
        """Generate custom tool implementation."""
        method_name = tool_spec['name'].replace('-', '_')
        
        return f"""
async def {method_name}(self, **kwargs) -> List[types.TextContent]:
    \"\"\"Custom tool implementation for {tool_spec['name']}.\"\"\"
    try:
        # TODO: Implement custom logic for {tool_spec['name']}
        result = "Custom tool result"
        
        return [types.TextContent(
            type="text",
            text=str(result)
        )]
        
    except Exception as e:
        logger.error(f"Error in {method_name}: {{str(e)}}")
        return [types.TextContent(
            type="text",
            text=f"Error: {{str(e)}}"
        )]
"""
    
    def _generate_custom_resource_implementation(self, resource_spec: Dict[str, Any]) -> str:
        """Generate custom resource implementation."""
        method_name = f"read_{resource_spec['name'].replace('-', '_')}"
        
        return f"""
async def {method_name}(self, uri: str) -> str:
    \"\"\"Custom resource implementation for {resource_spec['name']}.\"\"\"
    try:
        # TODO: Implement custom logic for {resource_spec['name']} resource
        content = "Custom resource content"
        
        return content
        
    except Exception as e:
        logger.error(f"Error reading resource: {{str(e)}}")
        raise
"""
    
    def _generate_custom_prompt_implementation(self, prompt_spec: Dict[str, Any]) -> str:
        """Generate custom prompt implementation."""
        method_name = f"get_{prompt_spec['name'].replace('-', '_')}_prompt"
        
        return f"""
async def {method_name}(self, arguments: Dict[str, str]) -> types.GetPromptResult:
    \"\"\"Custom prompt implementation for {prompt_spec['name']}.\"\"\"
    
    # TODO: Implement custom prompt logic
    prompt_text = "Custom prompt content"
    
    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=prompt_text
            )
        )
    ]
    
    return types.GetPromptResult(messages=messages)
"""
    
    def generate_server_from_openapi(self, openapi_spec: Dict[str, Any], server_name: str) -> str:
        """Generate MCP server from OpenAPI specification."""
        
        # Parse OpenAPI spec
        paths = openapi_spec.get('paths', {})
        server_info = openapi_spec.get('info', {})
        
        # Create server specification
        server_spec = {
            'name': server_name,
            'description': server_info.get('description', f'Generated from OpenAPI spec for {server_name}'),
            'language': 'python',
            'category': 'api_integration',
            'tools': [],
            'resources': [],
            'required_config': ['api_base_url']
        }
        
        # Generate tools from OpenAPI paths
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE']:
                    tool_name = f"{method.lower()}{path.replace('/', '-').replace('{', '').replace('}', '')}"
                    
                    # Generate input schema from parameters
                    input_schema = {'type': 'object', 'properties': {}, 'required': []}
                    
                    for param in operation.get('parameters', []):
                        prop_name = param['name']
                        input_schema['properties'][prop_name] = {
                            'type': 'string',  # Simplify for now
                            'description': param.get('description', '')
                        }
                        if param.get('required', False):
                            input_schema['required'].append(prop_name)
                    
                    tool_spec = {
                        'name': tool_name,
                        'description': operation.get('summary', f'{method.upper()} {path}'),
                        'type': 'api_get' if method.upper() == 'GET' else 'api_post',
                        'input_schema': input_schema,
                        'endpoint': path
                    }
                    
                    server_spec['tools'].append(tool_spec)
        
        return self.generate_custom_server(server_spec)
    
    def create_server_cli(self):
        """Create command-line interface for server generation."""
        import argparse
        
        parser = argparse.ArgumentParser(description="Generate MCP servers from specifications")
        parser.add_argument('--spec', required=True, help="Server specification file (JSON/YAML)")
        parser.add_argument('--output', help="Output directory")
        parser.add_argument('--language', choices=['python', 'typescript'], default='python', help="Implementation language")
        
        args = parser.parse_args()
        
        # Load specification
        spec_path = Path(args.spec)
        if spec_path.suffix.lower() in ['.yaml', '.yml']:
            with open(spec_path) as f:
                spec = yaml.safe_load(f)
        else:
            with open(spec_path) as f:
                spec = json.load(f)
        
        # Override language if specified
        if args.language:
            spec['language'] = args.language
        
        # Generate server
        output_path = self.generate_custom_server(spec)
        print(f"Generated server at: {output_path}")

def create_example_server_spec() -> Dict[str, Any]:
    """Create example server specification for demonstration."""
    return {
        "name": "example-api-server",
        "description": "Example API integration server",
        "language": "python",
        "category": "api_integration",
        "required_config": ["api_key", "base_url"],
        "api_endpoint": "https://api.example.com",
        "auth_method": "api_key",
        "python_dependencies": ["mcp", "httpx", "pydantic"],
        "tools": [
            {
                "name": "get-users",
                "description": "Fetch list of users",
                "type": "api_get",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of users to fetch"},
                        "offset": {"type": "integer", "description": "Offset for pagination"}
                    }
                }
            },
            {
                "name": "create-user",
                "description": "Create a new user",
                "type": "api_post",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "User name"},
                        "email": {"type": "string", "description": "User email"}
                    },
                    "required": ["name", "email"]
                }
            }
        ],
        "resources": [
            {
                "name": "user-data",
                "description": "User data resource",
                "type": "api_resource",
                "uri": "api://users"
            }
        ],
        "prompts": [
            {
                "name": "user-analysis",
                "description": "Analyze user data",
                "type": "analysis_prompt",
                "arguments": [
                    {"name": "user_data", "description": "User data to analyze", "required": True}
                ]
            }
        ]
    }

if __name__ == "__main__":
    generator = CodeGenerator()
    
    # Generate example server
    example_spec = create_example_server_spec()
    output_path = generator.generate_custom_server(example_spec)
    print(f"Generated example server at: {output_path}")
    
    # Save example spec for reference
    spec_file = Path(__file__).parent / "example_server_spec.json"
    with open(spec_file, 'w') as f:
        json.dump(example_spec, f, indent=2)
    print(f"Example specification saved to: {spec_file}")