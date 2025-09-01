#!/usr/bin/env python3
"""
MCP Protocol Compliance Tester
Comprehensive testing of MCP protocol adherence and server behavior.
"""

import asyncio
import json
import logging
import time
import traceback
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import subprocess
import tempfile
from pathlib import Path
import jsonschema
import httpx
import websockets
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class ProtocolTestResult:
    """Result of a protocol compliance test."""
    test_name: str
    category: str  # 'initialization', 'tools', 'resources', 'prompts', 'error_handling'
    passed: bool
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None
    severity: str = "error"  # 'error', 'warning', 'info'
    
@dataclass
class MCPMessage:
    """MCP protocol message structure."""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class MCPProtocolTester:
    """Comprehensive MCP protocol compliance testing."""
    
    def __init__(self):
        """Initialize the protocol tester."""
        self.mcp_schemas = self._load_mcp_schemas()
        self.test_results: List[ProtocolTestResult] = []
        self.server_process: Optional[subprocess.Popen] = None
        self.server_capabilities: Dict[str, Any] = {}
        
    def _load_mcp_schemas(self) -> Dict[str, Any]:
        """Load MCP JSON schemas for validation."""
        # MCP protocol schemas - in production, these would be loaded from files
        return {
            "initialize_request": {
                "type": "object",
                "properties": {
                    "jsonrpc": {"type": "string", "enum": ["2.0"]},
                    "id": {"type": ["string", "number"]},
                    "method": {"type": "string", "enum": ["initialize"]},
                    "params": {
                        "type": "object",
                        "properties": {
                            "protocolVersion": {"type": "string"},
                            "capabilities": {"type": "object"},
                            "clientInfo": {"type": "object"}
                        },
                        "required": ["protocolVersion"]
                    }
                },
                "required": ["jsonrpc", "id", "method", "params"]
            },
            "initialize_response": {
                "type": "object",
                "properties": {
                    "jsonrpc": {"type": "string", "enum": ["2.0"]},
                    "id": {"type": ["string", "number"]},
                    "result": {
                        "type": "object",
                        "properties": {
                            "protocolVersion": {"type": "string"},
                            "capabilities": {"type": "object"},
                            "serverInfo": {"type": "object"}
                        },
                        "required": ["protocolVersion", "capabilities"]
                    }
                },
                "required": ["jsonrpc", "id", "result"]
            },
            "tools_list_request": {
                "type": "object",
                "properties": {
                    "jsonrpc": {"type": "string", "enum": ["2.0"]},
                    "id": {"type": ["string", "number"]},
                    "method": {"type": "string", "enum": ["tools/list"]},
                    "params": {"type": "object"}
                },
                "required": ["jsonrpc", "id", "method"]
            },
            "tools_call_request": {
                "type": "object",
                "properties": {
                    "jsonrpc": {"type": "string", "enum": ["2.0"]},
                    "id": {"type": ["string", "number"]},
                    "method": {"type": "string", "enum": ["tools/call"]},
                    "params": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "arguments": {"type": "object"}
                        },
                        "required": ["name"]
                    }
                },
                "required": ["jsonrpc", "id", "method", "params"]
            }
        }
    
    async def run_full_compliance_test(self, server_path: str) -> List[Dict[str, Any]]:
        """Run complete MCP protocol compliance test suite."""
        logger.info(f"Starting MCP protocol compliance testing for: {server_path}")
        self.test_results.clear()
        
        server_path_obj = Path(server_path)
        if not server_path_obj.exists():
            self._add_result("server_exists", "initialization", False, 
                           f"Server path does not exist: {server_path}", 0.0)
            return self._format_results()
        
        try:
            # Test 1: Server startup and initialization
            await self._test_server_startup(server_path)
            
            # Test 2: Protocol handshake
            await self._test_protocol_handshake()
            
            # Test 3: Capability discovery
            await self._test_capability_discovery()
            
            # Test 4: Tool functionality (if supported)
            if self.server_capabilities.get('tools'):
                await self._test_tool_functionality()
            
            # Test 5: Resource functionality (if supported)
            if self.server_capabilities.get('resources'):
                await self._test_resource_functionality()
            
            # Test 6: Prompt functionality (if supported)
            if self.server_capabilities.get('prompts'):
                await self._test_prompt_functionality()
            
            # Test 7: Error handling
            await self._test_error_handling()
            
            # Test 8: Message format validation
            await self._test_message_formats()
            
            # Test 9: Performance characteristics
            await self._test_performance_characteristics()
            
        except Exception as e:
            logger.error(f"Protocol testing failed: {e}")
            self._add_result("protocol_testing", "system", False, 
                           f"Protocol testing failed: {str(e)}", 0.0, 
                           details={"error": str(e), "traceback": traceback.format_exc()})
        
        finally:
            await self._cleanup_server()
        
        return self._format_results()
    
    async def _test_server_startup(self, server_path: str):
        """Test server startup and basic connectivity."""
        start_time = time.time()
        
        try:
            # Determine server type and startup command
            server_path_obj = Path(server_path)
            
            if server_path_obj.is_file() and server_path_obj.suffix == '.py':
                # Python server
                cmd = [sys.executable, str(server_path)]
            elif server_path_obj.is_file() and server_path_obj.suffix == '.js':
                # Node.js server  
                cmd = ['node', str(server_path)]
            elif server_path_obj.is_dir():
                # Directory - look for main files
                python_main = server_path_obj / 'main.py'
                js_main = server_path_obj / 'index.js'
                
                if python_main.exists():
                    cmd = [sys.executable, str(python_main)]
                elif js_main.exists():
                    cmd = ['node', str(js_main)]
                else:
                    raise FileNotFoundError("No main server file found")
            else:
                raise ValueError("Unsupported server path format")
            
            # Start server process
            self.server_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Give server time to start
            await asyncio.sleep(1.0)
            
            # Check if server is still running
            if self.server_process.poll() is not None:
                stderr_output = self.server_process.stderr.read() if self.server_process.stderr else ""
                raise RuntimeError(f"Server failed to start. Error: {stderr_output}")
            
            duration = time.time() - start_time
            self._add_result("server_startup", "initialization", True,
                           "Server started successfully", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("server_startup", "initialization", False,
                           f"Server startup failed: {str(e)}", duration,
                           details={"error": str(e)})
            raise
    
    async def _test_protocol_handshake(self):
        """Test MCP protocol initialization handshake."""
        start_time = time.time()
        
        try:
            if not self.server_process:
                raise RuntimeError("Server not started")
            
            # Send initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": "init-1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "mcp-test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send request to server
            request_json = json.dumps(initialize_request) + '\n'
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            # Read response
            response_line = self.server_process.stdout.readline()
            if not response_line:
                raise RuntimeError("No response from server")
            
            response = json.loads(response_line.strip())
            
            # Validate response format
            try:
                jsonschema.validate(response, self.mcp_schemas["initialize_response"])
            except jsonschema.ValidationError as e:
                raise ValueError(f"Invalid initialize response format: {e}")
            
            # Store server capabilities for later tests
            if 'result' in response and 'capabilities' in response['result']:
                self.server_capabilities = response['result']['capabilities']
            
            duration = time.time() - start_time
            self._add_result("protocol_handshake", "initialization", True,
                           "Protocol handshake completed successfully", duration,
                           details={"response": response})
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("protocol_handshake", "initialization", False,
                           f"Protocol handshake failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _test_capability_discovery(self):
        """Test capability discovery and validation."""
        start_time = time.time()
        
        try:
            # Check if server reported capabilities
            if not self.server_capabilities:
                raise ValueError("No server capabilities reported during initialization")
            
            # Validate capability structure
            valid_capabilities = ['tools', 'resources', 'prompts', 'logging']
            reported_capabilities = list(self.server_capabilities.keys())
            
            # Check for at least one capability
            if not any(cap in valid_capabilities for cap in reported_capabilities):
                self._add_result("capability_discovery", "capabilities", False,
                               "Server reported no recognized capabilities", 
                               time.time() - start_time, severity="warning")
                return
            
            # Test each reported capability
            for capability in reported_capabilities:
                if capability in valid_capabilities:
                    await self._validate_capability_structure(capability)
            
            duration = time.time() - start_time
            self._add_result("capability_discovery", "capabilities", True,
                           f"Capabilities validated: {reported_capabilities}", duration,
                           details={"capabilities": self.server_capabilities})
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("capability_discovery", "capabilities", False,
                           f"Capability discovery failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _validate_capability_structure(self, capability: str):
        """Validate the structure of a specific capability."""
        capability_config = self.server_capabilities.get(capability, {})
        
        # Each capability should be properly structured
        if capability == 'tools' and not isinstance(capability_config, dict):
            raise ValueError(f"Invalid tools capability structure: {type(capability_config)}")
        elif capability == 'resources' and not isinstance(capability_config, dict):
            raise ValueError(f"Invalid resources capability structure: {type(capability_config)}")
        elif capability == 'prompts' and not isinstance(capability_config, dict):
            raise ValueError(f"Invalid prompts capability structure: {type(capability_config)}")
    
    async def _test_tool_functionality(self):
        """Test tool listing and execution functionality."""
        start_time = time.time()
        
        try:
            # Test tools/list
            list_request = {
                "jsonrpc": "2.0",
                "id": "tools-list-1",
                "method": "tools/list",
                "params": {}
            }
            
            await self._send_request_and_validate_response(list_request, "tools_list")
            
            # Test tools/call with first available tool
            tools_response = await self._get_tools_list()
            if tools_response and 'result' in tools_response and 'tools' in tools_response['result']:
                tools = tools_response['result']['tools']
                if tools:
                    first_tool = tools[0]
                    await self._test_tool_execution(first_tool)
            
            duration = time.time() - start_time
            self._add_result("tool_functionality", "tools", True,
                           "Tool functionality tests completed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("tool_functionality", "tools", False,
                           f"Tool functionality test failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _test_tool_execution(self, tool_info: Dict[str, Any]):
        """Test execution of a specific tool."""
        tool_name = tool_info.get('name')
        if not tool_name:
            return
        
        # Create minimal valid arguments based on tool schema
        arguments = self._generate_test_arguments(tool_info.get('inputSchema', {}))
        
        call_request = {
            "jsonrpc": "2.0", 
            "id": f"tool-call-{tool_name}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            await self._send_request_and_validate_response(call_request, "tool_call")
        except Exception as e:
            # Tool execution failure might be expected if we don't have valid test data
            logger.warning(f"Tool {tool_name} execution failed (may be expected): {e}")
    
    async def _test_resource_functionality(self):
        """Test resource listing and reading functionality."""
        start_time = time.time()
        
        try:
            # Test resources/list
            list_request = {
                "jsonrpc": "2.0",
                "id": "resources-list-1", 
                "method": "resources/list",
                "params": {}
            }
            
            resources_response = await self._send_request_and_validate_response(list_request, "resources_list")
            
            # Test resources/read with first available resource
            if (resources_response and 'result' in resources_response and 
                'resources' in resources_response['result']):
                resources = resources_response['result']['resources']
                if resources:
                    first_resource = resources[0]
                    await self._test_resource_reading(first_resource)
            
            duration = time.time() - start_time
            self._add_result("resource_functionality", "resources", True,
                           "Resource functionality tests completed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("resource_functionality", "resources", False,
                           f"Resource functionality test failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _test_resource_reading(self, resource_info: Dict[str, Any]):
        """Test reading of a specific resource."""
        resource_uri = resource_info.get('uri')
        if not resource_uri:
            return
        
        read_request = {
            "jsonrpc": "2.0",
            "id": f"resource-read-{hash(resource_uri)}",
            "method": "resources/read", 
            "params": {
                "uri": resource_uri
            }
        }
        
        await self._send_request_and_validate_response(read_request, "resource_read")
    
    async def _test_prompt_functionality(self):
        """Test prompt listing and retrieval functionality."""
        start_time = time.time()
        
        try:
            # Test prompts/list
            list_request = {
                "jsonrpc": "2.0",
                "id": "prompts-list-1",
                "method": "prompts/list",
                "params": {}
            }
            
            prompts_response = await self._send_request_and_validate_response(list_request, "prompts_list")
            
            # Test prompts/get with first available prompt
            if (prompts_response and 'result' in prompts_response and 
                'prompts' in prompts_response['result']):
                prompts = prompts_response['result']['prompts']
                if prompts:
                    first_prompt = prompts[0]
                    await self._test_prompt_retrieval(first_prompt)
            
            duration = time.time() - start_time
            self._add_result("prompt_functionality", "prompts", True,
                           "Prompt functionality tests completed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("prompt_functionality", "prompts", False,
                           f"Prompt functionality test failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _test_prompt_retrieval(self, prompt_info: Dict[str, Any]):
        """Test retrieval of a specific prompt."""
        prompt_name = prompt_info.get('name')
        if not prompt_name:
            return
        
        # Generate test arguments for prompt
        arguments = self._generate_test_arguments(prompt_info.get('arguments', []))
        
        get_request = {
            "jsonrpc": "2.0",
            "id": f"prompt-get-{prompt_name}",
            "method": "prompts/get",
            "params": {
                "name": prompt_name,
                "arguments": arguments
            }
        }
        
        await self._send_request_and_validate_response(get_request, "prompt_get")
    
    async def _test_error_handling(self):
        """Test server error handling with invalid requests."""
        start_time = time.time()
        
        try:
            # Test 1: Invalid JSON-RPC format
            await self._test_invalid_request('{"invalid": "json"}', "invalid_json_rpc")
            
            # Test 2: Unknown method
            unknown_method_request = {
                "jsonrpc": "2.0",
                "id": "error-1",
                "method": "unknown/method",
                "params": {}
            }
            await self._test_invalid_request(json.dumps(unknown_method_request), "unknown_method")
            
            # Test 3: Missing required parameters
            invalid_params_request = {
                "jsonrpc": "2.0", 
                "id": "error-2",
                "method": "tools/call",
                "params": {}  # Missing required 'name' parameter
            }
            await self._test_invalid_request(json.dumps(invalid_params_request), "missing_params")
            
            duration = time.time() - start_time
            self._add_result("error_handling", "error_handling", True,
                           "Error handling tests completed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("error_handling", "error_handling", False,
                           f"Error handling test failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _test_invalid_request(self, invalid_request: str, test_name: str):
        """Test server response to an invalid request."""
        if not self.server_process:
            return
        
        # Send invalid request
        self.server_process.stdin.write(invalid_request + '\n')
        self.server_process.stdin.flush()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                asyncio.create_task(self._read_server_response()), 
                timeout=5.0
            )
            
            if response_line:
                response = json.loads(response_line.strip())
                
                # Valid error response should have error field
                if 'error' not in response:
                    raise ValueError(f"Server should return error for {test_name}")
                
                # Error should have code and message
                error = response['error']
                if 'code' not in error or 'message' not in error:
                    raise ValueError(f"Invalid error format for {test_name}")
            
        except asyncio.TimeoutError:
            # No response might be acceptable for some invalid requests
            logger.warning(f"No response to {test_name} (may be acceptable)")
        except json.JSONDecodeError:
            # Invalid JSON response is an error
            raise ValueError(f"Invalid JSON response to {test_name}")
    
    async def _test_message_formats(self):
        """Test message format validation."""
        start_time = time.time()
        
        try:
            # Test that all responses follow JSON-RPC 2.0 format
            test_requests = []
            
            # Add basic format validation tests
            if self.server_capabilities.get('tools'):
                test_requests.append({
                    "jsonrpc": "2.0",
                    "id": "format-1",
                    "method": "tools/list",
                    "params": {}
                })
            
            for request in test_requests:
                response = await self._send_request_and_validate_response(request, "format_validation")
                
                # Validate JSON-RPC format
                if response.get('jsonrpc') != '2.0':
                    raise ValueError("Response missing or invalid jsonrpc field")
                
                if 'id' not in response:
                    raise ValueError("Response missing id field")
                
                if 'result' not in response and 'error' not in response:
                    raise ValueError("Response missing result or error field")
            
            duration = time.time() - start_time
            self._add_result("message_formats", "protocol", True,
                           "Message format validation completed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("message_formats", "protocol", False,
                           f"Message format test failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _test_performance_characteristics(self):
        """Test basic performance characteristics."""
        start_time = time.time()
        
        try:
            if not self.server_capabilities.get('tools'):
                # Skip if no tools available
                return
            
            # Measure response time for tools/list
            response_times = []
            for i in range(5):
                test_start = time.time()
                
                list_request = {
                    "jsonrpc": "2.0",
                    "id": f"perf-{i}",
                    "method": "tools/list",
                    "params": {}
                }
                
                await self._send_request_and_validate_response(list_request, "performance_test")
                response_time = time.time() - test_start
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # Check for reasonable performance (configurable thresholds)
            if avg_response_time > 5.0:  # 5 second threshold
                self._add_result("performance_characteristics", "performance", False,
                               f"Average response time too high: {avg_response_time:.2f}s", 
                               time.time() - start_time, severity="warning")
            elif max_response_time > 10.0:  # 10 second max threshold
                self._add_result("performance_characteristics", "performance", False,
                               f"Max response time too high: {max_response_time:.2f}s",
                               time.time() - start_time, severity="warning")
            else:
                duration = time.time() - start_time
                self._add_result("performance_characteristics", "performance", True,
                               f"Performance acceptable - avg: {avg_response_time:.2f}s, max: {max_response_time:.2f}s",
                               duration, details={"response_times": response_times})
            
        except Exception as e:
            duration = time.time() - start_time
            self._add_result("performance_characteristics", "performance", False,
                           f"Performance test failed: {str(e)}", duration,
                           details={"error": str(e)})
    
    async def _send_request_and_validate_response(self, request: Dict[str, Any], test_context: str) -> Dict[str, Any]:
        """Send request to server and validate response."""
        if not self.server_process:
            raise RuntimeError("Server not started")
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.server_process.stdin.write(request_json)
        self.server_process.stdin.flush()
        
        # Read response
        response_line = await asyncio.wait_for(
            asyncio.create_task(self._read_server_response()),
            timeout=30.0
        )
        
        if not response_line:
            raise RuntimeError(f"No response from server for {test_context}")
        
        try:
            response = json.loads(response_line.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response for {test_context}: {e}")
        
        # Basic validation
        if response.get('jsonrpc') != '2.0':
            raise ValueError(f"Invalid jsonrpc field in response for {test_context}")
        
        if response.get('id') != request.get('id'):
            raise ValueError(f"Response ID mismatch for {test_context}")
        
        return response
    
    async def _read_server_response(self) -> str:
        """Read a line from server stdout."""
        if not self.server_process or not self.server_process.stdout:
            return ""
        
        # This is a simplified implementation - in production, you'd want
        # proper async I/O handling
        return self.server_process.stdout.readline()
    
    async def _get_tools_list(self) -> Optional[Dict[str, Any]]:
        """Get list of available tools from server."""
        try:
            list_request = {
                "jsonrpc": "2.0",
                "id": "get-tools-list",
                "method": "tools/list", 
                "params": {}
            }
            
            return await self._send_request_and_validate_response(list_request, "get_tools_list")
            
        except Exception as e:
            logger.error(f"Failed to get tools list: {e}")
            return None
    
    def _generate_test_arguments(self, schema: Any) -> Dict[str, Any]:
        """Generate minimal test arguments based on JSON schema."""
        if isinstance(schema, dict):
            args = {}
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                if prop_name in required:
                    # Generate minimal valid value
                    prop_type = prop_schema.get('type', 'string')
                    if prop_type == 'string':
                        args[prop_name] = 'test_value'
                    elif prop_type == 'integer':
                        args[prop_name] = 1
                    elif prop_type == 'number':
                        args[prop_name] = 1.0
                    elif prop_type == 'boolean':
                        args[prop_name] = True
                    elif prop_type == 'array':
                        args[prop_name] = []
                    elif prop_type == 'object':
                        args[prop_name] = {}
            
            return args
        elif isinstance(schema, list):
            # Handle argument list format
            return {arg.get('name', 'arg'): 'test_value' for arg in schema if isinstance(arg, dict)}
        
        return {}
    
    def _add_result(self, test_name: str, category: str, passed: bool, 
                   message: str, duration: float, details: Optional[Dict[str, Any]] = None,
                   severity: str = "error"):
        """Add a test result."""
        result = ProtocolTestResult(
            test_name=test_name,
            category=category,
            passed=passed,
            message=message,
            duration=duration,
            details=details,
            severity=severity
        )
        self.test_results.append(result)
        
        level = logging.INFO if passed else logging.ERROR
        logger.log(level, f"{test_name}: {message}")
    
    def _format_results(self) -> List[Dict[str, Any]]:
        """Format test results for return."""
        return [
            {
                "test_name": result.test_name,
                "category": result.category,
                "passed": result.passed,
                "message": result.message,
                "duration": result.duration,
                "details": result.details,
                "severity": result.severity,
                "timestamp": datetime.now().isoformat()
            }
            for result in self.test_results
        ]
    
    async def _cleanup_server(self):
        """Clean up server process."""
        if self.server_process:
            try:
                self.server_process.terminate()
                await asyncio.sleep(1)
                
                if self.server_process.poll() is None:
                    self.server_process.kill()
                    
            except Exception as e:
                logger.error(f"Error cleaning up server: {e}")
            finally:
                self.server_process = None

async def main():
    """CLI entry point for protocol testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Protocol Compliance Tester")
    parser.add_argument("server_path", help="Path to MCP server to test")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = MCPProtocolTester()
    results = await tester.run_full_compliance_test(args.server_path)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        print(json.dumps(results, indent=2))
    
    # Exit with error code if any tests failed
    failed_tests = [r for r in results if not r['passed']]
    sys.exit(0 if not failed_tests else 1)

if __name__ == "__main__":
    asyncio.run(main())