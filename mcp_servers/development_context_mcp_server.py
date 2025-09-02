#!/usr/bin/env python3
"""
Development Context Resurrection MCP Server for SynthNet AI

Solves the #1 developer pain point: losing context when switching between tasks.
Saves and restores complete development sessions including files, terminal state, 
git branches, running processes, and developer notes.

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
import glob
import psutil

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
    
    async def run(self, host: str = "localhost", port: int = 8767):
        self.logger.info(f"Starting {self.name} on {host}:{port}")
        while True:
            await asyncio.sleep(1)


class ContextManager:
    """Development context management class"""
    
    def __init__(self):
        self.logger = logging.getLogger("ContextManager")
        self.sessions_dir = Path("/data/data/com.termux/files/home/synthnet/dev_sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
    def _run_command(self, command: List[str], cwd: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str, str]:
        """Execute command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def capture_git_state(self, project_path: str) -> Dict[str, Any]:
        """Capture current Git repository state"""
        try:
            if not os.path.exists(os.path.join(project_path, '.git')):
                return {"git_available": False, "message": "Not a git repository"}
            
            git_info = {"git_available": True}
            
            # Get current branch
            success, stdout, stderr = self._run_command(['git', 'branch', '--show-current'], cwd=project_path)
            git_info['current_branch'] = stdout.strip() if success else "unknown"
            
            # Get uncommitted changes
            success, stdout, stderr = self._run_command(['git', 'status', '--porcelain'], cwd=project_path)
            git_info['uncommitted_files'] = stdout.strip().split('\n') if stdout.strip() else []
            
            # Get recent commits
            success, stdout, stderr = self._run_command(
                ['git', 'log', '--oneline', '-5'], cwd=project_path
            )
            git_info['recent_commits'] = stdout.strip().split('\n') if success else []
            
            # Get stash list
            success, stdout, stderr = self._run_command(['git', 'stash', 'list'], cwd=project_path)
            git_info['stashes'] = stdout.strip().split('\n') if stdout.strip() else []
            
            return git_info
            
        except Exception as e:
            return {"git_available": False, "error": str(e)}
    
    def capture_editor_state(self, project_path: str) -> Dict[str, Any]:
        """Capture currently open editor files and cursor positions"""
        editor_info = {
            "open_files": [],
            "recent_files": [],
            "editor_sessions": []
        }
        
        try:
            # Look for common editor session files
            session_patterns = [
                ".vscode/settings.json",
                ".idea/workspace.xml", 
                "Session.vim",
                ".vim/session.vim"
            ]
            
            for pattern in session_patterns:
                session_file = os.path.join(project_path, pattern)
                if os.path.exists(session_file):
                    editor_info["editor_sessions"].append({
                        "type": pattern.split('/')[0] if '/' in pattern else "vim",
                        "file": pattern,
                        "modified": os.path.getmtime(session_file)
                    })
            
            # Find recently modified files (likely being worked on)
            try:
                recent_files = []
                for root, dirs, files in os.walk(project_path):
                    # Skip common ignore directories
                    dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
                    
                    for file in files:
                        if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.md')):
                            file_path = os.path.join(root, file)
                            try:
                                mtime = os.path.getmtime(file_path)
                                if datetime.now().timestamp() - mtime < 3600:  # Modified in last hour
                                    recent_files.append({
                                        "path": os.path.relpath(file_path, project_path),
                                        "modified": mtime,
                                        "size": os.path.getsize(file_path)
                                    })
                            except OSError:
                                continue
                
                # Sort by modification time
                recent_files.sort(key=lambda x: x['modified'], reverse=True)
                editor_info["recent_files"] = recent_files[:20]  # Top 20 recent files
                
            except Exception as e:
                self.logger.error(f"Error capturing recent files: {e}")
        
        except Exception as e:
            self.logger.error(f"Error capturing editor state: {e}")
        
        return editor_info
    
    def capture_terminal_state(self) -> Dict[str, Any]:
        """Capture current terminal sessions and history"""
        terminal_info = {
            "active_sessions": [],
            "command_history": [],
            "environment_vars": {},
            "current_directory": os.getcwd()
        }
        
        try:
            # Capture command history (last 20 commands)
            history_file = os.path.expanduser("~/.bash_history")
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r') as f:
                        history = f.readlines()
                        terminal_info["command_history"] = [cmd.strip() for cmd in history[-20:]]
                except Exception as e:
                    self.logger.error(f"Error reading bash history: {e}")
            
            # Capture important environment variables
            important_vars = [
                'PATH', 'PYTHONPATH', 'NODE_PATH', 'JAVA_HOME', 'GOPATH', 
                'VIRTUAL_ENV', 'CONDA_DEFAULT_ENV', 'GITHUB_TOKEN'
            ]
            for var in important_vars:
                if var in os.environ:
                    # Mask sensitive variables
                    if 'TOKEN' in var or 'KEY' in var or 'SECRET' in var:
                        terminal_info["environment_vars"][var] = "***MASKED***"
                    else:
                        terminal_info["environment_vars"][var] = os.environ[var]
            
            # Get active terminal processes
            try:
                current_pid = os.getpid()
                parent = psutil.Process(current_pid).parent()
                if parent:
                    terminal_info["active_sessions"].append({
                        "pid": parent.pid,
                        "name": parent.name(),
                        "cmdline": parent.cmdline()
                    })
            except Exception as e:
                self.logger.error(f"Error capturing terminal processes: {e}")
        
        except Exception as e:
            self.logger.error(f"Error capturing terminal state: {e}")
        
        return terminal_info
    
    def capture_running_processes(self, project_path: str) -> Dict[str, Any]:
        """Capture development-related running processes"""
        processes_info = {
            "dev_servers": [],
            "databases": [],
            "other_processes": []
        }
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    proc_info = proc.info
                    if not proc_info['cmdline']:
                        continue
                    
                    cmdline_str = ' '.join(proc_info['cmdline'])
                    
                    # Check if process is related to current project
                    if proc_info['cwd'] and project_path in proc_info['cwd']:
                        process_data = {
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cmdline": cmdline_str[:100],  # Truncate long command lines
                            "cwd": proc_info['cwd']
                        }
                        
                        # Categorize processes
                        if any(server in cmdline_str.lower() for server in ['serve', 'server', 'flask', 'django', 'express', 'node']):
                            processes_info["dev_servers"].append(process_data)
                        elif any(db in cmdline_str.lower() for db in ['postgres', 'mysql', 'mongo', 'redis']):
                            processes_info["databases"].append(process_data)
                        else:
                            processes_info["other_processes"].append(process_data)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            self.logger.error(f"Error capturing running processes: {e}")
        
        return processes_info
    
    def extract_todo_comments(self, project_path: str) -> List[Dict[str, Any]]:
        """Extract TODO, FIXME, and NOTE comments from codebase"""
        todos = []
        todo_patterns = [
            r'#\s*(TODO|FIXME|NOTE|HACK|XXX):\s*(.+)',  # Python, Shell
            r'//\s*(TODO|FIXME|NOTE|HACK|XXX):\s*(.+)', # JavaScript, Java, C++
            r'/\*\s*(TODO|FIXME|NOTE|HACK|XXX):\s*(.+)\s*\*/', # Multi-line comments
        ]
        
        try:
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
                
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    for pattern in todo_patterns:
                                        match = re.search(pattern, line, re.IGNORECASE)
                                        if match:
                                            todos.append({
                                                "file": os.path.relpath(file_path, project_path),
                                                "line": line_num,
                                                "type": match.group(1).upper(),
                                                "comment": match.group(2).strip(),
                                                "full_line": line.strip()
                                            })
                        except Exception as e:
                            continue
        
        except Exception as e:
            self.logger.error(f"Error extracting TODOs: {e}")
        
        return todos[:50]  # Limit to first 50 TODOs


# Initialize server and manager
mcp = SimpleMCPServer("Development Context MCP")
context_mgr = ContextManager()


@mcp.tool
async def save_development_session(session_name: str, project_path: str = "", notes: str = "") -> Dict[str, Any]:
    """
    Save complete development session including all context.
    
    Args:
        session_name: Name for the session
        project_path: Path to project directory (default: current directory)
        notes: Additional notes about current work
        
    Returns:
        Dictionary containing session save result
    """
    try:
        if not project_path:
            project_path = os.getcwd()
        
        project_path = os.path.abspath(project_path)
        if not os.path.exists(project_path):
            return {"success": False, "error": f"Project path does not exist: {project_path}"}
        
        session_data = {
            "session_name": session_name,
            "project_path": project_path,
            "saved_at": datetime.now().isoformat(),
            "notes": notes,
            "git_state": context_mgr.capture_git_state(project_path),
            "editor_state": context_mgr.capture_editor_state(project_path),
            "terminal_state": context_mgr.capture_terminal_state(),
            "running_processes": context_mgr.capture_running_processes(project_path),
            "todo_comments": context_mgr.extract_todo_comments(project_path)
        }
        
        # Save session to file
        session_file = context_mgr.sessions_dir / f"{session_name}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return {
            "success": True,
            "session_name": session_name,
            "session_file": str(session_file),
            "project_path": project_path,
            "saved_at": session_data["saved_at"],
            "context_captured": {
                "git_branch": session_data["git_state"].get("current_branch", "none"),
                "uncommitted_files": len(session_data["git_state"].get("uncommitted_files", [])),
                "recent_files": len(session_data["editor_state"]["recent_files"]),
                "todo_comments": len(session_data["todo_comments"]),
                "running_processes": sum(len(procs) for procs in session_data["running_processes"].values())
            },
            "message": f"Development session '{session_name}' saved successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def list_development_sessions() -> Dict[str, Any]:
    """
    List all saved development sessions.
    
    Returns:
        Dictionary containing list of available sessions
    """
    try:
        sessions = []
        
        for session_file in context_mgr.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    "session_name": session_data["session_name"],
                    "project_path": session_data["project_path"],
                    "saved_at": session_data["saved_at"],
                    "notes": session_data.get("notes", "")[:100],  # Truncate long notes
                    "git_branch": session_data["git_state"].get("current_branch", "none"),
                    "file_count": len(session_data["editor_state"]["recent_files"])
                })
                
            except Exception as e:
                continue
        
        # Sort by save date (most recent first)
        sessions.sort(key=lambda x: x['saved_at'], reverse=True)
        
        return {
            "success": True,
            "sessions": sessions,
            "total_count": len(sessions),
            "sessions_directory": str(context_mgr.sessions_dir)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "sessions": []}


@mcp.tool
async def load_development_session(session_name: str) -> Dict[str, Any]:
    """
    Load and display development session details.
    
    Args:
        session_name: Name of the session to load
        
    Returns:
        Dictionary containing full session details
    """
    try:
        session_file = context_mgr.sessions_dir / f"{session_name}.json"
        
        if not session_file.exists():
            return {"success": False, "error": f"Session '{session_name}' not found"}
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        return {
            "success": True,
            "session_data": session_data,
            "restoration_guide": {
                "project_directory": session_data["project_path"],
                "git_branch": session_data["git_state"].get("current_branch", "none"),
                "files_to_open": [f["path"] for f in session_data["editor_state"]["recent_files"][:10]],
                "commands_to_run": session_data["terminal_state"]["command_history"][-5:],
                "processes_to_start": session_data["running_processes"]["dev_servers"],
                "todos_to_review": session_data["todo_comments"][:10]
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def restore_development_session(session_name: str, auto_restore: bool = False) -> Dict[str, Any]:
    """
    Restore development session context (guidance mode).
    
    Args:
        session_name: Name of the session to restore
        auto_restore: Whether to automatically restore what's possible
        
    Returns:
        Dictionary containing restoration instructions and results
    """
    try:
        session_file = context_mgr.sessions_dir / f"{session_name}.json"
        
        if not session_file.exists():
            return {"success": False, "error": f"Session '{session_name}' not found"}
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        restoration_steps = []
        results = []
        
        # 1. Navigate to project directory
        project_path = session_data["project_path"]
        if os.path.exists(project_path):
            restoration_steps.append(f"cd {project_path}")
            if auto_restore:
                os.chdir(project_path)
                results.append({"step": "change_directory", "success": True, "message": f"Changed to {project_path}"})
        else:
            restoration_steps.append(f"# Warning: Project directory not found: {project_path}")
        
        # 2. Git branch restoration
        git_branch = session_data["git_state"].get("current_branch")
        if git_branch and git_branch != "none":
            restoration_steps.append(f"git checkout {git_branch}")
            if auto_restore and os.path.exists(project_path):
                success, stdout, stderr = context_mgr._run_command(
                    ['git', 'checkout', git_branch], cwd=project_path
                )
                results.append({
                    "step": "git_checkout", 
                    "success": success,
                    "message": stdout if success else stderr
                })
        
        # 3. File restoration suggestions
        recent_files = session_data["editor_state"]["recent_files"][:5]
        if recent_files:
            file_list = " ".join([f["path"] for f in recent_files])
            restoration_steps.append(f"# Open recent files: {file_list}")
        
        # 4. Environment restoration
        env_vars = session_data["terminal_state"]["environment_vars"]
        for var, value in env_vars.items():
            if value != "***MASKED***":
                restoration_steps.append(f"export {var}='{value}'")
        
        # 5. Process restoration suggestions
        dev_servers = session_data["running_processes"]["dev_servers"]
        for server in dev_servers:
            restoration_steps.append(f"# Restart server: {server['cmdline'][:50]}...")
        
        # 6. TODO reminders
        todos = session_data["todo_comments"][:5]
        if todos:
            restoration_steps.append("# Recent TODOs to review:")
            for todo in todos:
                restoration_steps.append(f"#   {todo['file']}:{todo['line']} - {todo['comment']}")
        
        return {
            "success": True,
            "session_name": session_name,
            "project_path": project_path,
            "restoration_steps": restoration_steps,
            "auto_restore_results": results,
            "context_summary": {
                "git_branch": git_branch,
                "recent_files_count": len(recent_files),
                "todo_count": len(todos),
                "running_processes": len(dev_servers),
                "session_age": session_data["saved_at"]
            },
            "message": f"Session '{session_name}' restoration guide generated"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def delete_development_session(session_name: str) -> Dict[str, Any]:
    """
    Delete a saved development session.
    
    Args:
        session_name: Name of the session to delete
        
    Returns:
        Dictionary containing deletion result
    """
    try:
        session_file = context_mgr.sessions_dir / f"{session_name}.json"
        
        if not session_file.exists():
            return {"success": False, "error": f"Session '{session_name}' not found"}
        
        session_file.unlink()
        
        return {
            "success": True,
            "session_name": session_name,
            "message": f"Session '{session_name}' deleted successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
async def capture_current_context(project_path: str = "") -> Dict[str, Any]:
    """
    Capture current development context without saving as session.
    
    Args:
        project_path: Path to project directory (default: current directory)
        
    Returns:
        Dictionary containing current context information
    """
    try:
        if not project_path:
            project_path = os.getcwd()
        
        project_path = os.path.abspath(project_path)
        
        context_snapshot = {
            "captured_at": datetime.now().isoformat(),
            "project_path": project_path,
            "git_state": context_mgr.capture_git_state(project_path),
            "editor_state": context_mgr.capture_editor_state(project_path),
            "terminal_state": context_mgr.capture_terminal_state(),
            "running_processes": context_mgr.capture_running_processes(project_path),
            "todo_comments": context_mgr.extract_todo_comments(project_path)
        }
        
        return {
            "success": True,
            "context_snapshot": context_snapshot,
            "summary": {
                "project": os.path.basename(project_path),
                "git_branch": context_snapshot["git_state"].get("current_branch", "none"),
                "uncommitted_changes": len(context_snapshot["git_state"].get("uncommitted_files", [])),
                "recent_files": len(context_snapshot["editor_state"]["recent_files"]),
                "active_processes": sum(len(procs) for procs in context_snapshot["running_processes"].values()),
                "pending_todos": len(context_snapshot["todo_comments"])
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.resource
async def context_manager_status() -> str:
    """Get context manager status and statistics."""
    try:
        sessions = []
        total_size = 0
        
        for session_file in context_mgr.sessions_dir.glob("*.json"):
            try:
                file_size = session_file.stat().st_size
                total_size += file_size
                
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    "name": session_data["session_name"],
                    "saved_at": session_data["saved_at"],
                    "size_kb": round(file_size / 1024, 1)
                })
                
            except Exception:
                continue
        
        status_info = {
            "context_manager_status": "operational",
            "sessions_directory": str(context_mgr.sessions_dir),
            "total_sessions": len(sessions),
            "total_size_kb": round(total_size / 1024, 1),
            "recent_sessions": sorted(sessions, key=lambda x: x['saved_at'], reverse=True)[:5],
            "available_tools": [
                "save_development_session",
                "list_development_sessions", 
                "load_development_session",
                "restore_development_session",
                "delete_development_session",
                "capture_current_context"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(status_info, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "timestamp": datetime.now().isoformat()}, indent=2)


if __name__ == "__main__":
    print("🧠 Development Context Resurrection MCP Server for SynthNet AI")
    print("=" * 70)
    
    print("✅ Context management system initialized")
    print(f"📁 Sessions directory: {context_mgr.sessions_dir}")
    
    print("\nAvailable tools:")
    for tool_name in mcp.tools.keys():
        print(f"  - {tool_name}")
    
    print("\nAvailable resources:")
    for resource_name in mcp.resources.keys():
        print(f"  - {resource_name}")
    
    print("\nStarting Development Context MCP Server...")
    
    try:
        if "--test" in sys.argv:
            async def test_context_server():
                print("\n🧪 Testing Development Context MCP Server...")
                
                # Test current context capture
                result = await capture_current_context()
                print(f"Capture context: {'✅' if result['success'] else '❌'}")
                
                # Test session save
                result = await save_development_session("test_session", notes="Test session")
                print(f"Save session: {'✅' if result['success'] else '❌'}")
                
                # Test session list
                result = await list_development_sessions()
                print(f"List sessions: {'✅' if result['success'] else '❌'}")
                
                # Test session load
                result = await load_development_session("test_session")
                print(f"Load session: {'✅' if result['success'] else '❌'}")
                
                # Clean up test session
                await delete_development_session("test_session")
                
                print("\n✅ Development Context MCP Server tests completed")
            
            asyncio.run(test_context_server())
        else:
            asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("\n👋 Shutting down Development Context MCP Server...")
    except Exception as e:
        print(f"❌ Error: {e}")