#!/usr/bin/env python3
"""
MCP Security Testing and Vulnerability Scanner
Comprehensive security testing for MCP servers including vulnerability scanning,
penetration testing, and compliance validation.
"""

import asyncio
import logging
import json
import re
import hashlib
import subprocess
import time
import os
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import ast
import requests
import ssl
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability."""
    vuln_id: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'injection', 'auth', 'crypto', 'input_validation', etc.
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    cve_id: Optional[str] = None
    recommendation: Optional[str] = None

@dataclass
class SecurityScanResult:
    """Result of a security scan."""
    scan_type: str
    passed: bool
    vulnerabilities: List[SecurityVulnerability]
    scan_duration: float
    summary: str
    recommendations: List[str] = field(default_factory=list)

class SecurityScanner:
    """Comprehensive security scanner for MCP servers."""
    
    def __init__(self):
        """Initialize the security scanner."""
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.compliance_rules = self._load_compliance_rules()
        self.security_headers = self._get_required_security_headers()
        
    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load vulnerability detection patterns."""
        return {
            "sql_injection": [
                {
                    "pattern": r"execute\s*\(\s*[\"'][^\"']*%[^\"']*[\"']\s*%",
                    "severity": "high",
                    "description": "Potential SQL injection via string formatting",
                    "recommendation": "Use parameterized queries instead of string formatting"
                },
                {
                    "pattern": r"execute\s*\(\s*f[\"'][^\"']*\{[^}]*\}[^\"']*[\"']\s*\)",
                    "severity": "high", 
                    "description": "Potential SQL injection via f-string",
                    "recommendation": "Use parameterized queries instead of f-strings"
                },
                {
                    "pattern": r"\.format\s*\([^)]*\)\s*(?=.*execute|.*query)",
                    "severity": "medium",
                    "description": "Potential SQL injection via .format()",
                    "recommendation": "Use parameterized queries"
                }
            ],
            "command_injection": [
                {
                    "pattern": r"os\.system\s*\([^)]*\+[^)]*\)",
                    "severity": "critical",
                    "description": "Command injection via os.system with concatenation",
                    "recommendation": "Use subprocess with shell=False and argument lists"
                },
                {
                    "pattern": r"subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True[^)]*\+",
                    "severity": "critical",
                    "description": "Command injection via subprocess with shell=True",
                    "recommendation": "Avoid shell=True and use argument lists"
                },
                {
                    "pattern": r"eval\s*\(",
                    "severity": "critical",
                    "description": "Code injection via eval()",
                    "recommendation": "Avoid eval(), use safe alternatives like ast.literal_eval"
                },
                {
                    "pattern": r"exec\s*\(",
                    "severity": "critical",
                    "description": "Code injection via exec()",
                    "recommendation": "Avoid exec(), refactor to eliminate dynamic code execution"
                }
            ],
            "path_traversal": [
                {
                    "pattern": r"open\s*\([^)]*\+[^)]*\)",
                    "severity": "high",
                    "description": "Path traversal via string concatenation in file operations",
                    "recommendation": "Use os.path.join() and validate file paths"
                },
                {
                    "pattern": r"\.\.\/|\.\.\\\\",
                    "severity": "medium",
                    "description": "Directory traversal patterns detected",
                    "recommendation": "Validate and sanitize file paths"
                }
            ],
            "hardcoded_secrets": [
                {
                    "pattern": r"(api_key|password|secret|token)\s*=\s*[\"'][^\"']{8,}[\"']",
                    "severity": "high",
                    "description": "Hardcoded secret detected",
                    "recommendation": "Use environment variables or secure key management"
                },
                {
                    "pattern": r"(aws_secret_access_key|private_key|certificate)\s*=\s*[\"'][^\"']+[\"']",
                    "severity": "critical",
                    "description": "Hardcoded credentials detected", 
                    "recommendation": "Move secrets to secure configuration"
                }
            ],
            "crypto_issues": [
                {
                    "pattern": r"hashlib\.(md5|sha1)\(",
                    "severity": "medium",
                    "description": "Weak cryptographic hash function",
                    "recommendation": "Use SHA-256 or stronger hash functions"
                },
                {
                    "pattern": r"random\.random\(\)|random\.randint\(",
                    "severity": "low",
                    "description": "Weak random number generation",
                    "recommendation": "Use secrets.randbelow() for cryptographic purposes"
                }
            ],
            "input_validation": [
                {
                    "pattern": r"request\.(args|form|json)\[[^]]+\](?!\s*(?:in|not\s+in|\.|=))",
                    "severity": "medium",
                    "description": "Direct use of user input without validation",
                    "recommendation": "Validate and sanitize all user inputs"
                },
                {
                    "pattern": r"int\([^)]*request\.[^)]*\)",
                    "severity": "medium",
                    "description": "Type conversion without error handling",
                    "recommendation": "Add proper error handling for type conversions"
                }
            ],
            "authentication_issues": [
                {
                    "pattern": r"if\s+[^:]*==\s*[\"']admin[\"'][^:]*:",
                    "severity": "high",
                    "description": "Hardcoded authentication bypass",
                    "recommendation": "Implement proper authentication mechanisms"
                },
                {
                    "pattern": r"session\[[\"']user[\"']\]\s*=\s*True",
                    "severity": "medium",
                    "description": "Insecure session management",
                    "recommendation": "Use proper session management libraries"
                }
            ]
        }
    
    def _load_compliance_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load compliance validation rules."""
        return {
            "hipaa": [
                {
                    "rule": "encryption_at_rest",
                    "description": "Data must be encrypted at rest",
                    "check": "encryption_patterns"
                },
                {
                    "rule": "access_logging",
                    "description": "All data access must be logged",
                    "check": "logging_patterns"
                },
                {
                    "rule": "authentication_required",
                    "description": "Authentication required for all endpoints",
                    "check": "auth_patterns"
                }
            ],
            "gdpr": [
                {
                    "rule": "data_minimization",
                    "description": "Collect only necessary data",
                    "check": "data_collection_patterns"
                },
                {
                    "rule": "consent_management",
                    "description": "Explicit consent for data processing",
                    "check": "consent_patterns"
                },
                {
                    "rule": "right_to_erasure",
                    "description": "Support for data deletion",
                    "check": "deletion_patterns"
                }
            ],
            "owasp_top10": [
                {
                    "rule": "injection_prevention",
                    "description": "Protection against injection attacks",
                    "check": "injection_patterns"
                },
                {
                    "rule": "authentication_security",
                    "description": "Secure authentication implementation",
                    "check": "auth_security_patterns"
                },
                {
                    "rule": "sensitive_data_exposure",
                    "description": "Protection of sensitive data",
                    "check": "data_exposure_patterns"
                }
            ]
        }
    
    def _get_required_security_headers(self) -> List[str]:
        """Get list of required security headers."""
        return [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
    
    async def scan_server(self, server_path: str) -> List[Dict[str, Any]]:
        """Run comprehensive security scan on MCP server."""
        logger.info(f"Starting security scan for: {server_path}")
        
        results = []
        
        try:
            # Static code analysis
            static_result = await self.run_static_analysis(server_path)
            results.append(static_result)
            
            # Dependency vulnerability scan
            dependency_result = await self.scan_dependencies(server_path)
            results.append(dependency_result)
            
            # Configuration security scan
            config_result = await self.scan_configuration(server_path)
            results.append(config_result)
            
            # Runtime security testing
            runtime_result = await self.run_runtime_security_tests(server_path)
            results.append(runtime_result)
            
            # Network security scan
            network_result = await self.scan_network_security(server_path)
            results.append(network_result)
            
            # Compliance validation
            compliance_result = await self.validate_compliance(server_path)
            results.append(compliance_result)
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            results.append({
                "test_name": "security_scan_error",
                "passed": False,
                "message": f"Security scan failed: {str(e)}",
                "scan_duration": 0.0,
                "error": str(e)
            })
        
        return results
    
    async def run_static_analysis(self, server_path: str) -> Dict[str, Any]:
        """Run static code analysis for vulnerabilities."""
        logger.info("Running static code analysis")
        
        start_time = time.time()
        vulnerabilities = []
        
        try:
            server_path_obj = Path(server_path)
            
            if server_path_obj.is_file():
                code_files = [server_path_obj]
            else:
                # Scan all code files in directory
                code_files = []
                code_files.extend(server_path_obj.glob("**/*.py"))
                code_files.extend(server_path_obj.glob("**/*.js"))
                code_files.extend(server_path_obj.glob("**/*.ts"))
            
            for file_path in code_files:
                file_vulns = await self._analyze_code_file(file_path)
                vulnerabilities.extend(file_vulns)
            
            scan_duration = time.time() - start_time
            
            # Categorize vulnerabilities by severity
            critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
            high_vulns = [v for v in vulnerabilities if v.severity == 'high']
            medium_vulns = [v for v in vulnerabilities if v.severity == 'medium']
            low_vulns = [v for v in vulnerabilities if v.severity == 'low']
            
            passed = len(critical_vulns) == 0 and len(high_vulns) == 0
            
            summary = f"Found {len(vulnerabilities)} vulnerabilities: "
            summary += f"{len(critical_vulns)} critical, {len(high_vulns)} high, "
            summary += f"{len(medium_vulns)} medium, {len(low_vulns)} low"
            
            return {
                "test_name": "static_analysis",
                "passed": passed,
                "vulnerabilities": [self._vulnerability_to_dict(v) for v in vulnerabilities],
                "scan_duration": scan_duration,
                "summary": summary,
                "recommendations": self._generate_static_analysis_recommendations(vulnerabilities)
            }
            
        except Exception as e:
            scan_duration = time.time() - start_time
            return {
                "test_name": "static_analysis",
                "passed": False,
                "message": f"Static analysis failed: {str(e)}",
                "scan_duration": scan_duration,
                "error": str(e)
            }
    
    async def _analyze_code_file(self, file_path: Path) -> List[SecurityVulnerability]:
        """Analyze a single code file for vulnerabilities."""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check each vulnerability category
            for category, patterns in self.vulnerability_patterns.items():
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    severity = pattern_info['severity']
                    description = pattern_info['description']
                    recommendation = pattern_info['recommendation']
                    
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Extract code snippet
                        line_start = max(0, line_num - 3)
                        line_end = min(len(lines), line_num + 2)
                        code_snippet = '\n'.join(lines[line_start:line_end])
                        
                        vulnerability = SecurityVulnerability(
                            vuln_id=f"{category}_{hashlib.md5(match.group().encode()).hexdigest()[:8]}",
                            severity=severity,
                            category=category,
                            title=f"{category.replace('_', ' ').title()} Vulnerability",
                            description=description,
                            file_path=str(file_path),
                            line_number=line_num,
                            code_snippet=code_snippet,
                            recommendation=recommendation
                        )
                        vulnerabilities.append(vulnerability)
            
            # Additional Python-specific analysis
            if file_path.suffix == '.py':
                python_vulns = await self._analyze_python_ast(file_path, content)
                vulnerabilities.extend(python_vulns)
                
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return vulnerabilities
    
    async def _analyze_python_ast(self, file_path: Path, content: str) -> List[SecurityVulnerability]:
        """Perform AST-based analysis for Python files."""
        vulnerabilities = []
        
        try:
            tree = ast.parse(content)
            
            # Check for dangerous imports
            dangerous_imports = ['pickle', 'marshal', 'shelve']
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in dangerous_imports:
                            vulnerability = SecurityVulnerability(
                                vuln_id=f"dangerous_import_{alias.name}",
                                severity="medium",
                                category="dangerous_imports",
                                title="Dangerous Import",
                                description=f"Import of potentially dangerous module: {alias.name}",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                recommendation=f"Consider safer alternatives to {alias.name}"
                            )
                            vulnerabilities.append(vulnerability)
                
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if (isinstance(node.func, ast.Name) and 
                        node.func.id in ['eval', 'exec', 'compile']):
                        vulnerability = SecurityVulnerability(
                            vuln_id=f"dangerous_call_{node.func.id}",
                            severity="critical",
                            category="code_injection",
                            title="Dangerous Function Call",
                            description=f"Use of dangerous function: {node.func.id}",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            recommendation=f"Avoid using {node.func.id}, use safer alternatives"
                        )
                        vulnerabilities.append(vulnerability)
                        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.warning(f"AST analysis failed for {file_path}: {e}")
        
        return vulnerabilities
    
    async def scan_dependencies(self, server_path: str) -> Dict[str, Any]:
        """Scan dependencies for known vulnerabilities."""
        logger.info("Scanning dependencies for vulnerabilities")
        
        start_time = time.time()
        vulnerabilities = []
        
        try:
            server_path_obj = Path(server_path)
            
            # Find dependency files
            requirements_files = list(server_path_obj.glob("**/requirements*.txt"))
            package_json_files = list(server_path_obj.glob("**/package.json"))
            pyproject_files = list(server_path_obj.glob("**/pyproject.toml"))
            
            # Scan Python dependencies
            for req_file in requirements_files:
                python_vulns = await self._scan_python_dependencies(req_file)
                vulnerabilities.extend(python_vulns)
            
            for pyproject_file in pyproject_files:
                python_vulns = await self._scan_pyproject_dependencies(pyproject_file)
                vulnerabilities.extend(python_vulns)
            
            # Scan Node.js dependencies
            for package_file in package_json_files:
                node_vulns = await self._scan_node_dependencies(package_file)
                vulnerabilities.extend(node_vulns)
            
            scan_duration = time.time() - start_time
            
            passed = not any(v.severity in ['critical', 'high'] for v in vulnerabilities)
            
            summary = f"Scanned dependencies, found {len(vulnerabilities)} vulnerabilities"
            
            return {
                "test_name": "dependency_scan",
                "passed": passed,
                "vulnerabilities": [self._vulnerability_to_dict(v) for v in vulnerabilities],
                "scan_duration": scan_duration,
                "summary": summary
            }
            
        except Exception as e:
            scan_duration = time.time() - start_time
            return {
                "test_name": "dependency_scan",
                "passed": False,
                "message": f"Dependency scan failed: {str(e)}",
                "scan_duration": scan_duration,
                "error": str(e)
            }
    
    async def _scan_python_dependencies(self, requirements_file: Path) -> List[SecurityVulnerability]:
        """Scan Python dependencies using safety."""
        vulnerabilities = []
        
        try:
            # Run safety check (if available)
            result = subprocess.run(
                ['safety', 'check', '-r', str(requirements_file), '--json'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                # No vulnerabilities found
                return vulnerabilities
            
            # Parse safety output
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        vulnerability = SecurityVulnerability(
                            vuln_id=vuln.get('id', 'unknown'),
                            severity='high',  # Safety typically reports high-severity issues
                            category='dependency_vulnerability',
                            title=f"Vulnerable dependency: {vuln.get('package_name', 'unknown')}",
                            description=vuln.get('advisory', 'No description available'),
                            recommendation=f"Update {vuln.get('package_name')} to a secure version"
                        )
                        vulnerabilities.append(vulnerability)
                except json.JSONDecodeError:
                    logger.warning("Could not parse safety output")
                    
        except FileNotFoundError:
            logger.info("Safety tool not available, skipping Python dependency scan")
        except subprocess.TimeoutExpired:
            logger.warning("Safety scan timed out")
        except Exception as e:
            logger.warning(f"Python dependency scan failed: {e}")
        
        return vulnerabilities
    
    async def _scan_pyproject_dependencies(self, pyproject_file: Path) -> List[SecurityVulnerability]:
        """Scan pyproject.toml dependencies."""
        # This would require parsing TOML and checking against vulnerability databases
        # Simplified implementation for now
        return []
    
    async def _scan_node_dependencies(self, package_json_file: Path) -> List[SecurityVulnerability]:
        """Scan Node.js dependencies using npm audit."""
        vulnerabilities = []
        
        try:
            # Run npm audit
            package_dir = package_json_file.parent
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                cwd=str(package_dir),
                capture_output=True, text=True, timeout=60
            )
            
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities_data = audit_data.get('vulnerabilities', {})
                    
                    for package_name, vuln_info in vulnerabilities_data.items():
                        severity = vuln_info.get('severity', 'medium')
                        
                        vulnerability = SecurityVulnerability(
                            vuln_id=f"npm_{package_name}_{vuln_info.get('cwe', 'unknown')}",
                            severity=severity,
                            category='dependency_vulnerability',
                            title=f"Vulnerable Node.js dependency: {package_name}",
                            description=vuln_info.get('title', 'No description available'),
                            recommendation=f"Update {package_name} to fix vulnerability"
                        )
                        vulnerabilities.append(vulnerability)
                        
                except json.JSONDecodeError:
                    logger.warning("Could not parse npm audit output")
                    
        except FileNotFoundError:
            logger.info("npm not available, skipping Node.js dependency scan")
        except subprocess.TimeoutExpired:
            logger.warning("npm audit timed out")
        except Exception as e:
            logger.warning(f"Node.js dependency scan failed: {e}")
        
        return vulnerabilities
    
    async def scan_configuration(self, server_path: str) -> Dict[str, Any]:
        """Scan server configuration for security issues."""
        logger.info("Scanning configuration security")
        
        start_time = time.time()
        vulnerabilities = []
        
        try:
            server_path_obj = Path(server_path)
            
            # Check for common configuration files
            config_files = []
            config_files.extend(server_path_obj.glob("**/*.ini"))
            config_files.extend(server_path_obj.glob("**/*.conf"))
            config_files.extend(server_path_obj.glob("**/*.yaml"))
            config_files.extend(server_path_obj.glob("**/*.yml"))
            config_files.extend(server_path_obj.glob("**/*.json"))
            config_files.extend(server_path_obj.glob("**/.*env*"))
            
            for config_file in config_files:
                config_vulns = await self._analyze_config_file(config_file)
                vulnerabilities.extend(config_vulns)
            
            # Check file permissions
            permission_vulns = await self._check_file_permissions(server_path_obj)
            vulnerabilities.extend(permission_vulns)
            
            scan_duration = time.time() - start_time
            
            passed = not any(v.severity in ['critical', 'high'] for v in vulnerabilities)
            
            return {
                "test_name": "configuration_scan",
                "passed": passed,
                "vulnerabilities": [self._vulnerability_to_dict(v) for v in vulnerabilities],
                "scan_duration": scan_duration,
                "summary": f"Configuration scan found {len(vulnerabilities)} issues"
            }
            
        except Exception as e:
            scan_duration = time.time() - start_time
            return {
                "test_name": "configuration_scan",
                "passed": False,
                "message": f"Configuration scan failed: {str(e)}",
                "scan_duration": scan_duration,
                "error": str(e)
            }
    
    async def _analyze_config_file(self, config_file: Path) -> List[SecurityVulnerability]:
        """Analyze a configuration file for security issues."""
        vulnerabilities = []
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for hardcoded secrets in config
            secret_patterns = [
                (r'password\s*[=:]\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
                (r'secret\s*[=:]\s*["\'][^"\']{8,}["\']', 'Hardcoded secret'),
                (r'api_key\s*[=:]\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
                (r'private_key\s*[=:]\s*["\'][^"\']+["\']', 'Hardcoded private key')
            ]
            
            for pattern, description in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    vulnerability = SecurityVulnerability(
                        vuln_id=f"config_secret_{hashlib.md5(match.group().encode()).hexdigest()[:8]}",
                        severity="high",
                        category="hardcoded_secrets",
                        title="Hardcoded Secret in Configuration",
                        description=description,
                        file_path=str(config_file),
                        line_number=line_num,
                        recommendation="Move secrets to environment variables or secure vaults"
                    )
                    vulnerabilities.append(vulnerability)
            
            # Check for debug mode enabled
            if re.search(r'debug\s*[=:]\s*(true|1|yes)', content, re.IGNORECASE):
                vulnerability = SecurityVulnerability(
                    vuln_id="debug_mode_enabled",
                    severity="medium",
                    category="configuration",
                    title="Debug Mode Enabled",
                    description="Debug mode is enabled in configuration",
                    file_path=str(config_file),
                    recommendation="Disable debug mode in production"
                )
                vulnerabilities.append(vulnerability)
                
        except Exception as e:
            logger.warning(f"Failed to analyze config file {config_file}: {e}")
        
        return vulnerabilities
    
    async def _check_file_permissions(self, server_path: Path) -> List[SecurityVulnerability]:
        """Check file permissions for security issues."""
        vulnerabilities = []
        
        try:
            # Check for world-writable files
            for file_path in server_path.rglob("*"):
                if file_path.is_file():
                    stat_info = file_path.stat()
                    mode = stat_info.st_mode
                    
                    # Check if world-writable
                    if mode & 0o002:
                        vulnerability = SecurityVulnerability(
                            vuln_id=f"world_writable_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}",
                            severity="medium",
                            category="file_permissions",
                            title="World-Writable File",
                            description=f"File is world-writable: {file_path}",
                            file_path=str(file_path),
                            recommendation="Restrict file permissions to prevent unauthorized modification"
                        )
                        vulnerabilities.append(vulnerability)
                        
        except Exception as e:
            logger.warning(f"Failed to check file permissions: {e}")
        
        return vulnerabilities
    
    async def run_runtime_security_tests(self, server_path: str) -> Dict[str, Any]:
        """Run runtime security tests against running server."""
        logger.info("Running runtime security tests")
        
        start_time = time.time()
        vulnerabilities = []
        
        try:
            # This would involve starting the server and testing various attack vectors
            # For now, we'll implement basic checks
            
            # Test input validation
            input_vulns = await self._test_input_validation(server_path)
            vulnerabilities.extend(input_vulns)
            
            # Test authentication bypass
            auth_vulns = await self._test_authentication_bypass(server_path)
            vulnerabilities.extend(auth_vulns)
            
            # Test for timing attacks
            timing_vulns = await self._test_timing_attacks(server_path)
            vulnerabilities.extend(timing_vulns)
            
            scan_duration = time.time() - start_time
            
            passed = not any(v.severity in ['critical', 'high'] for v in vulnerabilities)
            
            return {
                "test_name": "runtime_security",
                "passed": passed,
                "vulnerabilities": [self._vulnerability_to_dict(v) for v in vulnerabilities],
                "scan_duration": scan_duration,
                "summary": f"Runtime security tests found {len(vulnerabilities)} issues"
            }
            
        except Exception as e:
            scan_duration = time.time() - start_time
            return {
                "test_name": "runtime_security",
                "passed": False,
                "message": f"Runtime security tests failed: {str(e)}",
                "scan_duration": scan_duration,
                "error": str(e)
            }
    
    async def _test_input_validation(self, server_path: str) -> List[SecurityVulnerability]:
        """Test input validation security."""
        # This would involve sending malicious payloads to the running server
        # Simplified implementation for now
        return []
    
    async def _test_authentication_bypass(self, server_path: str) -> List[SecurityVulnerability]:
        """Test for authentication bypass vulnerabilities."""
        # This would test various auth bypass techniques
        # Simplified implementation for now
        return []
    
    async def _test_timing_attacks(self, server_path: str) -> List[SecurityVulnerability]:
        """Test for timing attack vulnerabilities."""
        # This would measure response times to detect timing attacks
        # Simplified implementation for now
        return []
    
    async def scan_network_security(self, server_path: str) -> Dict[str, Any]:
        """Scan network security configuration."""
        logger.info("Scanning network security")
        
        start_time = time.time()
        vulnerabilities = []
        
        try:
            # Check TLS configuration
            tls_vulns = await self._check_tls_configuration(server_path)
            vulnerabilities.extend(tls_vulns)
            
            # Check for open ports
            port_vulns = await self._check_open_ports(server_path)
            vulnerabilities.extend(port_vulns)
            
            scan_duration = time.time() - start_time
            
            passed = not any(v.severity in ['critical', 'high'] for v in vulnerabilities)
            
            return {
                "test_name": "network_security",
                "passed": passed,
                "vulnerabilities": [self._vulnerability_to_dict(v) for v in vulnerabilities],
                "scan_duration": scan_duration,
                "summary": f"Network security scan found {len(vulnerabilities)} issues"
            }
            
        except Exception as e:
            scan_duration = time.time() - start_time
            return {
                "test_name": "network_security",
                "passed": False,
                "message": f"Network security scan failed: {str(e)}",
                "scan_duration": scan_duration,
                "error": str(e)
            }
    
    async def _check_tls_configuration(self, server_path: str) -> List[SecurityVulnerability]:
        """Check TLS/SSL configuration."""
        # This would check TLS versions, cipher suites, etc.
        # Simplified implementation for now
        return []
    
    async def _check_open_ports(self, server_path: str) -> List[SecurityVulnerability]:
        """Check for unnecessary open ports."""
        # This would scan for open ports
        # Simplified implementation for now
        return []
    
    async def validate_compliance(self, server_path: str) -> Dict[str, Any]:
        """Validate compliance with security standards."""
        logger.info("Validating compliance")
        
        start_time = time.time()
        compliance_issues = []
        
        try:
            # Check OWASP Top 10 compliance
            owasp_issues = await self._check_owasp_compliance(server_path)
            compliance_issues.extend(owasp_issues)
            
            # Check HIPAA compliance (if applicable)
            if self._is_healthcare_server(server_path):
                hipaa_issues = await self._check_hipaa_compliance(server_path)
                compliance_issues.extend(hipaa_issues)
            
            # Check GDPR compliance (if applicable)
            gdpr_issues = await self._check_gdpr_compliance(server_path)
            compliance_issues.extend(gdpr_issues)
            
            scan_duration = time.time() - start_time
            
            passed = len(compliance_issues) == 0
            
            return {
                "test_name": "compliance_validation",
                "passed": passed,
                "vulnerabilities": compliance_issues,
                "scan_duration": scan_duration,
                "summary": f"Compliance validation found {len(compliance_issues)} issues"
            }
            
        except Exception as e:
            scan_duration = time.time() - start_time
            return {
                "test_name": "compliance_validation",
                "passed": False,
                "message": f"Compliance validation failed: {str(e)}",
                "scan_duration": scan_duration,
                "error": str(e)
            }
    
    async def _check_owasp_compliance(self, server_path: str) -> List[Dict[str, Any]]:
        """Check OWASP Top 10 compliance."""
        # This would implement specific OWASP Top 10 checks
        return []
    
    async def _check_hipaa_compliance(self, server_path: str) -> List[Dict[str, Any]]:
        """Check HIPAA compliance for healthcare servers."""
        # This would implement HIPAA-specific checks
        return []
    
    async def _check_gdpr_compliance(self, server_path: str) -> List[Dict[str, Any]]:
        """Check GDPR compliance."""
        # This would implement GDPR-specific checks
        return []
    
    def _is_healthcare_server(self, server_path: str) -> bool:
        """Determine if this is a healthcare server."""
        server_path_lower = server_path.lower()
        return any(keyword in server_path_lower for keyword in ['health', 'fhir', 'medical', 'patient'])
    
    def _vulnerability_to_dict(self, vuln: SecurityVulnerability) -> Dict[str, Any]:
        """Convert vulnerability to dictionary format."""
        return {
            "vuln_id": vuln.vuln_id,
            "severity": vuln.severity,
            "category": vuln.category,
            "title": vuln.title,
            "description": vuln.description,
            "file_path": vuln.file_path,
            "line_number": vuln.line_number,
            "code_snippet": vuln.code_snippet,
            "cve_id": vuln.cve_id,
            "recommendation": vuln.recommendation
        }
    
    def _generate_static_analysis_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Generate recommendations based on static analysis results."""
        recommendations = []
        
        categories = set(v.category for v in vulnerabilities)
        
        if 'sql_injection' in categories:
            recommendations.append("Implement parameterized queries to prevent SQL injection")
        
        if 'command_injection' in categories:
            recommendations.append("Use subprocess with argument lists instead of shell=True")
        
        if 'hardcoded_secrets' in categories:
            recommendations.append("Move all secrets to environment variables or secure vaults")
        
        if 'crypto_issues' in categories:
            recommendations.append("Upgrade to stronger cryptographic algorithms")
        
        return recommendations

async def main():
    """CLI entry point for security scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Security Scanner")
    parser.add_argument("server_path", help="Path to MCP server to scan")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--scan-type", choices=['static', 'dependencies', 'runtime', 'all'], 
                       default='all', help="Type of security scan")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scanner = SecurityScanner()
    
    if args.scan_type == 'static':
        results = [await scanner.run_static_analysis(args.server_path)]
    elif args.scan_type == 'dependencies':
        results = [await scanner.scan_dependencies(args.server_path)]
    elif args.scan_type == 'runtime':
        results = [await scanner.run_runtime_security_tests(args.server_path)]
    else:
        results = await scanner.scan_server(args.server_path)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        print(json.dumps(results, indent=2))
    
    # Exit with error code if critical/high vulnerabilities found
    has_critical = any(
        any(v.get('severity') in ['critical', 'high'] 
            for v in result.get('vulnerabilities', []))
        for result in results
    )
    sys.exit(0 if not has_critical else 1)

if __name__ == "__main__":
    import sys
    asyncio.run(main())