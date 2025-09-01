#!/usr/bin/env python3
"""
JUnit XML Test Report Generator
Creates JUnit-compatible XML reports for CI/CD integration.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class JUnitReporter:
    """Generate JUnit XML test reports for CI/CD integration."""
    
    def __init__(self, output_dir: str):
        """Initialize the JUnit reporter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JUnit XML report."""
        logger.info("Generating JUnit XML test report")
        
        try:
            session = report_data.get('session')
            results = report_data.get('results', [])
            config = report_data.get('config', {})
            
            # Create root testsuites element
            testsuites = ET.Element("testsuites")
            testsuites.set("name", f"MCP Server Tests - {config.get('server_type', 'Unknown')}")
            testsuites.set("timestamp", datetime.now().isoformat())
            
            # Add overall statistics
            total_tests = len(results)
            total_failures = len([r for r in results if r.status == 'failed'])
            total_errors = len([r for r in results if r.status == 'error'])
            total_skipped = len([r for r in results if r.status == 'skipped'])
            total_time = str(session.duration if session and hasattr(session, 'duration') and session.duration else 0.0)
            
            testsuites.set("tests", str(total_tests))
            testsuites.set("failures", str(total_failures))
            testsuites.set("errors", str(total_errors))
            testsuites.set("skipped", str(total_skipped))
            testsuites.set("time", total_time)
            
            # Group tests by test type for separate test suites
            tests_by_type = {}
            for result in results:
                test_type = getattr(result, 'test_type', 'unknown')
                if test_type not in tests_by_type:
                    tests_by_type[test_type] = []
                tests_by_type[test_type].append(result)
            
            # Create a testsuite for each test type
            for test_type, type_results in tests_by_type.items():
                testsuite = self._create_testsuite(test_type, type_results, config)
                testsuites.append(testsuite)
            
            # Generate XML
            self._indent_xml(testsuites)
            tree = ET.ElementTree(testsuites)
            
            # Save report
            report_path = self.output_dir / "junit_results.xml"
            tree.write(str(report_path), encoding='utf-8', xml_declaration=True)
            
            logger.info(f"JUnit XML report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"JUnit XML report generation failed: {e}")
            raise
    
    def _create_testsuite(self, test_type: str, results: List[Any], config: Dict[str, Any]) -> ET.Element:
        """Create a testsuite element for a specific test type."""
        
        testsuite = ET.Element("testsuite")
        
        # Calculate suite statistics
        total_tests = len(results)
        total_failures = len([r for r in results if r.status == 'failed'])
        total_errors = len([r for r in results if r.status == 'error'])
        total_skipped = len([r for r in results if r.status == 'skipped'])
        total_time = sum(getattr(r, 'duration', 0.0) for r in results)
        
        # Set testsuite attributes
        testsuite.set("name", f"{test_type.replace('_', ' ').title()} Tests")
        testsuite.set("package", f"mcp.server.{config.get('server_type', 'unknown')}")
        testsuite.set("tests", str(total_tests))
        testsuite.set("failures", str(total_failures))
        testsuite.set("errors", str(total_errors))
        testsuite.set("skipped", str(total_skipped))
        testsuite.set("time", f"{total_time:.3f}")
        testsuite.set("timestamp", datetime.now().isoformat())
        testsuite.set("hostname", config.get('server_path', 'unknown'))
        
        # Add properties
        properties = ET.SubElement(testsuite, "properties")
        
        # Add configuration properties
        for key, value in config.items():
            if isinstance(value, (str, int, float, bool)):
                prop = ET.SubElement(properties, "property")
                prop.set("name", key)
                prop.set("value", str(value))
        
        # Add system properties
        system_props = {
            "test.framework": "MCP Testing Framework",
            "test.type": test_type,
            "report.generated": datetime.now().isoformat()
        }
        
        for key, value in system_props.items():
            prop = ET.SubElement(properties, "property")
            prop.set("name", key)
            prop.set("value", str(value))
        
        # Add individual test cases
        for result in results:
            testcase = self._create_testcase(result, test_type)
            testsuite.append(testcase)
        
        # Add system-out and system-err if needed
        system_out_content = self._get_system_output(results, 'stdout')
        if system_out_content:
            system_out = ET.SubElement(testsuite, "system-out")
            system_out.text = system_out_content
        
        system_err_content = self._get_system_output(results, 'stderr')
        if system_err_content:
            system_err = ET.SubElement(testsuite, "system-err")
            system_err.text = system_err_content
        
        return testsuite
    
    def _create_testcase(self, result: Any, test_type: str) -> ET.Element:
        """Create a testcase element for a single test result."""
        
        testcase = ET.Element("testcase")
        
        # Set testcase attributes
        test_name = getattr(result, 'test_name', 'unknown_test')
        class_name = f"mcp.{test_type}.{self._sanitize_class_name(test_name)}"
        
        testcase.set("name", test_name)
        testcase.set("classname", class_name)
        testcase.set("time", f"{getattr(result, 'duration', 0.0):.3f}")
        
        # Add timestamp if available
        if hasattr(result, 'timestamp'):
            testcase.set("timestamp", result.timestamp)
        
        # Handle different test statuses
        status = getattr(result, 'status', 'unknown')
        
        if status == 'failed':
            failure = ET.SubElement(testcase, "failure")
            failure.set("type", "TestFailure")
            
            message = getattr(result, 'message', 'Test failed')
            failure.set("message", message)
            
            # Add failure details
            failure_text = self._format_failure_text(result)
            failure.text = failure_text
            
        elif status == 'error':
            error = ET.SubElement(testcase, "error")
            error.set("type", "TestError")
            
            error_msg = getattr(result, 'error', getattr(result, 'message', 'Test error'))
            error.set("message", error_msg)
            
            # Add error details
            error_text = self._format_error_text(result)
            error.text = error_text
            
        elif status == 'skipped':
            skipped = ET.SubElement(testcase, "skipped")
            skip_message = getattr(result, 'message', 'Test skipped')
            skipped.set("message", skip_message)
        
        # Add test properties if available
        if hasattr(result, 'details') and result.details:
            properties = ET.SubElement(testcase, "properties")
            self._add_test_properties(properties, result.details)
        
        return testcase
    
    def _format_failure_text(self, result: Any) -> str:
        """Format failure information for JUnit XML."""
        lines = []
        
        # Add basic failure info
        if hasattr(result, 'message') and result.message:
            lines.append(f"Message: {result.message}")
        
        # Add error if available
        if hasattr(result, 'error') and result.error:
            lines.append(f"Error: {result.error}")
        
        # Add details if available
        if hasattr(result, 'details') and result.details:
            lines.append("Details:")
            if isinstance(result.details, dict):
                for key, value in result.details.items():
                    lines.append(f"  {key}: {value}")
            else:
                lines.append(f"  {result.details}")
        
        # Add test context
        if hasattr(result, 'test_type'):
            lines.append(f"Test Type: {result.test_type}")
        
        if hasattr(result, 'timestamp'):
            lines.append(f"Timestamp: {result.timestamp}")
        
        return "\n".join(lines)
    
    def _format_error_text(self, result: Any) -> str:
        """Format error information for JUnit XML."""
        lines = []
        
        # Add error message
        if hasattr(result, 'error') and result.error:
            lines.append(f"Error: {result.error}")
        elif hasattr(result, 'message') and result.message:
            lines.append(f"Message: {result.message}")
        
        # Add stack trace if available in details
        if hasattr(result, 'details') and result.details:
            if isinstance(result.details, dict):
                traceback = result.details.get('traceback')
                if traceback:
                    lines.append("Stack Trace:")
                    lines.append(traceback)
                
                # Add other details
                for key, value in result.details.items():
                    if key != 'traceback':
                        lines.append(f"{key}: {value}")
            else:
                lines.append(f"Details: {result.details}")
        
        return "\n".join(lines)
    
    def _add_test_properties(self, properties_element: ET.Element, details: Dict[str, Any]):
        """Add test properties from result details."""
        
        def add_property(name: str, value: Any):
            """Add a single property."""
            prop = ET.SubElement(properties_element, "property")
            prop.set("name", name)
            prop.set("value", str(value))
        
        # Add details as properties
        for key, value in details.items():
            if isinstance(value, (str, int, float, bool)):
                add_property(key, value)
            elif isinstance(value, dict):
                # Flatten nested dictionaries
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, (str, int, float, bool)):
                        add_property(f"{key}.{nested_key}", nested_value)
            elif isinstance(value, list):
                # Add list length and first few items
                add_property(f"{key}.count", len(value))
                for i, item in enumerate(value[:3]):  # First 3 items
                    if isinstance(item, (str, int, float, bool)):
                        add_property(f"{key}.{i}", item)
    
    def _get_system_output(self, results: List[Any], output_type: str) -> str:
        """Get system output (stdout/stderr) from test results."""
        output_lines = []
        
        for result in results:
            if hasattr(result, 'details') and result.details:
                if isinstance(result.details, dict):
                    output = result.details.get(output_type)
                    if output:
                        output_lines.append(f"=== {result.test_name} ===")
                        output_lines.append(str(output))
                        output_lines.append("")
        
        return "\n".join(output_lines) if output_lines else ""
    
    def _sanitize_class_name(self, test_name: str) -> str:
        """Sanitize test name for use as class name."""
        # Remove special characters and replace with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', test_name)
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        return sanitized or 'UnknownTest'
    
    def _indent_xml(self, element: ET.Element, level: int = 0):
        """Add indentation to XML for pretty printing."""
        indent = "\n" + "  " * level
        if len(element):
            if not element.text or not element.text.strip():
                element.text = indent + "  "
            if not element.tail or not element.tail.strip():
                element.tail = indent
            for child in element:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = indent

def generate_junit_report(results: List[Any], output_path: str, suite_name: str = "MCP Tests") -> str:
    """Utility function to generate JUnit XML report from test results."""
    
    # Create testsuites root
    testsuites = ET.Element("testsuites")
    testsuites.set("name", suite_name)
    testsuites.set("timestamp", datetime.now().isoformat())
    
    # Calculate overall stats
    total_tests = len(results)
    total_failures = len([r for r in results if getattr(r, 'status', '') == 'failed'])
    total_errors = len([r for r in results if getattr(r, 'status', '') == 'error'])
    total_skipped = len([r for r in results if getattr(r, 'status', '') == 'skipped'])
    total_time = sum(getattr(r, 'duration', 0.0) for r in results)
    
    testsuites.set("tests", str(total_tests))
    testsuites.set("failures", str(total_failures))
    testsuites.set("errors", str(total_errors))
    testsuites.set("skipped", str(total_skipped))
    testsuites.set("time", f"{total_time:.3f}")
    
    # Create single testsuite
    testsuite = ET.SubElement(testsuites, "testsuite")
    testsuite.set("name", suite_name)
    testsuite.set("tests", str(total_tests))
    testsuite.set("failures", str(total_failures))
    testsuite.set("errors", str(total_errors))
    testsuite.set("skipped", str(total_skipped))
    testsuite.set("time", f"{total_time:.3f}")
    testsuite.set("timestamp", datetime.now().isoformat())
    
    # Add test cases
    for i, result in enumerate(results):
        testcase = ET.SubElement(testsuite, "testcase")
        test_name = getattr(result, 'test_name', f'test_{i}')
        testcase.set("name", test_name)
        testcase.set("classname", f"mcp.tests.{test_name.replace('-', '_')}")
        testcase.set("time", f"{getattr(result, 'duration', 0.0):.3f}")
        
        status = getattr(result, 'status', 'unknown')
        
        if status == 'failed':
            failure = ET.SubElement(testcase, "failure")
            failure.set("message", getattr(result, 'message', 'Test failed'))
            failure.text = getattr(result, 'error', '')
            
        elif status == 'error':
            error = ET.SubElement(testcase, "error")
            error.set("message", getattr(result, 'message', 'Test error'))
            error.text = getattr(result, 'error', '')
            
        elif status == 'skipped':
            skipped = ET.SubElement(testcase, "skipped")
            skipped.set("message", getattr(result, 'message', 'Test skipped'))
    
    # Format and save XML
    JUnitReporter(Path(output_path).parent)._indent_xml(testsuites)
    tree = ET.ElementTree(testsuites)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    return output_path

if __name__ == "__main__":
    # Test the JUnit reporter
    async def test_reporter():
        from dataclasses import dataclass
        from datetime import datetime
        
        @dataclass
        class MockResult:
            test_name: str
            test_type: str
            status: str
            duration: float
            message: str = ""
            error: Optional[str] = None
            details: Optional[Dict[str, Any]] = None
            timestamp: str = datetime.now().isoformat()
        
        @dataclass
        class MockSession:
            duration: float = 120.5
        
        # Mock test data
        mock_data = {
            'session': MockSession(),
            'config': {'server_path': '/test/server.py', 'server_type': 'healthcare'},
            'results': [
                MockResult('test_connection', 'unit', 'passed', 0.5, 'Connection test passed'),
                MockResult('test_authentication', 'integration', 'failed', 1.2, 'Auth failed', 'Invalid credentials'),
                MockResult('test_performance', 'performance', 'error', 2.1, 'Performance test error', 'Server not responding'),
                MockResult('test_security', 'security', 'skipped', 0.0, 'Security test skipped'),
            ]
        }
        
        reporter = JUnitReporter('test_output')
        report_path = await reporter.generate_report(mock_data)
        print(f"JUnit XML report generated: {report_path}")
        
        # Read and print the generated XML
        with open(report_path, 'r') as f:
            print("\nGenerated XML:")
            print(f.read())
    
    import asyncio
    asyncio.run(test_reporter())