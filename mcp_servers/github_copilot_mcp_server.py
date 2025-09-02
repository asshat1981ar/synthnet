#!/usr/bin/env python3
"""
GitHub Copilot MCP Server for SynthNet AI

This MCP server provides GitHub integration tools optimized for Termux/Android environments.
It enables GitHub Copilot to interact with GitHub repositories, issues, pull requests, and workflows
while maintaining compatibility with the SynthNet AI ecosystem.

Author: SynthNet AI Team
Version: 1.0.0
License: MIT
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.types import Resource, Tool
except ImportError:
    print("MCP SDK not found. Install with: pip install mcp")
    exit(1)

import aiohttp
import aiofiles


@dataclass
class GitHubConfig:
    """Configuration for GitHub API access"""
    token: Optional[str] = None
    username: Optional[str] = None
    base_url: str = "https://api.github.com"
    
    @classmethod
    def from_env(cls) -> 'GitHubConfig':
        return cls(
            token=os.getenv("GITHUB_TOKEN"),
            username=os.getenv("GITHUB_USERNAME"),
            base_url=os.getenv("GITHUB_API_URL", "https://api.github.com")
        )


@dataclass
class RepositoryInfo:
    """Repository information structure"""
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    clone_url: str
    ssh_url: str
    default_branch: str
    is_private: bool
    created_at: str
    updated_at: str


@dataclass
class IssueInfo:
    """GitHub issue information"""
    number: int
    title: str
    body: Optional[str]
    state: str
    html_url: str
    created_at: str
    updated_at: str
    labels: List[str]
    assignees: List[str]


@dataclass
class PullRequestInfo:
    """GitHub pull request information"""
    number: int
    title: str
    body: Optional[str]
    state: str
    html_url: str
    head_branch: str
    base_branch: str
    created_at: str
    updated_at: str
    mergeable: Optional[bool]


class GitHubMCPServer:
    """Main GitHub MCP Server implementation"""
    
    def __init__(self):
        self.config = GitHubConfig.from_env()
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the MCP server"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/data/data/com.termux/files/home/synthnet/logs/github_mcp.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("GitHubMCPServer")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with GitHub authentication"""
        if self.session is None:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "SynthNet-GitHub-MCP/1.0"
            }
            if self.config.token:
                headers["Authorization"] = f"token {self.config.token}"
            
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def _github_api_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make authenticated GitHub API request"""
        session = await self._get_session()
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method.upper() == "PATCH":
                async with session.patch(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"GitHub API request failed: {e}")
            raise
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()


# Initialize the MCP server
mcp = FastMCP("GitHub Copilot Integration")
github_server = GitHubMCPServer()


@mcp.tool()
async def get_repository_info(owner: str, repo: str) -> Dict[str, Any]:
    """
    Get detailed information about a GitHub repository.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        
    Returns:
        Dictionary containing repository information
    """
    try:
        data = await github_server._github_api_request(f"/repos/{owner}/{repo}")
        
        repo_info = RepositoryInfo(
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            html_url=data["html_url"],
            clone_url=data["clone_url"],
            ssh_url=data["ssh_url"],
            default_branch=data["default_branch"],
            is_private=data["private"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
        
        return asdict(repo_info)
        
    except Exception as e:
        github_server.logger.error(f"Failed to get repository info: {e}")
        return {"error": str(e)}


@mcp.tool()
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
            
        data = await github_server._github_api_request(endpoint)
        
        files = []
        for item in data:
            files.append({
                "name": item["name"],
                "path": item["path"],
                "type": item["type"],
                "size": item.get("size", 0),
                "sha": item["sha"]
            })
        
        return {
            "owner": owner,
            "repo": repo,
            "path": path,
            "branch": branch,
            "files": files
        }
        
    except Exception as e:
        github_server.logger.error(f"Failed to list repository files: {e}")
        return {"error": str(e)}


@mcp.tool()
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
            
        data = await github_server._github_api_request(endpoint)
        
        # Decode base64 content
        import base64
        content = base64.b64decode(data["content"]).decode('utf-8')
        
        return {
            "owner": owner,
            "repo": repo,
            "path": path,
            "branch": branch,
            "content": content,
            "size": data["size"],
            "sha": data["sha"],
            "encoding": data["encoding"]
        }
        
    except Exception as e:
        github_server.logger.error(f"Failed to get file content: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Ensure log directory exists
    log_dir = Path("/data/data/com.termux/files/home/synthnet/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Start the MCP server
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down GitHub MCP Server...")
    finally:
        asyncio.run(github_server.close())