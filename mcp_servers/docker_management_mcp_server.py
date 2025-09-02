#!/usr/bin/env python3
"""
Docker Management MCP Server for SynthNet AI

A comprehensive Docker container management MCP server optimized for Termux/Android.
Provides intelligent container lifecycle management, image optimization, and development workflow automation.

Author: SynthNet AI Team
Version: 1.0.0
License: MIT
"""

import asyncio
import json
import logging
import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re
import yaml
import tarfile

# Simple MCP server implementation
class SimpleMCPServer:
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(self.name)
    
    def tool(self, func):
        self.tools[func.__name__] = func
        return func
    
    def resource(self, func):
        self.resources[func.__name__] = func
        return func
    
    async def run(self, host: str = "localhost", port: int = 8766):
        self.logger.info(f"Starting {self.name} on {host}:{port}")
        while True:
            await asyncio.sleep(1)


class DockerManager:
    """Docker operations management class"""
    
    def __init__(self):
        self.logger = logging.getLogger("DockerManager")
        self._check_docker_availability()
    
    def _check_docker_availability(self) -> bool:
        """Check if Docker is available and accessible"""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info(f"Docker available: {result.stdout.strip()}")
                return True
            else:
                self.logger.warning("Docker command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Docker not available: {e}")
            return False
    
    def _run_docker_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Execute docker command and return success, stdout, stderr"""
        try:
            full_command = ['docker'] + command
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def parse_docker_ps_output(self, output: str) -> List[Dict]:
        """Parse docker ps output into structured data"""
        lines = output.strip().split('\n')
        if len(lines) < 2:  # No containers or header only
            return []
        
        containers = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 7:
                container = {
                    "container_id": parts[0],
                    "image": parts[1],
                    "command": ' '.join(parts[2:-4]) if len(parts) > 7 else parts[2],
                    "created": parts[-4],
                    "status": parts[-3],
                    "ports": parts[-2],
                    "names": parts[-1]
                }
                containers.append(container)
        return containers


# Initialize server and manager
mcp = SimpleMCPServer("Docker Management MCP")
docker_mgr = DockerManager()


@mcp.tool
async def list_containers(status: str = "all") -> Dict[str, Any]:
    """
    List Docker containers with optional status filtering.
    
    Args:
        status: Container status filter (all, running, stopped, exited)
        
    Returns:
        Dictionary containing container list and metadata
    """
    try:
        # Build docker ps command
        command = ['ps']
        if status == "all":
            command.append('-a')
        elif status == "running":
            command.extend(['--filter', 'status=running'])
        elif status == "stopped":
            command.extend(['--filter', 'status=exited'])
        elif status == "exited":
            command.extend(['--filter', 'status=exited'])
        
        success, stdout, stderr = docker_mgr._run_docker_command(command)
        
        if success:
            containers = docker_mgr.parse_docker_ps_output(stdout)
            return {
                "success": True,
                "containers": containers,
                "total_count": len(containers),
                "status_filter": status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": stderr,
                "containers": [],
                "total_count": 0
            }
            
    except Exception as e:
        return {"success": False, "error": str(e), "containers": []}


@mcp.tool
async def create_container(image: str, name: str = "", ports: str = "", volumes: str = "", env_vars: str = "", command: str = "") -> Dict[str, Any]:
    """
    Create a new Docker container with specified configuration.
    
    Args:
        image: Docker image name (e.g., "nginx:latest")
        name: Container name (optional)
        ports: Port mappings (e.g., "8080:80,9000:9000")
        volumes: Volume mounts (e.g., "/host/path:/container/path")
        env_vars: Environment variables (e.g., "KEY1=value1,KEY2=value2")
        command: Command to run in container (optional)
        
    Returns:
        Dictionary containing container creation result
    """
    try:
        docker_command = ['run', '-d']  # Run in detached mode
        
        # Add container name
        if name:
            docker_command.extend(['--name', name])
        
        # Add port mappings
        if ports:
            for port_map in ports.split(','):
                if ':' in port_map:
                    docker_command.extend(['-p', port_map.strip()])
        
        # Add volume mounts
        if volumes:
            for volume_map in volumes.split(','):
                if ':' in volume_map:
                    docker_command.extend(['-v', volume_map.strip()])
        
        # Add environment variables
        if env_vars:
            for env_var in env_vars.split(','):
                if '=' in env_var:
                    docker_command.extend(['-e', env_var.strip()])
        
        # Add image
        docker_command.append(image)
        
        # Add command if specified
        if command:
            docker_command.extend(command.split())
        
        success, stdout, stderr = docker_mgr._run_docker_command(docker_command, timeout=60)
        
        if success:
            container_id = stdout.strip()
            return {
                "success": True,
                "container_id": container_id,
                "container_name": name or container_id[:12],
                "image": image,
                "status": "created",
                "message": f"Container created successfully"
            }
        else:
            return {
                "success": False,
                "error": stderr,
                "message": "Failed to create container"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def manage_container(container_id: str, action: str) -> Dict[str, Any]:
    """
    Manage container lifecycle (start, stop, restart, remove, pause, unpause).
    
    Args:
        container_id: Container ID or name
        action: Action to perform (start, stop, restart, remove, pause, unpause, kill)
        
    Returns:
        Dictionary containing operation result
    """
    try:
        valid_actions = ['start', 'stop', 'restart', 'remove', 'rm', 'pause', 'unpause', 'kill']
        
        if action not in valid_actions:
            return {
                "success": False,
                "error": f"Invalid action. Valid actions: {', '.join(valid_actions)}"
            }
        
        # Handle 'remove' -> 'rm' alias
        docker_action = 'rm' if action == 'remove' else action
        
        # Add force flag for remove operations
        command = [docker_action]
        if docker_action == 'rm':
            command.append('-f')  # Force remove even if running
        
        command.append(container_id)
        
        success, stdout, stderr = docker_mgr._run_docker_command(command, timeout=30)
        
        if success:
            return {
                "success": True,
                "container_id": container_id,
                "action": action,
                "message": f"Container {action} operation completed successfully",
                "output": stdout.strip() if stdout.strip() else None
            }
        else:
            return {
                "success": False,
                "container_id": container_id,
                "action": action,
                "error": stderr,
                "message": f"Failed to {action} container"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def inspect_container(container_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a container.
    
    Args:
        container_id: Container ID or name
        
    Returns:
        Dictionary containing detailed container information
    """
    try:
        success, stdout, stderr = docker_mgr._run_docker_command(['inspect', container_id])
        
        if success:
            container_info = json.loads(stdout)[0]  # Docker inspect returns array
            
            # Extract key information
            simplified_info = {
                "container_id": container_info["Id"][:12],
                "name": container_info["Name"].lstrip('/'),
                "image": container_info["Config"]["Image"],
                "state": {
                    "status": container_info["State"]["Status"],
                    "running": container_info["State"]["Running"],
                    "started_at": container_info["State"]["StartedAt"],
                    "finished_at": container_info["State"]["FinishedAt"]
                },
                "network": {
                    "ip_address": container_info["NetworkSettings"]["IPAddress"],
                    "ports": container_info["NetworkSettings"]["Ports"]
                },
                "mounts": [
                    {
                        "source": mount["Source"],
                        "destination": mount["Destination"],
                        "mode": mount["Mode"]
                    } for mount in container_info["Mounts"]
                ],
                "environment": container_info["Config"]["Env"],
                "created": container_info["Created"]
            }
            
            return {
                "success": True,
                "container_info": simplified_info,
                "full_inspect_available": True
            }
        else:
            return {
                "success": False,
                "error": stderr,
                "message": f"Failed to inspect container {container_id}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def list_images() -> Dict[str, Any]:
    """
    List available Docker images.
    
    Returns:
        Dictionary containing image list and metadata
    """
    try:
        success, stdout, stderr = docker_mgr._run_docker_command(['images', '--format', 'table {{.Repository}}:{{.Tag}}\t{{.ImageID}}\t{{.CreatedSince}}\t{{.Size}}'])
        
        if success:
            lines = stdout.strip().split('\n')
            images = []
            
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        images.append({
                            "repository_tag": parts[0],
                            "image_id": parts[1][:12],
                            "created": parts[2],
                            "size": parts[3]
                        })
            
            return {
                "success": True,
                "images": images,
                "total_count": len(images),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": stderr,
                "images": []
            }
            
    except Exception as e:
        return {"success": False, "error": str(e), "images": []}


@mcp.tool
async def pull_image(image: str, tag: str = "latest") -> Dict[str, Any]:
    """
    Pull a Docker image from registry.
    
    Args:
        image: Image name (e.g., "nginx", "ubuntu")
        tag: Image tag (default: "latest")
        
    Returns:
        Dictionary containing pull operation result
    """
    try:
        full_image = f"{image}:{tag}"
        success, stdout, stderr = docker_mgr._run_docker_command(['pull', full_image], timeout=300)  # 5 min timeout
        
        if success:
            return {
                "success": True,
                "image": full_image,
                "message": f"Successfully pulled {full_image}",
                "output": stdout.strip()
            }
        else:
            return {
                "success": False,
                "image": full_image,
                "error": stderr,
                "message": f"Failed to pull {full_image}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def remove_image(image: str, force: bool = False) -> Dict[str, Any]:
    """
    Remove a Docker image.
    
    Args:
        image: Image ID or name:tag
        force: Force removal even if image is used by containers
        
    Returns:
        Dictionary containing removal result
    """
    try:
        command = ['rmi']
        if force:
            command.append('-f')
        command.append(image)
        
        success, stdout, stderr = docker_mgr._run_docker_command(command)
        
        if success:
            return {
                "success": True,
                "image": image,
                "message": f"Successfully removed image {image}",
                "output": stdout.strip()
            }
        else:
            return {
                "success": False,
                "image": image,
                "error": stderr,
                "message": f"Failed to remove image {image}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def container_logs(container_id: str, tail: int = 100, follow: bool = False) -> Dict[str, Any]:
    """
    Get container logs.
    
    Args:
        container_id: Container ID or name
        tail: Number of lines to show from end of logs
        follow: Whether to follow log output (not recommended for MCP)
        
    Returns:
        Dictionary containing container logs
    """
    try:
        command = ['logs']
        if tail > 0:
            command.extend(['--tail', str(tail)])
        if follow:
            command.append('-f')
        
        command.append(container_id)
        
        timeout = 10 if not follow else 30
        success, stdout, stderr = docker_mgr._run_docker_command(command, timeout=timeout)
        
        if success:
            return {
                "success": True,
                "container_id": container_id,
                "logs": stdout,
                "lines_shown": len(stdout.split('\n')) if stdout else 0,
                "tail": tail
            }
        else:
            return {
                "success": False,
                "container_id": container_id,
                "error": stderr,
                "message": f"Failed to get logs for container {container_id}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def execute_in_container(container_id: str, command: str, interactive: bool = False) -> Dict[str, Any]:
    """
    Execute a command inside a running container.
    
    Args:
        container_id: Container ID or name
        command: Command to execute
        interactive: Whether to run in interactive mode
        
    Returns:
        Dictionary containing execution result
    """
    try:
        docker_command = ['exec']
        if interactive:
            docker_command.extend(['-it'])
        
        docker_command.append(container_id)
        docker_command.extend(command.split())
        
        success, stdout, stderr = docker_mgr._run_docker_command(docker_command, timeout=60)
        
        if success:
            return {
                "success": True,
                "container_id": container_id,
                "command": command,
                "output": stdout,
                "exit_code": 0
            }
        else:
            return {
                "success": False,
                "container_id": container_id,
                "command": command,
                "error": stderr,
                "exit_code": 1
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def create_development_environment(project_name: str, base_image: str = "ubuntu:22.04", ports: str = "8000:8000") -> Dict[str, Any]:
    """
    Create a complete development environment container.
    
    Args:
        project_name: Name for the development environment
        base_image: Base Docker image to use
        ports: Port mappings for the development server
        
    Returns:
        Dictionary containing environment creation result
    """
    try:
        # Create a development-focused container with common tools
        container_name = f"dev-{project_name}"
        
        docker_command = [
            'run', '-d',
            '--name', container_name,
            '-p', ports,
            '-v', f'/data/data/com.termux/files/home/synthnet/workspace:/workspace',
            '-w', '/workspace',
            base_image,
            'tail', '-f', '/dev/null'  # Keep container running
        ]
        
        success, stdout, stderr = docker_mgr._run_docker_command(docker_command, timeout=120)
        
        if success:
            container_id = stdout.strip()
            
            # Install common development tools
            setup_commands = [
                "apt-get update && apt-get install -y curl wget git vim nano python3 python3-pip nodejs npm",
                "pip3 install --upgrade pip",
                "npm install -g yarn"
            ]
            
            setup_results = []
            for cmd in setup_commands:
                setup_success, setup_out, setup_err = docker_mgr._run_docker_command(
                    ['exec', container_id, 'bash', '-c', cmd], timeout=180
                )
                setup_results.append({
                    "command": cmd,
                    "success": setup_success,
                    "output": setup_out[:200] if setup_out else "",  # Limit output
                    "error": setup_err[:200] if setup_err else ""
                })
            
            return {
                "success": True,
                "container_id": container_id,
                "container_name": container_name,
                "project_name": project_name,
                "base_image": base_image,
                "ports": ports,
                "workspace_mount": "/workspace",
                "setup_results": setup_results,
                "message": f"Development environment '{container_name}' created successfully"
            }
        else:
            return {
                "success": False,
                "error": stderr,
                "message": f"Failed to create development environment"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.resource
async def docker_system_info() -> str:
    """Get Docker system information and status."""
    try:
        # Get Docker version
        version_success, version_out, version_err = docker_mgr._run_docker_command(['--version'])
        
        # Get system info
        info_success, info_out, info_err = docker_mgr._run_docker_command(['info', '--format', '{{json .}}'])
        
        # Get disk usage
        usage_success, usage_out, usage_err = docker_mgr._run_docker_command(['system', 'df'])
        
        system_info = {
            "docker_version": version_out.strip() if version_success else "Unknown",
            "system_available": version_success,
            "disk_usage": usage_out if usage_success else "Unable to get disk usage",
            "timestamp": datetime.now().isoformat()
        }
        
        if info_success:
            try:
                docker_info = json.loads(info_out)
                system_info.update({
                    "containers_running": docker_info.get("ContainersRunning", 0),
                    "containers_total": docker_info.get("Containers", 0),
                    "images_total": docker_info.get("Images", 0),
                    "server_version": docker_info.get("ServerVersion", "Unknown"),
                    "storage_driver": docker_info.get("Driver", "Unknown")
                })
            except json.JSONDecodeError:
                system_info["docker_info_error"] = "Failed to parse Docker info"
        
        return json.dumps(system_info, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "timestamp": datetime.now().isoformat()}, indent=2)


if __name__ == "__main__":
    print("🐳 Docker Management MCP Server for SynthNet AI")
    print("=" * 55)
    
    # Check Docker availability
    if not docker_mgr._check_docker_availability():
        print("❌ Docker is not available or accessible")
        print("Please ensure Docker is installed and running")
        print("\nFor Termux users:")
        print("1. Install Docker: pkg install docker")
        print("2. Start Docker daemon: sudo dockerd &")
        print("3. Add user to docker group: sudo usermod -aG docker $USER")
        sys.exit(1)
    else:
        print("✅ Docker is available and accessible")
    
    print("\nAvailable tools:")
    for tool_name in mcp.tools.keys():
        print(f"  - {tool_name}")
    
    print("\nAvailable resources:")
    for resource_name in mcp.resources.keys():
        print(f"  - {resource_name}")
    
    print("\nStarting Docker Management MCP Server...")
    
    try:
        if "--test" in sys.argv:
            async def test_docker_server():
                print("\n🧪 Testing Docker MCP Server...")
                
                # Test listing containers
                result = await list_containers()
                print(f"List containers: {'✅' if result['success'] else '❌'}")
                
                # Test listing images
                result = await list_images()
                print(f"List images: {'✅' if result['success'] else '❌'}")
                
                # Test system info
                info = await docker_system_info()
                print(f"System info: {'✅' if 'error' not in info else '❌'}")
                
                print("\n✅ Docker MCP Server tests completed")
            
            asyncio.run(test_docker_server())
        else:
            asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("\n👋 Shutting down Docker Management MCP Server...")
    except Exception as e:
        print(f"❌ Error: {e}")