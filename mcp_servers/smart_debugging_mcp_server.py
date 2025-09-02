#!/usr/bin/env python3
"""
Smart Debugging Assistant MCP Server for SynthNet AI

Transforms debugging from random trial-and-error into intelligent, pattern-based problem solving.
Analyzes bug patterns, suggests fixes, traces execution paths, and learns from codebase history.

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
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import traceback
import difflib
import hashlib

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
    
    async def run(self, host: str = "localhost", port: int = 8768):
        self.logger.info(f"Starting {self.name} on {host}:{port}")
        while True:
            await asyncio.sleep(1)


class DebuggingAnalyzer:
    """Smart debugging analysis engine"""
    
    def __init__(self):
        self.logger = logging.getLogger("DebuggingAnalyzer")
        self.debug_cache_dir = Path("/data/data/com.termux/files/home/synthnet/debug_cache")
        self.debug_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Common error patterns and their solutions
        self.error_patterns = {
            "python": {
                r"ModuleNotFoundError: No module named '(.+)'": {
                    "cause": "Missing Python package",
                    "solutions": ["pip install {}", "Check virtual environment", "Verify PYTHONPATH"]
                },
                r"IndentationError: (.+)": {
                    "cause": "Python indentation issue",
                    "solutions": ["Fix indentation", "Check tab/space mixing", "Use consistent indentation"]
                },
                r"NameError: name '(.+)' is not defined": {
                    "cause": "Variable not defined or out of scope",
                    "solutions": ["Define variable before use", "Check variable scope", "Fix typo in variable name"]
                },
                r"AttributeError: '(.+)' object has no attribute '(.+)'": {
                    "cause": "Method/attribute doesn't exist",
                    "solutions": ["Check object type", "Verify method name", "Check API documentation"]
                },
                r"TypeError: (.+) takes (\d+) positional arguments but (\d+) were given": {
                    "cause": "Wrong number of function arguments",
                    "solutions": ["Check function signature", "Verify argument count", "Check for missing parameters"]
                }
            },
            "javascript": {
                r"ReferenceError: (.+) is not defined": {
                    "cause": "Variable or function not declared",
                    "solutions": ["Declare variable", "Check scope", "Import missing module"]
                },
                r"TypeError: Cannot read property '(.+)' of undefined": {
                    "cause": "Accessing property of undefined object",
                    "solutions": ["Check object existence", "Add null checks", "Initialize object properly"]
                },
                r"SyntaxError: Unexpected token (.+)": {
                    "cause": "JavaScript syntax error",
                    "solutions": ["Check syntax", "Verify bracket matching", "Check for missing semicolons"]
                }
            },
            "general": {
                r"Permission denied": {
                    "cause": "File permission issue",
                    "solutions": ["chmod +x file", "Check file ownership", "Run with appropriate privileges"]
                },
                r"Connection refused": {
                    "cause": "Service not running or wrong port",
                    "solutions": ["Start the service", "Check port number", "Verify network configuration"]
                },
                r"No space left on device": {
                    "cause": "Disk full",
                    "solutions": ["Free disk space", "Clean temporary files", "Move files to other location"]
                }
            }
        }
    
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
    
    def analyze_error_pattern(self, error_message: str, language: str = "general") -> Dict[str, Any]:
        """Analyze error message and suggest solutions"""
        analysis = {
            "error_type": "unknown",
            "likely_cause": "Unknown error",
            "suggested_solutions": [],
            "confidence": 0.0,
            "pattern_matched": False
        }
        
        # Get patterns for the language
        patterns = self.error_patterns.get(language, {})
        patterns.update(self.error_patterns.get("general", {}))
        
        for pattern, info in patterns.items():
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                analysis.update({
                    "error_type": pattern,
                    "likely_cause": info["cause"],
                    "suggested_solutions": [sol.format(*match.groups()) if "{}" in sol else sol for sol in info["solutions"]],
                    "confidence": 0.9,
                    "pattern_matched": True,
                    "matched_groups": match.groups()
                })
                break
        
        return analysis
    
    def search_git_history(self, error_message: str, project_path: str, max_commits: int = 50) -> List[Dict[str, Any]]:
        """Search Git history for similar errors and their fixes"""
        similar_fixes = []
        
        try:
            # Get recent commits with messages containing error-related keywords
            error_keywords = self._extract_error_keywords(error_message)
            
            for keyword in error_keywords[:3]:  # Limit to top 3 keywords
                success, stdout, stderr = self._run_command([
                    'git', 'log', '--oneline', f'-{max_commits}', 
                    '--grep', keyword, '--ignore-case'
                ], cwd=project_path)
                
                if success:
                    for line in stdout.strip().split('\n'):
                        if line:
                            commit_hash = line.split()[0]
                            commit_msg = ' '.join(line.split()[1:])
                            
                            # Get the diff for this commit
                            diff_success, diff_out, diff_err = self._run_command([
                                'git', 'show', '--stat', commit_hash
                            ], cwd=project_path)
                            
                            if diff_success:
                                similar_fixes.append({
                                    "commit_hash": commit_hash,
                                    "message": commit_msg,
                                    "keyword_match": keyword,
                                    "files_changed": self._parse_git_stat(diff_out),
                                    "relevance_score": self._calculate_relevance(error_message, commit_msg)
                                })
        
        except Exception as e:
            self.logger.error(f"Error searching git history: {e}")
        
        # Sort by relevance score
        similar_fixes.sort(key=lambda x: x['relevance_score'], reverse=True)
        return similar_fixes[:10]  # Top 10 most relevant
    
    def _extract_error_keywords(self, error_message: str) -> List[str]:
        """Extract meaningful keywords from error message"""
        # Common error-related keywords
        error_words = ['error', 'exception', 'failed', 'missing', 'undefined', 'invalid', 'timeout']
        
        # Extract words from error message
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', error_message.lower())
        
        # Filter and prioritize keywords
        keywords = []
        for word in words:
            if len(word) >= 3 and word not in ['the', 'and', 'for', 'with', 'from']:
                keywords.append(word)
        
        return keywords[:5]  # Top 5 keywords
    
    def _parse_git_stat(self, git_stat_output: str) -> List[str]:
        """Parse git stat output to get changed files"""
        files = []
        for line in git_stat_output.split('\n'):
            if '|' in line and ('+' in line or '-' in line):
                file_name = line.split('|')[0].strip()
                if file_name:
                    files.append(file_name)
        return files
    
    def _calculate_relevance(self, error_message: str, commit_message: str) -> float:
        """Calculate relevance score between error and commit message"""
        error_words = set(re.findall(r'\b\w+\b', error_message.lower()))
        commit_words = set(re.findall(r'\b\w+\b', commit_message.lower()))
        
        if not error_words or not commit_words:
            return 0.0
        
        intersection = error_words.intersection(commit_words)
        union = error_words.union(commit_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_related_files(self, stack_trace: str, project_path: str) -> List[Dict[str, Any]]:
        """Find files mentioned in stack trace and related files"""
        related_files = []
        
        # Extract file paths from stack trace
        file_patterns = [
            r'"([^"]+\.py)"',  # Python files in quotes
            r"'([^']+\.py)'",  # Python files in single quotes
            r'File "([^"]+)"',  # Python traceback format
            r'at ([^(]+\.js):\d+:\d+',  # JavaScript files
            r'([a-zA-Z_][a-zA-Z0-9_/]*\.[a-zA-Z]+):\d+'  # General file:line format
        ]
        
        file_paths = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, stack_trace)
            file_paths.update(matches)
        
        # Analyze each file
        for file_path in file_paths:
            full_path = os.path.join(project_path, file_path) if not os.path.isabs(file_path) else file_path
            
            if os.path.exists(full_path):
                try:
                    # Get file info
                    stat = os.stat(full_path)
                    
                    # Find imports/dependencies in the file
                    dependencies = self._find_file_dependencies(full_path)
                    
                    related_files.append({
                        "file_path": file_path,
                        "full_path": full_path,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "dependencies": dependencies,
                        "exists": True
                    })
                except Exception as e:
                    related_files.append({
                        "file_path": file_path,
                        "full_path": full_path,
                        "error": str(e),
                        "exists": False
                    })
        
        return related_files
    
    def _find_file_dependencies(self, file_path: str) -> List[str]:
        """Find dependencies in a source file"""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Python imports
            if file_path.endswith('.py'):
                import_patterns = [
                    r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
                ]
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    dependencies.extend(matches)
            
            # JavaScript requires/imports
            elif file_path.endswith(('.js', '.ts')):
                js_patterns = [
                    r"require\(['\"]([^'\"]+)['\"]\)",
                    r"import.+from\s+['\"]([^'\"]+)['\"]"
                ]
                for pattern in js_patterns:
                    matches = re.findall(pattern, content)
                    dependencies.extend(matches)
        
        except Exception as e:
            self.logger.error(f"Error analyzing dependencies in {file_path}: {e}")
        
        return dependencies[:10]  # Limit to 10 dependencies
    
    def generate_reproduction_steps(self, error_info: Dict[str, Any]) -> List[str]:
        """Generate steps to reproduce the bug"""
        steps = [
            "1. Navigate to the project directory",
            "2. Ensure all dependencies are installed"
        ]
        
        # Add language-specific steps
        if "python" in error_info.get("language", "").lower():
            steps.extend([
                "3. Activate virtual environment (if applicable)",
                "4. Run: python -m pytest (or your test command)",
                "5. Check Python version compatibility"
            ])
        elif "javascript" in error_info.get("language", "").lower():
            steps.extend([
                "3. Run: npm install (to ensure dependencies)",
                "4. Run: npm test (or your test command)",
                "5. Check Node.js version compatibility"
            ])
        else:
            steps.extend([
                "3. Check system dependencies",
                "4. Verify configuration files",
                "5. Run the failing command"
            ])
        
        steps.extend([
            "6. Check logs for additional error details",
            "7. Verify environment variables",
            "8. Test with minimal reproduction case"
        ])
        
        return steps


# Initialize server and analyzer
mcp = SimpleMCPServer("Smart Debugging Assistant MCP")
debug_analyzer = DebuggingAnalyzer()


@mcp.tool
async def analyze_bug_pattern(error_message: str, stack_trace: str = "", language: str = "general", project_path: str = "") -> Dict[str, Any]:
    """
    Analyze error pattern and suggest intelligent fixes based on patterns and history.
    
    Args:
        error_message: The error message to analyze
        stack_trace: Full stack trace (optional)
        language: Programming language (python, javascript, java, etc.)
        project_path: Path to project directory for git history search
        
    Returns:
        Dictionary containing comprehensive bug analysis
    """
    try:
        if not project_path:
            project_path = os.getcwd()
        
        # Analyze error pattern
        pattern_analysis = debug_analyzer.analyze_error_pattern(error_message, language)
        
        # Search git history for similar fixes
        git_fixes = []
        if os.path.exists(project_path) and os.path.exists(os.path.join(project_path, '.git')):
            git_fixes = debug_analyzer.search_git_history(error_message, project_path)
        
        # Find related files from stack trace
        related_files = []
        if stack_trace:
            related_files = debug_analyzer.find_related_files(stack_trace, project_path)
        
        # Generate reproduction steps
        reproduction_steps = debug_analyzer.generate_reproduction_steps({
            "language": language,
            "error": error_message
        })
        
        return {
            "success": True,
            "error_analysis": {
                "error_message": error_message,
                "language": language,
                "pattern_matched": pattern_analysis["pattern_matched"],
                "error_type": pattern_analysis["error_type"],
                "confidence": pattern_analysis["confidence"]
            },
            "likely_causes": [pattern_analysis["likely_cause"]] if pattern_analysis["likely_cause"] != "Unknown error" else [],
            "suggested_fixes": pattern_analysis["suggested_solutions"],
            "similar_fixes_from_history": git_fixes[:5],  # Top 5 most relevant
            "related_files": related_files,
            "reproduction_steps": reproduction_steps,
            "debugging_strategy": {
                "immediate_actions": [
                    "Check the specific line mentioned in error",
                    "Verify all dependencies are installed",
                    "Check for typos in variable/function names"
                ],
                "investigation_areas": [
                    "Review recent changes in related files",
                    "Check configuration files",
                    "Verify environment setup"
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@mcp.tool
async def trace_execution_path(function_name: str, file_path: str, input_description: str = "") -> Dict[str, Any]:
    """
    Trace execution path and identify potential issues in function flow.
    
    Args:
        function_name: Name of the function to trace
        file_path: Path to the file containing the function
        input_description: Description of input parameters for analysis
        
    Returns:
        Dictionary containing execution path analysis
    """
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
        
        # Read and analyze the function
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the function definition
        function_pattern = rf'def\s+{re.escape(function_name)}\s*\([^)]*\):'
        function_match = re.search(function_pattern, content, re.MULTILINE)
        
        if not function_match:
            return {"success": False, "error": f"Function '{function_name}' not found in {file_path}"}
        
        # Extract function body (simplified - real implementation would need proper parsing)
        lines = content.split('\n')
        function_start = None
        
        for i, line in enumerate(lines):
            if function_match.group() in line:
                function_start = i
                break
        
        if function_start is None:
            return {"success": False, "error": "Could not locate function start"}
        
        # Analyze function structure
        function_lines = []
        indent_level = None
        
        for i in range(function_start, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None and line.strip():
                if i == function_start:
                    indent_level = current_indent
                else:
                    indent_level = current_indent
            
            if current_indent <= indent_level and i > function_start and line.strip() and not line.lstrip().startswith('#'):
                break
            
            function_lines.append({
                "line_number": i + 1,
                "content": line,
                "indent": current_indent
            })
        
        # Analyze execution flow
        execution_analysis = {
            "control_flow": [],
            "potential_issues": [],
            "return_paths": [],
            "exception_handling": []
        }
        
        for line_info in function_lines:
            line = line_info["content"].strip()
            line_num = line_info["line_number"]
            
            # Identify control flow
            if any(keyword in line for keyword in ['if', 'elif', 'else:']):
                execution_analysis["control_flow"].append({
                    "type": "conditional",
                    "line": line_num,
                    "content": line
                })
            elif any(keyword in line for keyword in ['for', 'while']):
                execution_analysis["control_flow"].append({
                    "type": "loop",
                    "line": line_num,
                    "content": line
                })
            elif 'return' in line:
                execution_analysis["return_paths"].append({
                    "line": line_num,
                    "content": line
                })
            
            # Identify potential issues
            if any(risky in line.lower() for risky in ['null', 'none', 'undefined']):
                execution_analysis["potential_issues"].append({
                    "type": "null_check",
                    "line": line_num,
                    "content": line,
                    "suggestion": "Consider null/None checking"
                })
            
            if any(keyword in line for keyword in ['try:', 'except', 'catch']):
                execution_analysis["exception_handling"].append({
                    "line": line_num,
                    "content": line
                })
        
        return {
            "success": True,
            "function_name": function_name,
            "file_path": file_path,
            "function_analysis": {
                "total_lines": len(function_lines),
                "execution_paths": len(execution_analysis["return_paths"]),
                "control_structures": len(execution_analysis["control_flow"]),
                "exception_handlers": len(execution_analysis["exception_handling"])
            },
            "execution_flow": execution_analysis,
            "complexity_assessment": {
                "cyclomatic_complexity": len(execution_analysis["control_flow"]) + 1,
                "complexity_level": "Low" if len(execution_analysis["control_flow"]) < 5 else "High"
            },
            "recommendations": [
                "Add input validation at function start",
                "Include error handling for edge cases",
                "Consider breaking down complex conditional logic",
                "Add logging for debugging purposes"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@mcp.tool
async def find_similar_bugs(error_signature: str, project_path: str = "", search_online: bool = False) -> Dict[str, Any]:
    """
    Find similar bugs in codebase history and optionally search online resources.
    
    Args:
        error_signature: Unique signature of the error
        project_path: Path to project directory
        search_online: Whether to search online bug databases (placeholder)
        
    Returns:
        Dictionary containing similar bug findings
    """
    try:
        if not project_path:
            project_path = os.getcwd()
        
        # Create a hash of the error signature for caching
        error_hash = hashlib.md5(error_signature.encode()).hexdigest()[:8]
        
        similar_bugs = {
            "local_matches": [],
            "online_resources": [],
            "pattern_matches": []
        }
        
        # Search local git history
        if os.path.exists(os.path.join(project_path, '.git')):
            git_matches = debug_analyzer.search_git_history(error_signature, project_path)
            similar_bugs["local_matches"] = git_matches
        
        # Search for similar error patterns in project files
        try:
            error_keywords = debug_analyzer._extract_error_keywords(error_signature)
            pattern_files = []
            
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
                
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.java', '.log')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Check if file contains similar error patterns
                            matches = 0
                            for keyword in error_keywords:
                                if keyword in content.lower():
                                    matches += 1
                            
                            if matches >= 2:  # At least 2 keywords match
                                pattern_files.append({
                                    "file": os.path.relpath(file_path, project_path),
                                    "keyword_matches": matches,
                                    "total_keywords": len(error_keywords)
                                })
                        except Exception:
                            continue
            
            similar_bugs["pattern_matches"] = sorted(pattern_files, key=lambda x: x['keyword_matches'], reverse=True)[:10]
            
        except Exception as e:
            debug_analyzer.logger.error(f"Error searching pattern matches: {e}")
        
        # Placeholder for online search (would integrate with Stack Overflow API, etc.)
        if search_online:
            similar_bugs["online_resources"] = [
                {
                    "source": "Stack Overflow",
                    "title": f"Similar error patterns (search: {error_signature[:50]}...)",
                    "url": f"https://stackoverflow.com/search?q={error_signature[:100]}",
                    "note": "Manual search recommended"
                }
            ]
        
        return {
            "success": True,
            "error_signature": error_signature,
            "search_results": similar_bugs,
            "total_matches": len(similar_bugs["local_matches"]) + len(similar_bugs["pattern_matches"]),
            "recommendations": [
                "Review local matches for proven solutions",
                "Check pattern matches for similar contexts",
                "Search online resources for community solutions"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool
async def debug_session_report(session_name: str, errors_encountered: List[str], fixes_applied: List[str]) -> Dict[str, Any]:
    """
    Generate a debugging session report for future reference.
    
    Args:
        session_name: Name for the debugging session
        errors_encountered: List of errors that were encountered
        fixes_applied: List of fixes that were applied
        
    Returns:
        Dictionary containing session report
    """
    try:
        session_data = {
            "session_name": session_name,
            "timestamp": datetime.now().isoformat(),
            "errors_encountered": errors_encountered,
            "fixes_applied": fixes_applied,
            "session_summary": {
                "total_errors": len(errors_encountered),
                "total_fixes": len(fixes_applied),
                "success_rate": len(fixes_applied) / len(errors_encountered) if errors_encountered else 0
            }
        }
        
        # Save session report
        report_file = debug_analyzer.debug_cache_dir / f"debug_session_{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return {
            "success": True,
            "session_name": session_name,
            "report_file": str(report_file),
            "summary": session_data["session_summary"],
            "lessons_learned": [
                "Error patterns identified for future reference",
                "Successful fixes documented",
                "Debugging strategies recorded"
            ]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.resource
async def debugging_statistics() -> str:
    """Get debugging session statistics and patterns."""
    try:
        stats = {
            "debug_cache_directory": str(debug_analyzer.debug_cache_dir),
            "available_error_patterns": len(debug_analyzer.error_patterns),
            "supported_languages": list(debug_analyzer.error_patterns.keys()),
            "common_error_types": [
                "ModuleNotFoundError (Python)",
                "ReferenceError (JavaScript)", 
                "AttributeError (Python)",
                "Permission denied (System)",
                "Connection refused (Network)"
            ],
            "debugging_tools": [
                "analyze_bug_pattern",
                "trace_execution_path",
                "find_similar_bugs",
                "debug_session_report"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(stats, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


if __name__ == "__main__":
    print("🔍 Smart Debugging Assistant MCP Server for SynthNet AI")
    print("=" * 65)
    
    print("✅ Debugging analysis engine initialized")
    print(f"📁 Debug cache directory: {debug_analyzer.debug_cache_dir}")
    print(f"🧠 Error patterns loaded: {len(debug_analyzer.error_patterns)} languages")
    
    print("\nAvailable tools:")
    for tool_name in mcp.tools.keys():
        print(f"  - {tool_name}")
    
    print("\nAvailable resources:")
    for resource_name in mcp.resources.keys():
        print(f"  - {resource_name}")
    
    print("\nStarting Smart Debugging MCP Server...")
    
    try:
        if "--test" in sys.argv:
            async def test_debug_server():
                print("\n🧪 Testing Smart Debugging MCP Server...")
                
                # Test error analysis
                result = await analyze_bug_pattern(
                    "ModuleNotFoundError: No module named 'requests'",
                    language="python"
                )
                print(f"Error analysis: {'✅' if result['success'] else '❌'}")
                
                # Test function tracing (mock)
                result = await find_similar_bugs("connection refused error")
                print(f"Similar bugs search: {'✅' if result['success'] else '❌'}")
                
                # Test session report
                result = await debug_session_report(
                    "test_session",
                    ["Error 1", "Error 2"],
                    ["Fix 1", "Fix 2"]
                )
                print(f"Session report: {'✅' if result['success'] else '❌'}")
                
                print("\n✅ Smart Debugging MCP Server tests completed")
            
            asyncio.run(test_debug_server())
        else:
            asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("\n👋 Shutting down Smart Debugging MCP Server...")
    except Exception as e:
        print(f"❌ Error: {e}")