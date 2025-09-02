#!/usr/bin/env python3
"""
Simple GitHub MCP Server for SynthNet AI

A lightweight MCP server for GitHub integration using only standard library and basic HTTP requests.
Optimized for Termux/Android environments where complex dependencies may be problematic.

Author: SynthNet AI Team
Version: 1.0.0
License: MIT
"""

import asyncio
import json
import logging
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import socket

# Simple MCP server implementation without external dependencies
class SimpleMCPServer:
    """Simple MCP server using only standard library"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(self.name)
    
    def tool(self, func):
        """Decorator to register a tool"""
        self.tools[func.__name__] = func
        return func
    
    def resource(self, func):
        """Decorator to register a resource"""
        self.resources[func.__name__] = func
        return func
    
    async def run(self, host: str = "localhost", port: int = 8765):
        """Run the MCP server"""
        self.logger.info(f"Starting {self.name} on {host}:{port}")
        
        # Simple server loop for demonstration
        # In a real implementation, this would handle MCP protocol
        while True:
            await asyncio.sleep(1)
            # Server running - tools can be called directly for testing


class GitHubClient:
    """Simple GitHub API client using urllib"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to GitHub API"""
        url = f"{self.base_url}{endpoint}"
        
        # Prepare headers
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SynthNet-Simple-MCP/1.0"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        # Prepare request
        req_data = None
        if data and method in ["POST", "PATCH", "PUT"]:
            req_data = json.dumps(data).encode('utf-8')
            headers["Content-Type"] = "application/json"
        
        try:
            request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"GitHub API Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


# Initialize server and client
mcp = SimpleMCPServer("Simple GitHub MCP")
github_client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))


@mcp.tool
async def get_repository_info(owner: str, repo: str) -> Dict[str, Any]:
    """
    Get basic information about a GitHub repository.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        
    Returns:
        Dictionary containing repository information
    """
    try:
        data = github_client._make_request(f"/repos/{owner}/{repo}")
        
        return {
            "success": True,
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data.get("description"),
            "html_url": data["html_url"],
            "clone_url": data["clone_url"],
            "default_branch": data["default_branch"],
            "is_private": data["private"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "language": data.get("language"),
            "created_at": data["created_at"],
            "updated_at": data["updated_at"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def list_repository_files(owner: str, repo: str, path: str = "", branch: str = "main") -> Dict[str, Any]:
    """
    List files and directories in a GitHub repository.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        path: Path within the repository (default: root)
        branch: Branch name (default: main)
        
    Returns:
        Dictionary containing file/directory listing
    """
    try:
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        if branch != "main":
            endpoint += f"?ref={branch}"
            
        data = github_client._make_request(endpoint)
        
        if isinstance(data, list):
            files = []
            for item in data:
                files.append({
                    "name": item["name"],
                    "path": item["path"],
                    "type": item["type"],  # "file" or "dir"
                    "size": item.get("size", 0),
                    "download_url": item.get("download_url")
                })
            
            return {
                "success": True,
                "owner": owner,
                "repo": repo,
                "path": path,
                "branch": branch,
                "files": files
            }
        else:
            # Single file
            return {
                "success": True,
                "owner": owner,
                "repo": repo,
                "path": path,
                "branch": branch,
                "files": [{
                    "name": data["name"],
                    "path": data["path"],
                    "type": data["type"],
                    "size": data.get("size", 0),
                    "download_url": data.get("download_url")
                }]
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def get_file_content(owner: str, repo: str, path: str, branch: str = "main") -> Dict[str, Any]:
    """
    Get the content of a specific file from a GitHub repository.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        path: File path within the repository
        branch: Branch name (default: main)
        
    Returns:
        Dictionary containing file content and metadata
    """
    try:
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        if branch != "main":
            endpoint += f"?ref={branch}"
            
        data = github_client._make_request(endpoint)
        
        if data.get("type") != "file":
            return {"success": False, "error": "Path is not a file"}
        
        # Decode base64 content
        content = base64.b64decode(data["content"]).decode('utf-8')
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "path": path,
            "branch": branch,
            "content": content,
            "size": data["size"],
            "encoding": data["encoding"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def search_repositories(query: str, sort: str = "updated", limit: int = 10) -> Dict[str, Any]:
    """
    Search for GitHub repositories.
    
    Args:
        query: Search query
        sort: Sort criteria (stars, forks, updated)
        limit: Maximum number of results
        
    Returns:
        Dictionary containing search results
    """
    try:
        encoded_query = urllib.parse.quote(query)
        endpoint = f"/search/repositories?q={encoded_query}&sort={sort}&per_page={limit}"
        
        data = github_client._make_request(endpoint)
        
        repositories = []
        for item in data.get("items", []):
            repositories.append({
                "name": item["name"],
                "full_name": item["full_name"],
                "description": item.get("description"),
                "html_url": item["html_url"],
                "language": item.get("language"),
                "stars": item["stargazers_count"],
                "forks": item["forks_count"],
                "updated_at": item["updated_at"]
            })
        
        return {
            "success": True,
            "query": query,
            "total_count": data.get("total_count", 0),
            "repositories": repositories
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def get_user_repositories(username: str = "", limit: int = 20) -> Dict[str, Any]:
    """
    Get repositories for a user.
    
    Args:
        username: GitHub username (leave empty for authenticated user)
        limit: Maximum number of repositories
        
    Returns:
        Dictionary containing user's repositories
    """
    try:
        if username:
            endpoint = f"/users/{username}/repos?per_page={limit}"
        else:
            endpoint = f"/user/repos?per_page={limit}"
            
        data = github_client._make_request(endpoint)
        
        repositories = []
        for item in data:
            repositories.append({
                "name": item["name"],
                "full_name": item["full_name"],
                "description": item.get("description"),
                "html_url": item["html_url"],
                "language": item.get("language"),
                "private": item["private"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"]
            })
        
        return {
            "success": True,
            "username": username or "authenticated_user",
            "repositories": repositories
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def create_issue(owner: str, repo: str, title: str, body: str = "") -> Dict[str, Any]:
    """
    Create a new issue in a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        title: Issue title
        body: Issue description
        
    Returns:
        Dictionary containing created issue info
    """
    try:
        data = {
            "title": title,
            "body": body
        }
        
        response = github_client._make_request(f"/repos/{owner}/{repo}/issues", method="POST", data=data)
        
        return {
            "success": True,
            "number": response["number"],
            "title": response["title"],
            "html_url": response["html_url"],
            "state": response["state"],
            "created_at": response["created_at"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.resource
async def github_status() -> str:
    """Get GitHub API status and rate limits."""
    try:
        rate_limit = github_client._make_request("/rate_limit")
        
        status = {
            "github_api_status": "connected",
            "rate_limit": {
                "remaining": rate_limit["rate"]["remaining"],
                "limit": rate_limit["rate"]["limit"],
                "reset_time": rate_limit["rate"]["reset"]
            },
            "server_time": datetime.now().isoformat(),
            "token_configured": bool(github_client.token)
        }
        
        return json.dumps(status, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# Test functions for direct invocation
async def test_server():
    """Test the MCP server tools"""
    print("🧪 Testing Simple GitHub MCP Server...")
    
    # Test repository info
    print("\n1. Testing get_repository_info...")
    result = await get_repository_info("octocat", "Hello-World")
    print(f"Result: {result.get('success', False)}")
    if result.get('success'):
        print(f"Repository: {result['full_name']}")
        print(f"Description: {result['description']}")
        print(f"Stars: {result['stars']}")
    
    # Test file listing
    print("\n2. Testing list_repository_files...")
    result = await list_repository_files("octocat", "Hello-World")
    print(f"Result: {result.get('success', False)}")
    if result.get('success'):
        print(f"Files found: {len(result['files'])}")
        for file in result['files'][:3]:  # Show first 3
            print(f"  - {file['name']} ({file['type']})")
    
    # Test search
    print("\n3. Testing search_repositories...")
    result = await search_repositories("python machine learning", limit=3)
    print(f"Result: {result.get('success', False)}")
    if result.get('success'):
        print(f"Repositories found: {len(result['repositories'])}")
        for repo in result['repositories']:
            print(f"  - {repo['full_name']} ({repo['stars']} ⭐)")
    
    # Test GitHub status
    print("\n4. Testing github_status resource...")
    status = await github_status()
    print(f"Status: {json.loads(status).get('github_api_status', 'unknown')}")


if __name__ == "__main__":
    print("🚀 Simple GitHub MCP Server for SynthNet AI")
    print("=" * 50)
    
    # Check for GitHub token
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️  Warning: GITHUB_TOKEN not set. Some features may be limited.")
        print("   Set with: export GITHUB_TOKEN='your_token_here'")
    else:
        print("✅ GitHub token configured")
    
    print("\nAvailable tools:")
    for tool_name in mcp.tools.keys():
        print(f"  - {tool_name}")
    
    print("\nAvailable resources:")
    for resource_name in mcp.resources.keys():
        print(f"  - {resource_name}")
    
    print("\nStarting server...")
    
    try:
        # Run test mode if --test argument provided
        if "--test" in sys.argv:
            asyncio.run(test_server())
        else:
            # Start MCP server
            asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error: {e}")