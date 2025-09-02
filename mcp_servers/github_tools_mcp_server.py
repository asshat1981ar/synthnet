#!/usr/bin/env python3
"""
GitHub Tools MCP Server for SynthNet AI

This MCP server provides comprehensive GitHub development tools optimized for Termux/Android.
It includes advanced repository management, code analysis, CI/CD integration, and development workflow tools.

Author: SynthNet AI Team
Version: 1.0.0
License: MIT
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
import re
import yaml

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.types import Resource, Tool
except ImportError:
    print("MCP SDK not found. Install with: pip install mcp")
    exit(1)

import aiohttp
import aiofiles


@dataclass
class GitHubToolsConfig:
    """Configuration for GitHub Tools MCP server"""
    token: Optional[str] = None
    username: Optional[str] = None
    base_url: str = "https://api.github.com"
    workspace_dir: str = "/data/data/com.termux/files/home/synthnet/workspace"
    
    @classmethod
    def from_env(cls) -> 'GitHubToolsConfig':
        return cls(
            token=os.getenv("GITHUB_TOKEN"),
            username=os.getenv("GITHUB_USERNAME"),
            base_url=os.getenv("GITHUB_API_URL", "https://api.github.com"),
            workspace_dir=os.getenv("SYNTHNET_WORKSPACE", "/data/data/com.termux/files/home/synthnet/workspace")
        )


@dataclass
class CodeAnalysisResult:
    """Code analysis result structure"""
    file_path: str
    language: str
    lines_of_code: int
    complexity_score: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    dependencies: List[str]


@dataclass
class WorkflowStatus:
    """GitHub Actions workflow status"""
    workflow_name: str
    status: str
    conclusion: Optional[str]
    run_id: int
    branch: str
    commit_sha: str
    created_at: str
    html_url: str


class GitHubToolsServer:
    """GitHub Tools MCP Server implementation"""
    
    def __init__(self):
        self.config = GitHubToolsConfig.from_env()
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = self._setup_logging()
        self._ensure_workspace()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the MCP server"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/data/data/com.termux/files/home/synthnet/logs/github_tools_mcp.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("GitHubToolsServer")
    
    def _ensure_workspace(self):
        """Ensure workspace directory exists"""
        Path(self.config.workspace_dir).mkdir(parents=True, exist_ok=True)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with GitHub authentication"""
        if self.session is None:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "SynthNet-GitHub-Tools-MCP/1.0"
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
            elif method.upper() == "DELETE":
                async with session.delete(url) as response:
                    response.raise_for_status()
                    return await response.json() if response.content else {}
        except aiohttp.ClientError as e:
            self.logger.error(f"GitHub API request failed: {e}")
            raise
    
    def _run_shell_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        """Execute shell command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=cwd or self.config.workspace_dir,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()


# Initialize the MCP server
mcp = FastMCP("GitHub Tools Integration")
github_tools = GitHubToolsServer()


@mcp.tool()
async def create_github_repository(name: str, description: str = "", private: bool = False, auto_init: bool = True) -> Dict[str, Any]:
    """
    Create a new GitHub repository.
    
    Args:
        name: Repository name
        description: Repository description
        private: Whether the repository should be private
        auto_init: Initialize with README
        
    Returns:
        Dictionary containing created repository information
    """
    try:
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init
        }
        
        response = await github_tools._github_api_request("/user/repos", method="POST", data=data)
        
        return {
            "success": True,
            "name": response["name"],
            "full_name": response["full_name"],
            "html_url": response["html_url"],
            "clone_url": response["clone_url"],
            "ssh_url": response["ssh_url"],
            "private": response["private"],
            "created_at": response["created_at"]
        }
        
    except Exception as e:
        github_tools.logger.error(f"Failed to create repository: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def fork_repository(owner: str, repo: str, organization: str = "") -> Dict[str, Any]:
    """
    Fork a GitHub repository.
    
    Args:
        owner: Original repository owner
        repo: Repository name
        organization: Organization to fork to (optional)
        
    Returns:
        Dictionary containing forked repository information
    """
    try:
        data = {}
        if organization:
            data["organization"] = organization
            
        response = await github_tools._github_api_request(
            f"/repos/{owner}/{repo}/forks",
            method="POST",
            data=data
        )
        
        return {
            "success": True,
            "name": response["name"],
            "full_name": response["full_name"],
            "html_url": response["html_url"],
            "clone_url": response["clone_url"],
            "parent": response["parent"]["full_name"],
            "created_at": response["created_at"]
        }
        
    except Exception as e:
        github_tools.logger.error(f"Failed to fork repository: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def create_pull_request(owner: str, repo: str, title: str, body: str, head: str, base: str = "main") -> Dict[str, Any]:
    """
    Create a pull request.
    
    Args:
        owner: Repository owner
        repo: Repository name
        title: PR title
        body: PR description
        head: Source branch
        base: Target branch
        
    Returns:
        Dictionary containing PR information
    """
    try:
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        response = await github_tools._github_api_request(
            f"/repos/{owner}/{repo}/pulls",
            method="POST",
            data=data
        )
        
        return {
            "success": True,
            "number": response["number"],
            "title": response["title"],
            "html_url": response["html_url"],
            "head_branch": response["head"]["ref"],
            "base_branch": response["base"]["ref"],
            "state": response["state"],
            "created_at": response["created_at"]
        }
        
    except Exception as e:
        github_tools.logger.error(f"Failed to create pull request: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def analyze_repository_code(owner: str, repo: str, branch: str = "main", max_files: int = 50) -> Dict[str, Any]:
    """
    Analyze code quality and structure of a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch to analyze
        max_files: Maximum number of files to analyze
        
    Returns:
        Dictionary containing code analysis results
    """
    try:
        # Clone repository to temporary directory
        temp_dir = tempfile.mkdtemp()
        clone_url = f"https://github.com/{owner}/{repo}.git"
        
        success, stdout, stderr = github_tools._run_shell_command([
            "git", "clone", "--depth", "1", "--branch", branch, clone_url, temp_dir
        ])
        
        if not success:
            return {"success": False, "error": f"Failed to clone repository: {stderr}"}
        
        # Analyze code files
        analysis_results = []
        file_count = 0
        
        for root, dirs, files in os.walk(temp_dir):
            # Skip .git and node_modules directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
            
            for file in files:
                if file_count >= max_files:
                    break
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, temp_dir)
                
                # Only analyze code files
                if any(file.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']):
                    result = await _analyze_code_file(file_path, rel_path)
                    if result:
                        analysis_results.append(result)
                        file_count += 1
        
        # Calculate overall metrics
        total_loc = sum(r.lines_of_code for r in analysis_results)
        avg_complexity = sum(r.complexity_score for r in analysis_results) / len(analysis_results) if analysis_results else 0
        all_issues = []
        for r in analysis_results:
            all_issues.extend(r.issues)
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "files_analyzed": len(analysis_results),
            "total_lines_of_code": total_loc,
            "average_complexity": round(avg_complexity, 2),
            "total_issues": len(all_issues),
            "file_analyses": [asdict(r) for r in analysis_results],
            "summary": {
                "code_quality": "Good" if avg_complexity < 5 else "Fair" if avg_complexity < 10 else "Needs Improvement",
                "issue_density": len(all_issues) / total_loc * 1000 if total_loc > 0 else 0
            }
        }
        
    except Exception as e:
        github_tools.logger.error(f"Failed to analyze repository code: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def setup_github_actions_workflow(owner: str, repo: str, workflow_type: str, language: str = "python") -> Dict[str, Any]:
    """
    Create a GitHub Actions workflow for a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        workflow_type: Type of workflow (ci, cd, test, lint)
        language: Programming language
        
    Returns:
        Dictionary containing workflow setup result
    """
    try:
        workflow_templates = {
            "ci": _generate_ci_workflow(language),
            "cd": _generate_cd_workflow(language),
            "test": _generate_test_workflow(language),
            "lint": _generate_lint_workflow(language)
        }
        
        if workflow_type not in workflow_templates:
            return {"success": False, "error": f"Unknown workflow type: {workflow_type}"}
        
        workflow_content = workflow_templates[workflow_type]
        workflow_path = f".github/workflows/{workflow_type}-{language}.yml"
        
        # Create workflow file via GitHub API
        data = {
            "message": f"Add {workflow_type} workflow for {language}",
            "content": workflow_content,
            "path": workflow_path
        }
        
        response = await github_tools._github_api_request(
            f"/repos/{owner}/{repo}/contents/{workflow_path}",
            method="PUT",
            data=data
        )
        
        return {
            "success": True,
            "workflow_path": workflow_path,
            "workflow_type": workflow_type,
            "language": language,
            "commit_sha": response["commit"]["sha"],
            "html_url": response["content"]["html_url"]
        }
        
    except Exception as e:
        github_tools.logger.error(f"Failed to setup workflow: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def manage_repository_secrets(owner: str, repo: str, action: str, secret_name: str = "", secret_value: str = "") -> Dict[str, Any]:
    """
    Manage GitHub repository secrets.
    
    Args:
        owner: Repository owner
        repo: Repository name
        action: Action to perform (list, create, update, delete)
        secret_name: Name of the secret
        secret_value: Value of the secret (for create/update)
        
    Returns:
        Dictionary containing operation result
    """
    try:
        if action == "list":
            response = await github_tools._github_api_request(f"/repos/{owner}/{repo}/actions/secrets")
            return {
                "success": True,
                "secrets": [secret["name"] for secret in response.get("secrets", [])]
            }
        
        elif action in ["create", "update"]:
            if not secret_name or not secret_value:
                return {"success": False, "error": "Secret name and value required"}
            
            # Get repository public key for encryption
            key_response = await github_tools._github_api_request(f"/repos/{owner}/{repo}/actions/secrets/public-key")
            
            # For simplicity, this is a basic implementation
            # In production, you'd use the public key to encrypt the secret
            data = {
                "encrypted_value": secret_value,  # Should be encrypted with public key
                "key_id": key_response["key_id"]
            }
            
            await github_tools._github_api_request(
                f"/repos/{owner}/{repo}/actions/secrets/{secret_name}",
                method="PUT",
                data=data
            )
            
            return {"success": True, "message": f"Secret {secret_name} {action}d successfully"}
        
        elif action == "delete":
            if not secret_name:
                return {"success": False, "error": "Secret name required"}
            
            await github_tools._github_api_request(
                f"/repos/{owner}/{repo}/actions/secrets/{secret_name}",
                method="DELETE"
            )
            
            return {"success": True, "message": f"Secret {secret_name} deleted successfully"}
        
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
            
    except Exception as e:
        github_tools.logger.error(f"Failed to manage secrets: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def sync_local_repository(repo_path: str, remote_url: str = "", branch: str = "main") -> Dict[str, Any]:
    """
    Sync a local repository with remote.
    
    Args:
        repo_path: Local repository path
        remote_url: Remote repository URL (optional)
        branch: Branch to sync
        
    Returns:
        Dictionary containing sync result
    """
    try:
        full_path = os.path.join(github_tools.config.workspace_dir, repo_path)
        
        if not os.path.exists(full_path):
            return {"success": False, "error": "Repository path does not exist"}
        
        # Check if it's a git repository
        if not os.path.exists(os.path.join(full_path, ".git")):
            return {"success": False, "error": "Not a git repository"}
        
        operations = []
        
        # Add remote if provided
        if remote_url:
            success, stdout, stderr = github_tools._run_shell_command([
                "git", "remote", "add", "origin", remote_url
            ], cwd=full_path)
            operations.append({"operation": "add_remote", "success": success, "output": stdout or stderr})
        
        # Fetch latest changes
        success, stdout, stderr = github_tools._run_shell_command([
            "git", "fetch", "origin"
        ], cwd=full_path)
        operations.append({"operation": "fetch", "success": success, "output": stdout or stderr})
        
        # Pull latest changes
        success, stdout, stderr = github_tools._run_shell_command([
            "git", "pull", "origin", branch
        ], cwd=full_path)
        operations.append({"operation": "pull", "success": success, "output": stdout or stderr})
        
        # Get current status
        success, stdout, stderr = github_tools._run_shell_command([
            "git", "status", "--porcelain"
        ], cwd=full_path)
        
        has_changes = bool(stdout.strip()) if success else False
        
        return {
            "success": True,
            "repo_path": repo_path,
            "branch": branch,
            "operations": operations,
            "has_uncommitted_changes": has_changes,
            "status": stdout if success else stderr
        }
        
    except Exception as e:
        github_tools.logger.error(f"Failed to sync repository: {e}")
        return {"success": False, "error": str(e)}


# Helper functions
async def _analyze_code_file(file_path: str, rel_path: str) -> Optional[CodeAnalysisResult]:
    """Analyze a single code file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect language
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.go': 'go', '.rs': 'rust'
        }
        language = language_map.get(ext, 'unknown')
        
        # Count lines of code (excluding empty lines and comments)
        lines = content.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*'))])
        
        # Simple complexity calculation (cyclomatic complexity approximation)
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'catch', 'switch', 'case']
        complexity = sum(content.lower().count(keyword) for keyword in complexity_keywords)
        complexity_score = complexity / max(loc, 1) * 10  # Normalize
        
        # Find potential issues
        issues = []
        if loc > 500:
            issues.append({"type": "size", "message": "File is very large", "severity": "warning"})
        if complexity_score > 10:
            issues.append({"type": "complexity", "message": "High complexity score", "severity": "warning"})
        
        # Extract imports/dependencies (simplified)
        dependencies = []
        for line in lines[:20]:  # Check first 20 lines
            if any(line.strip().startswith(prefix) for prefix in ['import ', 'from ', '#include', 'require(']):
                dependencies.append(line.strip())
        
        # Generate suggestions
        suggestions = []
        if complexity_score > 5:
            suggestions.append("Consider breaking down complex functions")
        if loc > 200:
            suggestions.append("Consider splitting large file into smaller modules")
        
        return CodeAnalysisResult(
            file_path=rel_path,
            language=language,
            lines_of_code=loc,
            complexity_score=round(complexity_score, 2),
            issues=issues,
            suggestions=suggestions,
            dependencies=dependencies[:5]  # Limit to first 5
        )
        
    except Exception as e:
        github_tools.logger.error(f"Failed to analyze file {file_path}: {e}")
        return None


def _generate_ci_workflow(language: str) -> str:
    """Generate CI workflow content"""
    if language == "python":
        return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Test with pytest
      run: |
        pytest --cov=./ --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
"""
    elif language == "javascript":
        return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [14.x, 16.x, 18.x]

    steps:
    - uses: actions/checkout@v3
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    - run: npm ci
    - run: npm run build --if-present
    - run: npm test
"""
    else:
        return f"# Generic CI workflow for {language}\n# Please customize based on your needs"


def _generate_cd_workflow(language: str) -> str:
    """Generate CD workflow content"""
    return f"""name: CD

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy {language} application
      run: |
        echo "Add your deployment steps here"
        # Customize based on your deployment needs
"""


def _generate_test_workflow(language: str) -> str:
    """Generate test workflow content"""
    return f"""name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests for {language}
      run: |
        echo "Add your test commands here"
        # Customize based on your testing framework
"""


def _generate_lint_workflow(language: str) -> str:
    """Generate lint workflow content"""
    if language == "python":
        return """name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black isort
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    - name: Check formatting with black
      run: black --check .
    - name: Check import sorting with isort
      run: isort --check-only .
"""
    else:
        return f"""name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Lint {language} code
      run: |
        echo "Add your linting commands here"
        # Customize based on your language's linting tools
"""


if __name__ == "__main__":
    # Ensure log directory exists
    log_dir = Path("/data/data/com.termux/files/home/synthnet/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Start the MCP server
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down GitHub Tools MCP Server...")
    finally:
        asyncio.run(github_tools.close())