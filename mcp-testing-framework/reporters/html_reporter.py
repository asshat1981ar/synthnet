#!/usr/bin/env python3
"""
HTML Test Report Generator
Creates comprehensive HTML reports for MCP server testing results.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader
import base64

logger = logging.getLogger(__name__)

class HTMLReporter:
    """Generate comprehensive HTML test reports."""
    
    def __init__(self, output_dir: str):
        """Initialize the HTML reporter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_env = self._setup_template_environment()
        
    def _setup_template_environment(self) -> Environment:
        """Setup Jinja2 template environment."""
        # In a real implementation, templates would be in separate files
        # For this demo, we'll use embedded templates
        return Environment(
            loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
            autoescape=True
        )
    
    async def generate_report(self, report_data: Dict[str, Any]) -> str:
        """Generate comprehensive HTML report."""
        logger.info("Generating HTML test report")
        
        try:
            # Process report data
            processed_data = self._process_report_data(report_data)
            
            # Generate main report
            report_html = self._generate_main_report(processed_data)
            
            # Save report
            report_path = self.output_dir / "test_report.html"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            # Generate additional assets
            await self._generate_assets(processed_data)
            
            logger.info(f"HTML report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"HTML report generation failed: {e}")
            raise
    
    def _process_report_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enrich report data for HTML generation."""
        session = report_data.get('session')
        results = report_data.get('results', [])
        
        # Calculate statistics
        stats = {
            'total_tests': len(results),
            'passed_tests': len([r for r in results if r.status == 'passed']),
            'failed_tests': len([r for r in results if r.status == 'failed']),
            'error_tests': len([r for r in results if r.status == 'error']),
            'skipped_tests': len([r for r in results if r.status == 'skipped']),
            'success_rate': 0.0
        }
        
        if stats['total_tests'] > 0:
            stats['success_rate'] = (stats['passed_tests'] / stats['total_tests']) * 100
        
        # Group results by test type
        results_by_type = {}
        for result in results:
            test_type = result.test_type
            if test_type not in results_by_type:
                results_by_type[test_type] = []
            results_by_type[test_type].append(result)
        
        # Generate charts data
        charts_data = self._generate_charts_data(stats, results_by_type)
        
        # Calculate test durations
        duration_stats = self._calculate_duration_stats(results)
        
        # Security vulnerability summary (if available)
        security_summary = self._generate_security_summary(results)
        
        # Performance summary (if available)
        performance_summary = self._generate_performance_summary(results)
        
        return {
            'session': session,
            'config': report_data.get('config'),
            'results': results,
            'stats': stats,
            'results_by_type': results_by_type,
            'charts_data': charts_data,
            'duration_stats': duration_stats,
            'security_summary': security_summary,
            'performance_summary': performance_summary,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_main_report(self, data: Dict[str, Any]) -> str:
        """Generate main HTML report."""
        
        # Embedded HTML template (in production, this would be a separate file)
        template_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Server Test Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }
        
        .card.success { border-left-color: #4CAF50; }
        .card.success h3 { color: #4CAF50; }
        .card.success .value { color: #4CAF50; }
        
        .card.danger { border-left-color: #f44336; }
        .card.danger h3 { color: #f44336; }
        .card.danger .value { color: #f44336; }
        
        .card.warning { border-left-color: #ff9800; }
        .card.warning h3 { color: #ff9800; }
        .card.warning .value { color: #ff9800; }
        
        .card.info { border-left-color: #2196F3; }
        .card.info h3 { color: #2196F3; }
        .card.info .value { color: #2196F3; }
        
        .section {
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section-header {
            background: #667eea;
            color: white;
            padding: 20px;
            font-size: 1.3rem;
            font-weight: bold;
        }
        
        .section-content {
            padding: 20px;
        }
        
        .test-results {
            margin-bottom: 20px;
        }
        
        .test-type {
            margin-bottom: 30px;
        }
        
        .test-type h4 {
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        
        .test-item {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #ddd;
        }
        
        .test-item.passed {
            background: #f8fff8;
            border-left-color: #4CAF50;
        }
        
        .test-item.failed {
            background: #fff8f8;
            border-left-color: #f44336;
        }
        
        .test-item.error {
            background: #fff5f5;
            border-left-color: #ff5722;
        }
        
        .test-item.skipped {
            background: #fafafa;
            border-left-color: #9e9e9e;
        }
        
        .test-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .test-message {
            color: #666;
            margin-bottom: 10px;
        }
        
        .test-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #999;
        }
        
        .test-details {
            margin-top: 15px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9rem;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-passed {
            background: #4CAF50;
            color: white;
        }
        
        .status-failed {
            background: #f44336;
            color: white;
        }
        
        .status-error {
            background: #ff5722;
            color: white;
        }
        
        .status-skipped {
            background: #9e9e9e;
            color: white;
        }
        
        .chart-container {
            height: 300px;
            margin-bottom: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 50px;
        }
        
        .collapsible {
            cursor: pointer;
            user-select: none;
        }
        
        .collapsible:hover {
            background: #f5f5f5;
        }
        
        .collapse-content {
            display: none;
        }
        
        .collapse-content.active {
            display: block;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>MCP Server Test Report</h1>
            <div class="subtitle">
                Server: {{ config.server_path if config else 'Unknown' }}<br>
                Generated: {{ generated_at }}
            </div>
        </div>
        
        <!-- Summary Cards -->
        <div class="summary-cards">
            <div class="card success">
                <h3>Success Rate</h3>
                <div class="value">{{ "%.1f"|format(stats.success_rate) }}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ stats.success_rate }}%"></div>
                </div>
            </div>
            
            <div class="card info">
                <h3>Total Tests</h3>
                <div class="value">{{ stats.total_tests }}</div>
            </div>
            
            <div class="card success">
                <h3>Passed</h3>
                <div class="value">{{ stats.passed_tests }}</div>
            </div>
            
            <div class="card danger">
                <h3>Failed</h3>
                <div class="value">{{ stats.failed_tests + stats.error_tests }}</div>
            </div>
            
            <div class="card warning">
                <h3>Duration</h3>
                <div class="value">{{ "%.1f"|format(session.duration if session and session.duration else 0) }}s</div>
            </div>
        </div>
        
        <!-- Test Results Overview -->
        <div class="section">
            <div class="section-header">Test Results Overview</div>
            <div class="section-content">
                <div class="chart-container">
                    <canvas id="resultsChart"></canvas>
                </div>
            </div>
        </div>
        
        {% if performance_summary %}
        <!-- Performance Summary -->
        <div class="section">
            <div class="section-header">Performance Summary</div>
            <div class="section-content">
                <div class="summary-cards">
                    {% for metric, value in performance_summary.items() %}
                    <div class="card">
                        <h3>{{ metric|replace('_', ' ')|title }}</h3>
                        <div class="value">{{ value }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}
        
        {% if security_summary %}
        <!-- Security Summary -->
        <div class="section">
            <div class="section-header">Security Summary</div>
            <div class="section-content">
                <div class="summary-cards">
                    <div class="card {{ 'danger' if security_summary.critical_vulns > 0 else 'success' }}">
                        <h3>Critical Vulnerabilities</h3>
                        <div class="value">{{ security_summary.critical_vulns }}</div>
                    </div>
                    <div class="card {{ 'warning' if security_summary.high_vulns > 0 else 'success' }}">
                        <h3>High Vulnerabilities</h3>
                        <div class="value">{{ security_summary.high_vulns }}</div>
                    </div>
                    <div class="card info">
                        <h3>Medium Vulnerabilities</h3>
                        <div class="value">{{ security_summary.medium_vulns }}</div>
                    </div>
                    <div class="card">
                        <h3>Low Vulnerabilities</h3>
                        <div class="value">{{ security_summary.low_vulns }}</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Detailed Test Results -->
        <div class="section">
            <div class="section-header">Detailed Test Results</div>
            <div class="section-content">
                {% for test_type, test_results in results_by_type.items() %}
                <div class="test-type">
                    <h4>{{ test_type|replace('_', ' ')|title }} Tests ({{ test_results|length }})</h4>
                    
                    {% for result in test_results %}
                    <div class="test-item {{ result.status }}">
                        <div class="collapsible" onclick="toggleCollapse('test-{{ loop.index0 }}-{{ loop.parent.index0 }}')">
                            <div class="test-name">
                                {{ result.test_name }}
                                <span class="status-badge status-{{ result.status }}">{{ result.status }}</span>
                            </div>
                            <div class="test-message">{{ result.message or 'No message' }}</div>
                            <div class="test-meta">
                                <span>Duration: {{ "%.3f"|format(result.duration) }}s</span>
                                <span>{{ result.timestamp }}</span>
                            </div>
                        </div>
                        
                        {% if result.details or result.error %}
                        <div id="test-{{ loop.index0 }}-{{ loop.parent.index0 }}" class="collapse-content">
                            <div class="test-details">
                                {% if result.error %}
                                <strong>Error:</strong><br>
                                {{ result.error }}
                                {% endif %}
                                
                                {% if result.details %}
                                <strong>Details:</strong><br>
                                {{ result.details|tojson(indent=2) }}
                                {% endif %}
                            </div>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            Report generated by MCP Testing Framework | {{ generated_at }}
        </div>
    </div>
    
    <script>
        // Initialize charts
        const ctx = document.getElementById('resultsChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed', 'Error', 'Skipped'],
                datasets: [{
                    data: [{{ stats.passed_tests }}, {{ stats.failed_tests }}, {{ stats.error_tests }}, {{ stats.skipped_tests }}],
                    backgroundColor: ['#4CAF50', '#f44336', '#ff5722', '#9e9e9e']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Test Results Distribution'
                    }
                }
            }
        });
        
        // Collapsible functionality
        function toggleCollapse(id) {
            const element = document.getElementById(id);
            element.classList.toggle('active');
        }
        
        // Auto-expand failed tests
        document.addEventListener('DOMContentLoaded', function() {
            const failedTests = document.querySelectorAll('.test-item.failed, .test-item.error');
            failedTests.forEach(function(test) {
                const collapsible = test.querySelector('.collapsible');
                if (collapsible) {
                    collapsible.click();
                }
            });
        });
    </script>
</body>
</html>
        """
        
        template = Template(template_html)
        return template.render(**data)
    
    def _generate_charts_data(self, stats: Dict[str, Any], results_by_type: Dict[str, List]) -> Dict[str, Any]:
        """Generate data for charts."""
        return {
            'test_results': {
                'labels': ['Passed', 'Failed', 'Error', 'Skipped'],
                'data': [stats['passed_tests'], stats['failed_tests'], stats['error_tests'], stats['skipped_tests']],
                'colors': ['#4CAF50', '#f44336', '#ff5722', '#9e9e9e']
            },
            'test_types': {
                'labels': list(results_by_type.keys()),
                'data': [len(results) for results in results_by_type.values()]
            }
        }
    
    def _calculate_duration_stats(self, results: List[Any]) -> Dict[str, Any]:
        """Calculate test duration statistics."""
        if not results:
            return {}
        
        durations = [r.duration for r in results if hasattr(r, 'duration')]
        if not durations:
            return {}
        
        return {
            'total_duration': sum(durations),
            'average_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'slowest_tests': sorted([
                {'name': r.test_name, 'duration': r.duration}
                for r in results if hasattr(r, 'duration')
            ], key=lambda x: x['duration'], reverse=True)[:5]
        }
    
    def _generate_security_summary(self, results: List[Any]) -> Optional[Dict[str, Any]]:
        """Generate security vulnerability summary."""
        security_results = [r for r in results if hasattr(r, 'test_type') and r.test_type == 'security']
        
        if not security_results:
            return None
        
        critical_vulns = 0
        high_vulns = 0
        medium_vulns = 0
        low_vulns = 0
        
        for result in security_results:
            if hasattr(result, 'details') and result.details:
                vulnerabilities = result.details.get('vulnerabilities', [])
                for vuln in vulnerabilities:
                    severity = vuln.get('severity', '').lower()
                    if severity == 'critical':
                        critical_vulns += 1
                    elif severity == 'high':
                        high_vulns += 1
                    elif severity == 'medium':
                        medium_vulns += 1
                    elif severity == 'low':
                        low_vulns += 1
        
        return {
            'critical_vulns': critical_vulns,
            'high_vulns': high_vulns,
            'medium_vulns': medium_vulns,
            'low_vulns': low_vulns,
            'total_vulns': critical_vulns + high_vulns + medium_vulns + low_vulns
        }
    
    def _generate_performance_summary(self, results: List[Any]) -> Optional[Dict[str, Any]]:
        """Generate performance testing summary."""
        performance_results = [r for r in results if hasattr(r, 'test_type') and r.test_type == 'performance']
        
        if not performance_results:
            return None
        
        summary = {}
        
        for result in performance_results:
            if hasattr(result, 'details') and result.details:
                metrics = result.details.get('metrics', {})
                
                # Collect key performance metrics
                if 'requests_per_second' in metrics:
                    summary['Requests/sec'] = f"{metrics['requests_per_second']:.1f}"
                if 'average_response_time' in metrics:
                    summary['Avg Response'] = f"{metrics['average_response_time']:.3f}s"
                if 'p95_response_time' in metrics:
                    summary['95th Percentile'] = f"{metrics['p95_response_time']:.3f}s"
                if 'error_rate' in metrics:
                    summary['Error Rate'] = f"{metrics['error_rate']:.2%}"
        
        return summary if summary else None
    
    async def _generate_assets(self, data: Dict[str, Any]):
        """Generate additional report assets (CSS, JS, images)."""
        # In a full implementation, this would generate separate CSS/JS files
        # and performance charts as images
        pass

if __name__ == "__main__":
    # Test the HTML reporter
    async def test_reporter():
        from datetime import datetime
        from dataclasses import dataclass
        
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
            total_tests: int = 50
            passed_tests: int = 45
            failed_tests: int = 3
            error_tests: int = 1
            skipped_tests: int = 1
        
        # Mock test data
        mock_data = {
            'session': MockSession(),
            'config': {'server_path': '/test/server.py', 'server_type': 'healthcare'},
            'results': [
                MockResult('test_connection', 'unit', 'passed', 0.5, 'Connection test passed'),
                MockResult('test_authentication', 'integration', 'failed', 1.2, 'Auth failed', 'Invalid credentials'),
                MockResult('test_performance', 'performance', 'passed', 2.1, 'Performance acceptable'),
            ]
        }
        
        reporter = HTMLReporter('test_output')
        report_path = await reporter.generate_report(mock_data)
        print(f"Test report generated: {report_path}")
    
    import asyncio
    asyncio.run(test_reporter())