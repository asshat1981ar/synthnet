#!/usr/bin/env python3
"""
MCP Testing Framework - Main Test Runner
Comprehensive test execution engine for MCP servers.
"""

import asyncio
import logging
import json
import sys
import time
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import subprocess
import tempfile
import shutil

from .mcp_protocol_tester import MCPProtocolTester
from .performance_tester import PerformanceTester
from .security_scanner import SecurityScanner
from ..reporters.html_reporter import HTMLReporter
from ..reporters.junit_reporter import JUnitReporter
from ..reporters.performance_reporter import PerformanceReporter
from ..fixtures.test_data.data_manager import TestDataManager

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Result of a single test execution."""
    test_name: str
    test_type: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    message: str = ""
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TestSuite:
    """Collection of related tests."""
    name: str
    description: str
    tests: List[Callable] = field(default_factory=list)
    setup_func: Optional[Callable] = None
    teardown_func: Optional[Callable] = None
    tags: List[str] = field(default_factory=list)
    timeout: int = 300  # Default 5 minutes

@dataclass
class TestConfiguration:
    """Configuration for test execution."""
    server_path: str
    server_type: str  # 'healthcare', 'education', 'iot', etc.
    test_types: List[str] = field(default_factory=lambda: ['unit', 'integration', 'protocol', 'performance', 'security'])
    parallel_execution: bool = True
    max_workers: int = 4
    timeout: int = 300
    output_dir: str = "test_results"
    report_formats: List[str] = field(default_factory=lambda: ['html', 'junit', 'json'])
    coverage_enabled: bool = True
    mock_external_services: bool = True
    environment: str = "test"
    test_data_config: Optional[Dict[str, Any]] = None

@dataclass
class TestSession:
    """Test execution session context."""
    config: TestConfiguration
    results: List[TestResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    
    @property
    def duration(self) -> Optional[float]:
        """Get total session duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Get test success percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

class MCPTestRunner:
    """Main test runner for MCP server testing."""
    
    def __init__(self, config: TestConfiguration):
        """Initialize the test runner with configuration."""
        self.config = config
        self.test_suites: List[TestSuite] = []
        self.session: Optional[TestSession] = None
        
        # Initialize test components
        self.protocol_tester = MCPProtocolTester()
        self.performance_tester = PerformanceTester()
        self.security_scanner = SecurityScanner()
        self.data_manager = TestDataManager(config.test_data_config or {})
        
        # Initialize reporters
        self.reporters = {
            'html': HTMLReporter(config.output_dir),
            'junit': JUnitReporter(config.output_dir),
            'performance': PerformanceReporter(config.output_dir)
        }
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for test execution."""
        log_level = logging.DEBUG if self.config.environment == 'debug' else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(Path(self.config.output_dir) / 'test_execution.log')
            ]
        )
    
    def register_test_suite(self, suite: TestSuite):
        """Register a test suite for execution."""
        self.test_suites.append(suite)
        logger.info(f"Registered test suite: {suite.name} with {len(suite.tests)} tests")
    
    def discover_tests(self, test_directory: str) -> None:
        """Automatically discover and register test suites."""
        test_dir = Path(test_directory)
        if not test_dir.exists():
            logger.warning(f"Test directory not found: {test_directory}")
            return
        
        # Find all test files
        test_files = list(test_dir.glob("**/test_*.py"))
        
        for test_file in test_files:
            self._load_test_file(test_file)
    
    def _load_test_file(self, test_file: Path):
        """Load tests from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for test functions and classes
                test_functions = []
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (callable(attr) and 
                        (attr_name.startswith('test_') or 
                         hasattr(attr, '_is_mcp_test'))):
                        test_functions.append(attr)
                
                if test_functions:
                    suite = TestSuite(
                        name=test_file.stem,
                        description=f"Tests from {test_file.name}",
                        tests=test_functions
                    )
                    self.register_test_suite(suite)
                    
        except Exception as e:
            logger.error(f"Failed to load test file {test_file}: {e}")
    
    async def run_all_tests(self) -> TestSession:
        """Execute all registered test suites."""
        self.session = TestSession(config=self.config)
        self.session.start_time = datetime.now()
        
        logger.info(f"Starting MCP test session with {len(self.test_suites)} test suites")
        
        # Create output directory
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Run different test types based on configuration
            if 'protocol' in self.config.test_types:
                await self._run_protocol_tests()
            
            if 'unit' in self.config.test_types:
                await self._run_unit_tests()
            
            if 'integration' in self.config.test_types:
                await self._run_integration_tests()
            
            if 'performance' in self.config.test_types:
                await self._run_performance_tests()
            
            if 'security' in self.config.test_types:
                await self._run_security_tests()
            
            # Run registered test suites
            await self._run_test_suites()
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            self.session.results.append(TestResult(
                test_name="test_execution",
                test_type="system",
                status="error",
                duration=0.0,
                error=str(e)
            ))
        
        finally:
            self.session.end_time = datetime.now()
            self._calculate_session_stats()
            await self._generate_reports()
            
        return self.session
    
    async def _run_protocol_tests(self):
        """Run MCP protocol compliance tests."""
        logger.info("Running MCP protocol compliance tests")
        
        protocol_results = await self.protocol_tester.run_full_compliance_test(
            self.config.server_path
        )
        
        for result in protocol_results:
            self.session.results.append(TestResult(
                test_name=result.get('test_name', 'protocol_test'),
                test_type='protocol',
                status='passed' if result.get('passed', False) else 'failed',
                duration=result.get('duration', 0.0),
                message=result.get('message', ''),
                details=result.get('details')
            ))
    
    async def _run_unit_tests(self):
        """Run unit tests using pytest or similar."""
        logger.info("Running unit tests")
        
        server_path = Path(self.config.server_path)
        test_files = list(server_path.glob("**/test_*.py"))
        
        if not test_files:
            logger.warning("No unit test files found")
            return
        
        # Run pytest if available
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(server_path),
                "--json-report", 
                f"--json-report-file={self.config.output_dir}/pytest_results.json",
                "--tb=short"
            ], capture_output=True, text=True, timeout=self.config.timeout)
            
            # Parse pytest results
            pytest_results_file = Path(self.config.output_dir) / "pytest_results.json"
            if pytest_results_file.exists():
                with open(pytest_results_file, 'r') as f:
                    pytest_data = json.load(f)
                
                for test in pytest_data.get('tests', []):
                    self.session.results.append(TestResult(
                        test_name=test['nodeid'],
                        test_type='unit',
                        status=test['outcome'],
                        duration=test.get('duration', 0.0),
                        message=test.get('call', {}).get('longrepr', ''),
                        details=test
                    ))
                    
        except subprocess.TimeoutExpired:
            self.session.results.append(TestResult(
                test_name="unit_tests",
                test_type="unit",
                status="error",
                duration=self.config.timeout,
                error="Unit tests timed out"
            ))
        except Exception as e:
            logger.error(f"Failed to run unit tests: {e}")
    
    async def _run_integration_tests(self):
        """Run integration tests with mock MCP client."""
        logger.info("Running integration tests")
        
        # TODO: Implement integration testing with mock MCP client
        # This would involve starting the server and testing full workflows
        
        self.session.results.append(TestResult(
            test_name="integration_placeholder",
            test_type="integration",
            status="skipped",
            duration=0.0,
            message="Integration tests not yet implemented"
        ))
    
    async def _run_performance_tests(self):
        """Run performance and load tests."""
        logger.info("Running performance tests")
        
        perf_results = await self.performance_tester.run_performance_suite(
            self.config.server_path
        )
        
        for result in perf_results:
            self.session.results.append(TestResult(
                test_name=result.get('test_name', 'performance_test'),
                test_type='performance',
                status='passed' if result.get('passed', False) else 'failed',
                duration=result.get('duration', 0.0),
                message=result.get('message', ''),
                details=result.get('metrics')
            ))
    
    async def _run_security_tests(self):
        """Run security vulnerability tests."""
        logger.info("Running security tests")
        
        security_results = await self.security_scanner.scan_server(
            self.config.server_path
        )
        
        for result in security_results:
            self.session.results.append(TestResult(
                test_name=result.get('test_name', 'security_test'),
                test_type='security',
                status='passed' if not result.get('vulnerabilities') else 'failed',
                duration=result.get('scan_duration', 0.0),
                message=result.get('summary', ''),
                details=result
            ))
    
    async def _run_test_suites(self):
        """Run registered test suites."""
        if not self.test_suites:
            return
        
        logger.info(f"Running {len(self.test_suites)} custom test suites")
        
        if self.config.parallel_execution:
            await self._run_suites_parallel()
        else:
            await self._run_suites_sequential()
    
    async def _run_suites_parallel(self):
        """Run test suites in parallel."""
        tasks = []
        semaphore = asyncio.Semaphore(self.config.max_workers)
        
        for suite in self.test_suites:
            task = asyncio.create_task(self._run_suite_with_semaphore(suite, semaphore))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_suites_sequential(self):
        """Run test suites sequentially."""
        for suite in self.test_suites:
            await self._run_single_suite(suite)
    
    async def _run_suite_with_semaphore(self, suite: TestSuite, semaphore: asyncio.Semaphore):
        """Run a test suite with semaphore for concurrency control."""
        async with semaphore:
            await self._run_single_suite(suite)
    
    async def _run_single_suite(self, suite: TestSuite):
        """Run a single test suite."""
        logger.info(f"Running test suite: {suite.name}")
        
        try:
            # Run setup if provided
            if suite.setup_func:
                await self._run_function_safely(suite.setup_func, f"{suite.name}_setup")
            
            # Run all tests in the suite
            for test_func in suite.tests:
                await self._run_single_test(test_func, suite.name)
                
        except Exception as e:
            logger.error(f"Test suite {suite.name} failed: {e}")
        
        finally:
            # Run teardown if provided
            if suite.teardown_func:
                await self._run_function_safely(suite.teardown_func, f"{suite.name}_teardown")
    
    async def _run_single_test(self, test_func: Callable, suite_name: str):
        """Run a single test function."""
        test_name = f"{suite_name}.{test_func.__name__}"
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                await asyncio.wait_for(test_func(), timeout=self.config.timeout)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, test_func)
            
            duration = time.time() - start_time
            
            self.session.results.append(TestResult(
                test_name=test_name,
                test_type='custom',
                status='passed',
                duration=duration,
                message=f"Test {test_name} passed successfully"
            ))
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self.session.results.append(TestResult(
                test_name=test_name,
                test_type='custom',
                status='error',
                duration=duration,
                error=f"Test {test_name} timed out after {self.config.timeout} seconds"
            ))
            
        except Exception as e:
            duration = time.time() - start_time
            self.session.results.append(TestResult(
                test_name=test_name,
                test_type='custom',
                status='failed',
                duration=duration,
                error=str(e),
                message=f"Test {test_name} failed: {str(e)}"
            ))
    
    async def _run_function_safely(self, func: Callable, context: str):
        """Run a function safely with error handling."""
        try:
            if asyncio.iscoroutinefunction(func):
                await func()
            else:
                func()
        except Exception as e:
            logger.error(f"{context} failed: {e}")
    
    def _calculate_session_stats(self):
        """Calculate test session statistics."""
        if not self.session:
            return
        
        self.session.total_tests = len(self.session.results)
        
        for result in self.session.results:
            if result.status == 'passed':
                self.session.passed_tests += 1
            elif result.status == 'failed':
                self.session.failed_tests += 1
            elif result.status == 'skipped':
                self.session.skipped_tests += 1
            elif result.status == 'error':
                self.session.error_tests += 1
        
        logger.info(f"Test session completed - "
                   f"Total: {self.session.total_tests}, "
                   f"Passed: {self.session.passed_tests}, "
                   f"Failed: {self.session.failed_tests}, "
                   f"Errors: {self.session.error_tests}, "
                   f"Skipped: {self.session.skipped_tests}")
    
    async def _generate_reports(self):
        """Generate test reports in configured formats."""
        if not self.session:
            return
        
        logger.info("Generating test reports")
        
        report_data = {
            'session': self.session,
            'config': self.config,
            'results': self.session.results
        }
        
        # Generate reports in parallel
        report_tasks = []
        
        for format_name in self.config.report_formats:
            if format_name in self.reporters:
                reporter = self.reporters[format_name]
                task = asyncio.create_task(reporter.generate_report(report_data))
                report_tasks.append(task)
        
        if report_tasks:
            await asyncio.gather(*report_tasks, return_exceptions=True)
        
        # Generate JSON report
        json_report_path = Path(self.config.output_dir) / "test_results.json"
        with open(json_report_path, 'w') as f:
            json.dump({
                'session_info': {
                    'start_time': self.session.start_time.isoformat() if self.session.start_time else None,
                    'end_time': self.session.end_time.isoformat() if self.session.end_time else None,
                    'duration': self.session.duration,
                    'total_tests': self.session.total_tests,
                    'passed_tests': self.session.passed_tests,
                    'failed_tests': self.session.failed_tests,
                    'error_tests': self.session.error_tests,
                    'skipped_tests': self.session.skipped_tests,
                    'success_rate': self.session.success_rate
                },
                'config': {
                    'server_path': self.config.server_path,
                    'server_type': self.config.server_type,
                    'test_types': self.config.test_types,
                    'environment': self.config.environment
                },
                'results': [
                    {
                        'test_name': result.test_name,
                        'test_type': result.test_type,
                        'status': result.status,
                        'duration': result.duration,
                        'message': result.message,
                        'error': result.error,
                        'timestamp': result.timestamp,
                        'details': result.details
                    }
                    for result in self.session.results
                ]
            }, f, indent=2, default=str)

def create_test_configuration(
    server_path: str,
    server_type: str = "generic",
    test_types: Optional[List[str]] = None,
    **kwargs
) -> TestConfiguration:
    """Create a test configuration with sensible defaults."""
    
    if test_types is None:
        test_types = ['unit', 'integration', 'protocol', 'performance', 'security']
    
    return TestConfiguration(
        server_path=server_path,
        server_type=server_type,
        test_types=test_types,
        **kwargs
    )

# Decorator for marking test functions
def mcp_test(name: Optional[str] = None, tags: Optional[List[str]] = None):
    """Decorator to mark functions as MCP tests."""
    def decorator(func):
        func._is_mcp_test = True
        func._test_name = name or func.__name__
        func._test_tags = tags or []
        return func
    return decorator

async def main():
    """CLI entry point for the test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server Test Runner")
    parser.add_argument("server_path", help="Path to MCP server to test")
    parser.add_argument("--server-type", default="generic", help="Server type (healthcare, education, iot)")
    parser.add_argument("--test-types", nargs="+", 
                       default=['unit', 'integration', 'protocol', 'performance', 'security'],
                       help="Types of tests to run")
    parser.add_argument("--output-dir", default="test_results", help="Output directory for results")
    parser.add_argument("--parallel", action="store_true", default=True, help="Run tests in parallel")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum parallel workers")
    parser.add_argument("--timeout", type=int, default=300, help="Test timeout in seconds")
    parser.add_argument("--report-formats", nargs="+", default=['html', 'junit'], 
                       help="Report formats to generate")
    parser.add_argument("--environment", default="test", help="Test environment")
    parser.add_argument("--discover-tests", help="Directory to discover tests from")
    
    args = parser.parse_args()
    
    # Create configuration
    config = TestConfiguration(
        server_path=args.server_path,
        server_type=args.server_type,
        test_types=args.test_types,
        parallel_execution=args.parallel,
        max_workers=args.max_workers,
        timeout=args.timeout,
        output_dir=args.output_dir,
        report_formats=args.report_formats,
        environment=args.environment
    )
    
    # Create and configure runner
    runner = MCPTestRunner(config)
    
    # Discover tests if specified
    if args.discover_tests:
        runner.discover_tests(args.discover_tests)
    
    # Run tests
    session = await runner.run_all_tests()
    
    # Print summary
    print(f"\nTest Results Summary:")
    print(f"Total Tests: {session.total_tests}")
    print(f"Passed: {session.passed_tests}")
    print(f"Failed: {session.failed_tests}")
    print(f"Errors: {session.error_tests}")
    print(f"Skipped: {session.skipped_tests}")
    print(f"Success Rate: {session.success_rate:.1f}%")
    print(f"Duration: {session.duration:.2f}s" if session.duration else "")
    print(f"Results saved to: {config.output_dir}")
    
    # Exit with error code if tests failed
    sys.exit(0 if session.failed_tests == 0 and session.error_tests == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())