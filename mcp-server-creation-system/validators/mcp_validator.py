#!/usr/bin/env python3
"""
MCP Server Validation Framework
Validates MCP server implementations against best practices and standards.
"""

import ast
import json
import yaml
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field
import logging
from datetime import datetime
import subprocess
import tempfile

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    severity: str  # 'error', 'warning', 'info'
    category: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class ServerValidationReport:
    """Comprehensive validation report for an MCP server."""
    server_path: str
    overall_score: float
    passed: bool
    results: List[ValidationResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_result(self, result: ValidationResult):
        """Add a validation result."""
        self.results.append(result)
    
    def get_errors(self) -> List[ValidationResult]:
        """Get all error-level results."""
        return [r for r in self.results if r.severity == 'error']
    
    def get_warnings(self) -> List[ValidationResult]:
        """Get all warning-level results."""
        return [r for r in self.results if r.severity == 'warning']
    
    def calculate_score(self):
        """Calculate overall validation score."""
        if not self.results:
            self.overall_score = 0.0
            return
        
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        error_penalty = len(self.get_errors()) * 0.1
        warning_penalty = len(self.get_warnings()) * 0.05
        
        base_score = (passed_checks / total_checks) * 100
        final_score = max(0, base_score - (error_penalty * 100) - (warning_penalty * 100))
        
        self.overall_score = round(final_score, 2)
        self.passed = len(self.get_errors()) == 0 and final_score >= 70.0

class MCPValidator:
    """Validates MCP server implementations for compliance and best practices."""
    
    def __init__(self):
        self.security_patterns = self.load_security_patterns()
        self.required_methods = self.load_required_methods()
        self.best_practices = self.load_best_practices()
    
    def load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security vulnerability patterns to check for."""
        return {
            "sql_injection": [
                r"execute\s*\(\s*[\"'].*%.*[\"']",  # String formatting in SQL
                r"execute\s*\(\s*f[\"'].*\{.*\}.*[\"']",  # f-strings in SQL
                r"\.format\s*\(.*\)\s*(?=.*execute|.*query)"  # .format() with SQL
            ],
            "command_injection": [
                r"os\.system\s*\(.*\+",  # String concatenation with os.system
                r"subprocess\.(call|run|Popen)\s*\(.*\+",  # String concat with subprocess
                r"eval\s*\(",  # eval() usage
                r"exec\s*\("   # exec() usage
            ],
            "path_traversal": [
                r"open\s*\(.*\+",  # String concatenation in file operations
                r"\.\.\/",  # Directory traversal patterns
                r"\.\.\\",  # Windows directory traversal
            ],
            "hardcoded_secrets": [
                r"api_key\s*=\s*[\"'][^\"']{20,}[\"']",  # Hardcoded API keys
                r"password\s*=\s*[\"'][^\"']+[\"']",  # Hardcoded passwords
                r"secret\s*=\s*[\"'][^\"']{10,}[\"']",  # Hardcoded secrets
                r"token\s*=\s*[\"'][^\"']{20,}[\"']"   # Hardcoded tokens
            ]
        }
    
    def load_required_methods(self) -> Dict[str, List[str]]:
        """Load required methods for different MCP capabilities."""
        return {
            "tools": [
                "list_tools",
                "call_tool"
            ],
            "resources": [
                "list_resources", 
                "read_resource"
            ],
            "prompts": [
                "list_prompts",
                "get_prompt"
            ],
            "common": [
                "__init__",
                "setup_handlers",
                "run"
            ]
        }
    
    def load_best_practices(self) -> Dict[str, Any]:
        """Load MCP best practice guidelines."""
        return {
            "error_handling": {
                "required_exceptions": ["Exception", "ValueError", "TypeError"],
                "logging_required": True,
                "graceful_degradation": True
            },
            "performance": {
                "async_required": True,
                "connection_pooling": True,
                "rate_limiting": True
            },
            "documentation": {
                "docstrings_required": True,
                "type_hints_required": True,
                "examples_required": True
            },
            "testing": {
                "unit_tests_required": True,
                "integration_tests_required": True,
                "coverage_minimum": 80
            }
        }
    
    def validate_server(self, server_path: str) -> ServerValidationReport:
        """Perform comprehensive validation of an MCP server."""
        server_path = Path(server_path)
        report = ServerValidationReport(server_path=str(server_path))
        
        if not server_path.exists():
            report.add_result(ValidationResult(
                passed=False,
                message=f"Server path does not exist: {server_path}",
                severity="error",
                category="structure"
            ))
            report.calculate_score()
            return report
        
        # Validate structure
        self._validate_structure(server_path, report)
        
        # Validate Python code (if applicable)
        python_files = list(server_path.glob("*.py"))
        for py_file in python_files:
            self._validate_python_file(py_file, report)
        
        # Validate TypeScript code (if applicable)
        ts_files = list(server_path.glob("*.ts"))
        for ts_file in ts_files:
            self._validate_typescript_file(ts_file, report)
        
        # Validate configuration files
        self._validate_configuration(server_path, report)
        
        # Validate security
        self._validate_security(server_path, report)
        
        # Validate documentation
        self._validate_documentation(server_path, report)
        
        # Validate tests
        self._validate_tests(server_path, report)
        
        # Generate recommendations
        self._generate_recommendations(report)
        
        report.calculate_score()
        return report
    
    def _validate_structure(self, server_path: Path, report: ServerValidationReport):
        """Validate server directory structure."""
        
        # Check for main server files
        python_servers = list(server_path.glob("*_server.py"))
        ts_servers = list(server_path.glob("*.ts"))
        
        if not python_servers and not ts_servers:
            report.add_result(ValidationResult(
                passed=False,
                message="No server implementation file found (expected *_server.py or *.ts)",
                severity="error",
                category="structure"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message="Server implementation file found",
                severity="info",
                category="structure"
            ))
        
        # Check for README
        readme_files = list(server_path.glob("README*"))
        if not readme_files:
            report.add_result(ValidationResult(
                passed=False,
                message="README file missing",
                severity="warning",
                category="documentation"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message="README file present",
                severity="info",
                category="documentation"
            ))
        
        # Check for configuration files
        config_files = (
            list(server_path.glob("pyproject.toml")) +
            list(server_path.glob("package.json")) +
            list(server_path.glob("requirements.txt"))
        )
        
        if not config_files:
            report.add_result(ValidationResult(
                passed=False,
                message="No configuration files found (pyproject.toml, package.json, or requirements.txt)",
                severity="warning",
                category="configuration"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message=f"Configuration files found: {[f.name for f in config_files]}",
                severity="info",
                category="configuration"
            ))
    
    def _validate_python_file(self, file_path: Path, report: ServerValidationReport):
        """Validate Python server implementation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Syntax error in {file_path.name}: {e}",
                    severity="error",
                    category="syntax"
                ))
                return
            
            # Validate MCP imports
            self._validate_mcp_imports(content, report)
            
            # Validate class structure
            self._validate_class_structure(tree, report)
            
            # Validate required methods
            self._validate_required_methods(tree, report)
            
            # Validate error handling
            self._validate_error_handling(tree, content, report)
            
            # Validate async usage
            self._validate_async_usage(tree, report)
            
            # Validate type hints
            self._validate_type_hints(tree, report)
            
            # Validate docstrings
            self._validate_docstrings(tree, report)
            
        except Exception as e:
            report.add_result(ValidationResult(
                passed=False,
                message=f"Failed to validate {file_path.name}: {e}",
                severity="error",
                category="validation"
            ))
    
    def _validate_typescript_file(self, file_path: Path, report: ServerValidationReport):
        """Validate TypeScript server implementation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for MCP SDK imports
            if '@modelcontextprotocol/sdk' not in content:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Missing MCP SDK import in {file_path.name}",
                    severity="error",
                    category="imports"
                ))
            else:
                report.add_result(ValidationResult(
                    passed=True,
                    message=f"MCP SDK import found in {file_path.name}",
                    severity="info",
                    category="imports"
                ))
            
            # Check for server class
            if 'class ' in content and 'Server' in content:
                report.add_result(ValidationResult(
                    passed=True,
                    message="Server class found",
                    severity="info",
                    category="structure"
                ))
            else:
                report.add_result(ValidationResult(
                    passed=False,
                    message="No server class found",
                    severity="error",
                    category="structure"
                ))
            
            # Check for async/await usage
            if 'async ' in content and 'await ' in content:
                report.add_result(ValidationResult(
                    passed=True,
                    message="Async/await patterns found",
                    severity="info",
                    category="performance"
                ))
            else:
                report.add_result(ValidationResult(
                    passed=False,
                    message="No async/await patterns found",
                    severity="warning",
                    category="performance"
                ))
            
        except Exception as e:
            report.add_result(ValidationResult(
                passed=False,
                message=f"Failed to validate {file_path.name}: {e}",
                severity="error",
                category="validation"
            ))
    
    def _validate_mcp_imports(self, content: str, report: ServerValidationReport):
        """Validate MCP-related imports."""
        required_imports = [
            'mcp.server',
            'mcp.types',
            'mcp.server.stdio'
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            report.add_result(ValidationResult(
                passed=False,
                message=f"Missing required MCP imports: {missing_imports}",
                severity="error",
                category="imports"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message="All required MCP imports found",
                severity="info",
                category="imports"
            ))
    
    def _validate_class_structure(self, tree: ast.AST, report: ServerValidationReport):
        """Validate server class structure."""
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        if not classes:
            report.add_result(ValidationResult(
                passed=False,
                message="No class definitions found",
                severity="error",
                category="structure"
            ))
            return
        
        # Look for server class (usually ends with 'Server')
        server_classes = [cls for cls in classes if cls.name.endswith('Server')]
        
        if not server_classes:
            report.add_result(ValidationResult(
                passed=False,
                message="No server class found (expected class name ending with 'Server')",
                severity="warning",
                category="structure"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message=f"Server class found: {server_classes[0].name}",
                severity="info",
                category="structure"
            ))
    
    def _validate_required_methods(self, tree: ast.AST, report: ServerValidationReport):
        """Validate presence of required MCP methods."""
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                methods.append(node.name)
        
        # Check for common required methods
        required_common = self.required_methods['common']
        missing_common = [method for method in required_common if method not in methods]
        
        if missing_common:
            report.add_result(ValidationResult(
                passed=False,
                message=f"Missing required common methods: {missing_common}",
                severity="error",
                category="methods"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message="All required common methods found",
                severity="info",
                category="methods"
            ))
        
        # Check for capability-specific methods
        for capability, required_methods in self.required_methods.items():
            if capability == 'common':
                continue
            
            # If any methods from this capability are present, all should be present
            capability_methods = [method for method in required_methods if method in methods]
            if capability_methods and len(capability_methods) < len(required_methods):
                missing = [method for method in required_methods if method not in methods]
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Incomplete {capability} implementation, missing: {missing}",
                    severity="error",
                    category="methods"
                ))
    
    def _validate_error_handling(self, tree: ast.AST, content: str, report: ServerValidationReport):
        """Validate error handling patterns."""
        # Check for try/except blocks
        try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        
        if not try_blocks:
            report.add_result(ValidationResult(
                passed=False,
                message="No error handling (try/except blocks) found",
                severity="warning",
                category="error_handling"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message=f"Found {len(try_blocks)} try/except blocks",
                severity="info",
                category="error_handling"
            ))
        
        # Check for logging
        if 'logger.' in content or 'logging.' in content:
            report.add_result(ValidationResult(
                passed=True,
                message="Logging usage found",
                severity="info",
                category="error_handling"
            ))
        else:
            report.add_result(ValidationResult(
                passed=False,
                message="No logging usage found",
                severity="warning",
                category="error_handling"
            ))
    
    def _validate_async_usage(self, tree: ast.AST, report: ServerValidationReport):
        """Validate async/await usage."""
        async_functions = [node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)]
        
        if not async_functions:
            report.add_result(ValidationResult(
                passed=False,
                message="No async functions found (required for MCP servers)",
                severity="error",
                category="performance"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message=f"Found {len(async_functions)} async functions",
                severity="info",
                category="performance"
            ))
    
    def _validate_type_hints(self, tree: ast.AST, report: ServerValidationReport):
        """Validate type hint usage."""
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        
        functions_with_hints = 0
        for func in functions:
            if func.returns or any(arg.annotation for arg in func.args.args):
                functions_with_hints += 1
        
        if functions and functions_with_hints / len(functions) < 0.5:
            report.add_result(ValidationResult(
                passed=False,
                message=f"Limited type hint usage ({functions_with_hints}/{len(functions)} functions)",
                severity="warning",
                category="documentation"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message=f"Good type hint usage ({functions_with_hints}/{len(functions)} functions)",
                severity="info",
                category="documentation"
            ))
    
    def _validate_docstrings(self, tree: ast.AST, report: ServerValidationReport):
        """Validate docstring usage."""
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        functions_with_docstrings = 0
        for func in functions:
            if (func.body and 
                isinstance(func.body[0], ast.Expr) and 
                isinstance(func.body[0].value, ast.Constant) and 
                isinstance(func.body[0].value.value, str)):
                functions_with_docstrings += 1
        
        classes_with_docstrings = 0
        for cls in classes:
            if (cls.body and 
                isinstance(cls.body[0], ast.Expr) and 
                isinstance(cls.body[0].value, ast.Constant) and 
                isinstance(cls.body[0].value.value, str)):
                classes_with_docstrings += 1
        
        total_definitions = len(functions) + len(classes)
        documented_definitions = functions_with_docstrings + classes_with_docstrings
        
        if total_definitions > 0:
            documentation_ratio = documented_definitions / total_definitions
            if documentation_ratio < 0.7:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Limited documentation ({documented_definitions}/{total_definitions} definitions have docstrings)",
                    severity="warning",
                    category="documentation"
                ))
            else:
                report.add_result(ValidationResult(
                    passed=True,
                    message=f"Good documentation coverage ({documented_definitions}/{total_definitions} definitions have docstrings)",
                    severity="info",
                    category="documentation"
                ))
    
    def _validate_configuration(self, server_path: Path, report: ServerValidationReport):
        """Validate configuration files."""
        
        # Check Python configuration
        pyproject_file = server_path / "pyproject.toml"
        requirements_file = server_path / "requirements.txt"
        
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    if 'mcp' not in content:
                        report.add_result(ValidationResult(
                            passed=False,
                            message="MCP dependency not found in pyproject.toml",
                            severity="warning",
                            category="configuration"
                        ))
                    else:
                        report.add_result(ValidationResult(
                            passed=True,
                            message="MCP dependency found in pyproject.toml",
                            severity="info",
                            category="configuration"
                        ))
            except Exception as e:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Error reading pyproject.toml: {e}",
                    severity="error",
                    category="configuration"
                ))
        
        # Check TypeScript configuration
        package_json = server_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    if '@modelcontextprotocol/sdk' not in deps:
                        report.add_result(ValidationResult(
                            passed=False,
                            message="MCP SDK dependency not found in package.json",
                            severity="warning",
                            category="configuration"
                        ))
                    else:
                        report.add_result(ValidationResult(
                            passed=True,
                            message="MCP SDK dependency found in package.json",
                            severity="info",
                            category="configuration"
                        ))
            except Exception as e:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Error reading package.json: {e}",
                    severity="error",
                    category="configuration"
                ))
    
    def _validate_security(self, server_path: Path, report: ServerValidationReport):
        """Validate security practices."""
        
        # Check all code files for security issues
        code_files = list(server_path.glob("*.py")) + list(server_path.glob("*.ts"))
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for vulnerability_type, patterns in self.security_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            report.add_result(ValidationResult(
                                passed=False,
                                message=f"Potential {vulnerability_type.replace('_', ' ')} vulnerability in {file_path.name}",
                                severity="error",
                                category="security",
                                details={"pattern": pattern, "file": str(file_path)}
                            ))
            
            except Exception as e:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Error scanning {file_path.name} for security issues: {e}",
                    severity="warning",
                    category="security"
                ))
        
        # Check for .gitignore to prevent secret leakage
        gitignore = server_path / ".gitignore"
        if not gitignore.exists():
            report.add_result(ValidationResult(
                passed=False,
                message=".gitignore file missing (may lead to secret exposure)",
                severity="warning",
                category="security"
            ))
        else:
            # Check if common secret files are ignored
            with open(gitignore, 'r') as f:
                gitignore_content = f.read()
            
            secret_patterns = ['.env', '*.key', '*.pem', 'config.json']
            missing_patterns = [p for p in secret_patterns if p not in gitignore_content]
            
            if missing_patterns:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Security: Consider adding to .gitignore: {missing_patterns}",
                    severity="warning",
                    category="security"
                ))
    
    def _validate_documentation(self, server_path: Path, report: ServerValidationReport):
        """Validate documentation quality."""
        
        readme_files = list(server_path.glob("README*"))
        if readme_files:
            readme_file = readme_files[0]
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for essential sections
                essential_sections = ['installation', 'usage', 'configuration']
                missing_sections = []
                
                for section in essential_sections:
                    if section.lower() not in content.lower():
                        missing_sections.append(section)
                
                if missing_sections:
                    report.add_result(ValidationResult(
                        passed=False,
                        message=f"README missing sections: {missing_sections}",
                        severity="warning",
                        category="documentation"
                    ))
                else:
                    report.add_result(ValidationResult(
                        passed=True,
                        message="README contains essential sections",
                        severity="info",
                        category="documentation"
                    ))
                
                # Check for examples
                if 'example' not in content.lower():
                    report.add_result(ValidationResult(
                        passed=False,
                        message="README lacks usage examples",
                        severity="warning",
                        category="documentation"
                    ))
                
            except Exception as e:
                report.add_result(ValidationResult(
                    passed=False,
                    message=f"Error reading README: {e}",
                    severity="error",
                    category="documentation"
                ))
    
    def _validate_tests(self, server_path: Path, report: ServerValidationReport):
        """Validate test coverage and quality."""
        
        test_dirs = [server_path / "tests", server_path / "test"]
        test_files = []
        
        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(list(test_dir.glob("test_*.py")))
                test_files.extend(list(test_dir.glob("*.test.ts")))
        
        # Also check for test files in root
        test_files.extend(list(server_path.glob("test_*.py")))
        test_files.extend(list(server_path.glob("*.test.ts")))
        
        if not test_files:
            report.add_result(ValidationResult(
                passed=False,
                message="No test files found",
                severity="warning",
                category="testing"
            ))
        else:
            report.add_result(ValidationResult(
                passed=True,
                message=f"Found {len(test_files)} test files",
                severity="info",
                category="testing"
            ))
            
            # Check test quality
            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for async test patterns
                    if test_file.suffix == '.py' and 'async def test_' in content:
                        report.add_result(ValidationResult(
                            passed=True,
                            message=f"Async tests found in {test_file.name}",
                            severity="info",
                            category="testing"
                        ))
                    
                    # Check for assertion patterns
                    assertion_patterns = ['assert ', 'expect(', 'assertEqual', 'assertTrue']
                    if not any(pattern in content for pattern in assertion_patterns):
                        report.add_result(ValidationResult(
                            passed=False,
                            message=f"No assertions found in {test_file.name}",
                            severity="warning",
                            category="testing"
                        ))
                
                except Exception as e:
                    report.add_result(ValidationResult(
                        passed=False,
                        message=f"Error reading test file {test_file.name}: {e}",
                        severity="warning",
                        category="testing"
                    ))
    
    def _generate_recommendations(self, report: ServerValidationReport):
        """Generate recommendations based on validation results."""
        
        errors = report.get_errors()
        warnings = report.get_warnings()
        
        # Priority recommendations based on errors
        if any(r.category == "security" for r in errors):
            report.recommendations.append("🔒 CRITICAL: Fix security vulnerabilities immediately")
        
        if any(r.category == "syntax" for r in errors):
            report.recommendations.append("🐛 Fix syntax errors before deployment")
        
        if any(r.category == "imports" for r in errors):
            report.recommendations.append("📦 Add missing MCP dependencies")
        
        # Quality improvements based on warnings
        if any(r.category == "documentation" for r in warnings):
            report.recommendations.append("📚 Improve documentation coverage and quality")
        
        if any(r.category == "testing" for r in warnings):
            report.recommendations.append("🧪 Add comprehensive test coverage")
        
        if any(r.category == "error_handling" for r in warnings):
            report.recommendations.append("🛡️ Implement better error handling and logging")
        
        if any(r.category == "performance" for r in warnings):
            report.recommendations.append("⚡ Optimize performance with async patterns")
        
        # General recommendations
        if report.overall_score < 90:
            report.recommendations.append("🎯 Consider refactoring to improve code quality")
        
        if report.overall_score >= 90:
            report.recommendations.append("🌟 Excellent implementation! Consider contributing to the MCP ecosystem")
    
    def generate_report_markdown(self, report: ServerValidationReport) -> str:
        """Generate a markdown report."""
        
        status_emoji = "✅" if report.passed else "❌"
        score_color = "🟢" if report.overall_score >= 80 else "🟡" if report.overall_score >= 60 else "🔴"
        
        md = f"""# MCP Server Validation Report
        
{status_emoji} **Overall Status**: {'PASSED' if report.passed else 'FAILED'}
{score_color} **Score**: {report.overall_score}/100

**Server Path**: `{report.server_path}`
**Generated**: {report.timestamp}

## Summary

- **Total Checks**: {len(report.results)}
- **Passed**: {sum(1 for r in report.results if r.passed)}
- **Failed**: {sum(1 for r in report.results if not r.passed)}
- **Errors**: {len(report.get_errors())}
- **Warnings**: {len(report.get_warnings())}

## Recommendations

"""
        
        for rec in report.recommendations:
            md += f"- {rec}\n"
        
        md += "\n## Detailed Results\n\n"
        
        # Group results by category
        categories = {}
        for result in report.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        for category, results in categories.items():
            md += f"### {category.title()}\n\n"
            
            for result in results:
                status = "✅" if result.passed else "❌"
                severity_emoji = {"error": "🚨", "warning": "⚠️", "info": "ℹ️"}[result.severity]
                
                md += f"- {status} {severity_emoji} **{result.severity.upper()}**: {result.message}\n"
            
            md += "\n"
        
        return md

def main():
    """CLI interface for MCP server validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate MCP server implementations")
    parser.add_argument('server_path', help="Path to MCP server directory")
    parser.add_argument('--output', help="Output file for validation report")
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown', help="Report format")
    
    args = parser.parse_args()
    
    validator = MCPValidator()
    report = validator.validate_server(args.server_path)
    
    if args.format == 'json':
        output = json.dumps(report.__dict__, indent=2, default=str)
    else:
        output = validator.generate_report_markdown(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to: {args.output}")
    else:
        print(output)
    
    # Exit with error code if validation failed
    exit(0 if report.passed else 1)

if __name__ == "__main__":
    main()