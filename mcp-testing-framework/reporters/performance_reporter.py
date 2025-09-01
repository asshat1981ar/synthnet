#!/usr/bin/env python3
"""
Performance Test Report Generator
Creates detailed performance analysis reports with charts and metrics.
"""

import json
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class PerformanceReporter:
    """Generate comprehensive performance test reports."""
    
    def __init__(self, output_dir: str):
        """Initialize the performance reporter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette("husl")
    
    async def generate_report(self, report_data: Dict[str, Any]) -> str:
        """Generate comprehensive performance report."""
        logger.info("Generating performance test report")
        
        try:
            # Extract performance data
            performance_data = self._extract_performance_data(report_data)
            
            if not performance_data:
                logger.warning("No performance data found in report")
                return self._generate_empty_report()
            
            # Generate analysis
            analysis = self._analyze_performance_data(performance_data)
            
            # Generate charts
            charts = await self._generate_charts(performance_data)
            
            # Generate detailed report
            report_content = self._generate_detailed_report(performance_data, analysis, charts)
            
            # Save reports
            report_paths = await self._save_reports(report_content, analysis, performance_data)
            
            logger.info(f"Performance reports generated: {report_paths}")
            return report_paths['html']
            
        except Exception as e:
            logger.error(f"Performance report generation failed: {e}")
            raise
    
    def _extract_performance_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and organize performance data from test results."""
        results = report_data.get('results', [])
        performance_results = []
        
        for result in results:
            if (hasattr(result, 'test_type') and result.test_type == 'performance') or \
               ('performance' in getattr(result, 'test_name', '').lower()):
                
                perf_data = {
                    'test_name': getattr(result, 'test_name', 'unknown'),
                    'duration': getattr(result, 'duration', 0.0),
                    'status': getattr(result, 'status', 'unknown'),
                    'timestamp': getattr(result, 'timestamp', datetime.now().isoformat()),
                    'metrics': {}
                }
                
                # Extract detailed metrics if available
                if hasattr(result, 'details') and result.details:
                    if isinstance(result.details, dict):
                        metrics = result.details.get('metrics', {})
                        perf_data['metrics'] = metrics
                        
                        # Also check for direct metrics in details
                        for key, value in result.details.items():
                            if key != 'metrics' and isinstance(value, (int, float)):
                                perf_data['metrics'][key] = value
                
                performance_results.append(perf_data)
        
        return {
            'test_results': performance_results,
            'session_info': report_data.get('session'),
            'config': report_data.get('config', {}),
            'generated_at': datetime.now().isoformat()
        }
    
    def _analyze_performance_data(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance data and generate insights."""
        test_results = performance_data.get('test_results', [])
        
        if not test_results:
            return {}
        
        analysis = {
            'summary': {},
            'trends': {},
            'bottlenecks': [],
            'recommendations': [],
            'benchmarks': {}
        }
        
        # Overall summary
        total_tests = len(test_results)
        passed_tests = len([t for t in test_results if t['status'] == 'passed'])
        
        analysis['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': sum(t['duration'] for t in test_results)
        }
        
        # Analyze response times
        response_times = []
        throughput_values = []
        error_rates = []
        memory_usage = []
        cpu_usage = []
        
        for test in test_results:
            metrics = test.get('metrics', {})
            
            if 'average_response_time' in metrics:
                response_times.append(metrics['average_response_time'])
            if 'requests_per_second' in metrics:
                throughput_values.append(metrics['requests_per_second'])
            if 'error_rate' in metrics:
                error_rates.append(metrics['error_rate'])
            if 'memory_usage_mb' in metrics:
                memory_usage.append(metrics['memory_usage_mb'])
            if 'cpu_usage_percent' in metrics:
                cpu_usage.append(metrics['cpu_usage_percent'])
        
        # Response time analysis
        if response_times:
            analysis['response_time_analysis'] = {
                'mean': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                'percentiles': {
                    'p50': self._percentile(response_times, 50),
                    'p90': self._percentile(response_times, 90),
                    'p95': self._percentile(response_times, 95),
                    'p99': self._percentile(response_times, 99)
                }
            }
        
        # Throughput analysis
        if throughput_values:
            analysis['throughput_analysis'] = {
                'mean': statistics.mean(throughput_values),
                'median': statistics.median(throughput_values),
                'max': max(throughput_values),
                'min': min(throughput_values),
                'peak_throughput': max(throughput_values)
            }
        
        # Error rate analysis
        if error_rates:
            analysis['error_analysis'] = {
                'mean_error_rate': statistics.mean(error_rates),
                'max_error_rate': max(error_rates),
                'tests_with_errors': len([r for r in error_rates if r > 0])
            }
        
        # Resource usage analysis
        if memory_usage:
            analysis['memory_analysis'] = {
                'mean_usage': statistics.mean(memory_usage),
                'peak_usage': max(memory_usage),
                'min_usage': min(memory_usage)
            }
        
        if cpu_usage:
            analysis['cpu_analysis'] = {
                'mean_usage': statistics.mean(cpu_usage),
                'peak_usage': max(cpu_usage),
                'min_usage': min(cpu_usage)
            }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis, test_results)
        
        # Identify bottlenecks
        analysis['bottlenecks'] = self._identify_bottlenecks(analysis, test_results)
        
        return analysis
    
    async def _generate_charts(self, performance_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate performance charts and return as base64 encoded images."""
        charts = {}
        test_results = performance_data.get('test_results', [])
        
        if not test_results:
            return charts
        
        # Chart 1: Response Time Distribution
        charts['response_time_distribution'] = await self._generate_response_time_chart(test_results)
        
        # Chart 2: Throughput over Time
        charts['throughput_chart'] = await self._generate_throughput_chart(test_results)
        
        # Chart 3: Resource Usage
        charts['resource_usage'] = await self._generate_resource_usage_chart(test_results)
        
        # Chart 4: Error Rate Analysis
        charts['error_rate_chart'] = await self._generate_error_rate_chart(test_results)
        
        # Chart 5: Load Test Comparison
        charts['load_comparison'] = await self._generate_load_comparison_chart(test_results)
        
        return charts
    
    async def _generate_response_time_chart(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate response time distribution chart."""
        response_times = []
        test_names = []
        
        for test in test_results:
            metrics = test.get('metrics', {})
            if 'average_response_time' in metrics:
                response_times.append(metrics['average_response_time'])
                test_names.append(test['test_name'])
        
        if not response_times:
            return ""
        
        plt.figure(figsize=(12, 6))
        
        # Create subplot for histogram and box plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Histogram
        ax1.hist(response_times, bins=min(20, len(response_times)), alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xlabel('Response Time (seconds)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Response Time Distribution')
        ax1.grid(True, alpha=0.3)
        
        # Box plot by test
        if len(set(test_names)) > 1:
            df = pd.DataFrame({'test_name': test_names, 'response_time': response_times})
            df.boxplot(column='response_time', by='test_name', ax=ax2)
            ax2.set_xlabel('Test Name')
            ax2.set_ylabel('Response Time (seconds)')
            ax2.set_title('Response Time by Test')
        else:
            ax2.boxplot(response_times)
            ax2.set_ylabel('Response Time (seconds)')
            ax2.set_title('Response Time Box Plot')
        
        plt.tight_layout()
        
        # Save as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    async def _generate_throughput_chart(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate throughput over time chart."""
        throughput_data = []
        timestamps = []
        
        for test in test_results:
            metrics = test.get('metrics', {})
            if 'requests_per_second' in metrics:
                throughput_data.append(metrics['requests_per_second'])
                timestamps.append(datetime.fromisoformat(test['timestamp'].replace('Z', '+00:00')))
        
        if not throughput_data:
            return ""
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, throughput_data, marker='o', linewidth=2, markersize=6)
        plt.xlabel('Time')
        plt.ylabel('Requests per Second')
        plt.title('Throughput Over Time')
        plt.grid(True, alpha=0.3)
        
        # Format x-axis dates
        if len(timestamps) > 1:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    async def _generate_resource_usage_chart(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate resource usage chart."""
        memory_usage = []
        cpu_usage = []
        test_names = []
        
        for test in test_results:
            metrics = test.get('metrics', {})
            if 'memory_usage_mb' in metrics and 'cpu_usage_percent' in metrics:
                memory_usage.append(metrics['memory_usage_mb'])
                cpu_usage.append(metrics['cpu_usage_percent'])
                test_names.append(test['test_name'][:20])  # Truncate long names
        
        if not memory_usage or not cpu_usage:
            return ""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Memory usage
        ax1.bar(range(len(memory_usage)), memory_usage, color='lightcoral', alpha=0.7)
        ax1.set_xlabel('Test')
        ax1.set_ylabel('Memory Usage (MB)')
        ax1.set_title('Memory Usage by Test')
        ax1.set_xticks(range(len(test_names)))
        ax1.set_xticklabels(test_names, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # CPU usage
        ax2.bar(range(len(cpu_usage)), cpu_usage, color='lightgreen', alpha=0.7)
        ax2.set_xlabel('Test')
        ax2.set_ylabel('CPU Usage (%)')
        ax2.set_title('CPU Usage by Test')
        ax2.set_xticks(range(len(test_names)))
        ax2.set_xticklabels(test_names, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    async def _generate_error_rate_chart(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate error rate analysis chart."""
        error_rates = []
        test_names = []
        
        for test in test_results:
            metrics = test.get('metrics', {})
            if 'error_rate' in metrics:
                error_rates.append(metrics['error_rate'] * 100)  # Convert to percentage
                test_names.append(test['test_name'][:20])
        
        if not error_rates:
            return ""
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(error_rates)), error_rates, color='orange', alpha=0.7)
        
        # Color bars based on error rate
        for i, bar in enumerate(bars):
            if error_rates[i] > 5:  # High error rate
                bar.set_color('red')
            elif error_rates[i] > 1:  # Medium error rate
                bar.set_color('orange')
            else:  # Low error rate
                bar.set_color('green')
        
        plt.xlabel('Test')
        plt.ylabel('Error Rate (%)')
        plt.title('Error Rate by Test')
        plt.xticks(range(len(test_names)), test_names, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # Add threshold lines
        plt.axhline(y=1, color='orange', linestyle='--', alpha=0.5, label='1% threshold')
        plt.axhline(y=5, color='red', linestyle='--', alpha=0.5, label='5% threshold')
        plt.legend()
        
        plt.tight_layout()
        
        # Save as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    async def _generate_load_comparison_chart(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate load test comparison chart."""
        load_tests = []
        
        for test in test_results:
            if 'load_test' in test['test_name'].lower():
                metrics = test.get('metrics', {})
                if 'requests_per_second' in metrics and 'average_response_time' in metrics:
                    # Extract concurrent users from test name if possible
                    import re
                    users_match = re.search(r'(\d+)_users', test['test_name'])
                    users = int(users_match.group(1)) if users_match else len(load_tests) + 1
                    
                    load_tests.append({
                        'users': users,
                        'throughput': metrics['requests_per_second'],
                        'response_time': metrics['average_response_time'],
                        'error_rate': metrics.get('error_rate', 0) * 100
                    })
        
        if len(load_tests) < 2:
            return ""
        
        # Sort by number of users
        load_tests.sort(key=lambda x: x['users'])
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        users = [test['users'] for test in load_tests]
        
        # Throughput vs Users
        throughput = [test['throughput'] for test in load_tests]
        ax1.plot(users, throughput, marker='o', color='blue', linewidth=2, markersize=6)
        ax1.set_xlabel('Concurrent Users')
        ax1.set_ylabel('Throughput (req/s)')
        ax1.set_title('Throughput vs Concurrent Users')
        ax1.grid(True, alpha=0.3)
        
        # Response Time vs Users
        response_times = [test['response_time'] for test in load_tests]
        ax2.plot(users, response_times, marker='s', color='red', linewidth=2, markersize=6)
        ax2.set_xlabel('Concurrent Users')
        ax2.set_ylabel('Response Time (s)')
        ax2.set_title('Response Time vs Concurrent Users')
        ax2.grid(True, alpha=0.3)
        
        # Error Rate vs Users
        error_rates = [test['error_rate'] for test in load_tests]
        ax3.plot(users, error_rates, marker='^', color='orange', linewidth=2, markersize=6)
        ax3.set_xlabel('Concurrent Users')
        ax3.set_ylabel('Error Rate (%)')
        ax3.set_title('Error Rate vs Concurrent Users')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def _generate_detailed_report(self, performance_data: Dict[str, Any], 
                                 analysis: Dict[str, Any], charts: Dict[str, str]) -> str:
        """Generate detailed HTML performance report."""
        
        # Embedded HTML template
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Performance Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007acc;
        }}
        
        .header h1 {{
            color: #007acc;
            font-size: 2.5em;
            margin: 0;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 1.2em;
            margin-top: 10px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .metric-card .unit {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .section {{
            margin: 40px 0;
        }}
        
        .section h2 {{
            color: #007acc;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .chart-container {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        
        .analysis-section {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #007acc;
            margin: 20px 0;
        }}
        
        .recommendations {{
            background: #e8f5e8;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .bottlenecks {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .test-results-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .test-results-table th,
        .test-results-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        .test-results-table th {{
            background-color: #007acc;
            color: white;
        }}
        
        .test-results-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        
        .status-passed {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .status-failed {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Performance Test Report</h1>
            <div class="subtitle">
                Server: {performance_data.get('config', {}).get('server_path', 'Unknown')}<br>
                Generated: {performance_data.get('generated_at', 'Unknown')}
            </div>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Tests</h3>
                    <div class="value">{analysis.get('summary', {}).get('total_tests', 0)}</div>
                </div>
                <div class="metric-card">
                    <h3>Success Rate</h3>
                    <div class="value">{analysis.get('summary', {}).get('success_rate', 0):.1f}</div>
                    <div class="unit">%</div>
                </div>
                <div class="metric-card">
                    <h3>Avg Response Time</h3>
                    <div class="value">{analysis.get('response_time_analysis', {}).get('mean', 0):.3f}</div>
                    <div class="unit">seconds</div>
                </div>
                <div class="metric-card">
                    <h3>Peak Throughput</h3>
                    <div class="value">{analysis.get('throughput_analysis', {}).get('peak_throughput', 0):.1f}</div>
                    <div class="unit">req/s</div>
                </div>
            </div>
        </div>
        
        {self._generate_charts_html(charts)}
        
        {self._generate_analysis_html(analysis)}
        
        {self._generate_test_results_html(performance_data.get('test_results', []))}
        
        <div class="footer">
            Generated by MCP Testing Framework Performance Reporter
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _generate_charts_html(self, charts: Dict[str, str]) -> str:
        """Generate HTML for performance charts."""
        html = '<div class="section"><h2>Performance Charts</h2>'
        
        chart_titles = {
            'response_time_distribution': 'Response Time Distribution',
            'throughput_chart': 'Throughput Over Time',
            'resource_usage': 'Resource Usage',
            'error_rate_chart': 'Error Rate Analysis',
            'load_comparison': 'Load Test Comparison'
        }
        
        for chart_key, chart_data in charts.items():
            if chart_data:
                title = chart_titles.get(chart_key, chart_key.replace('_', ' ').title())
                html += f'''
                <div class="chart-container">
                    <h3>{title}</h3>
                    <img src="data:image/png;base64,{chart_data}" alt="{title}">
                </div>
                '''
        
        html += '</div>'
        return html
    
    def _generate_analysis_html(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML for performance analysis."""
        html = '<div class="section"><h2>Performance Analysis</h2>'
        
        # Response Time Analysis
        if 'response_time_analysis' in analysis:
            rt_analysis = analysis['response_time_analysis']
            html += f'''
            <div class="analysis-section">
                <h3>Response Time Analysis</h3>
                <p><strong>Mean:</strong> {rt_analysis.get('mean', 0):.3f}s</p>
                <p><strong>Median:</strong> {rt_analysis.get('median', 0):.3f}s</p>
                <p><strong>95th Percentile:</strong> {rt_analysis.get('percentiles', {}).get('p95', 0):.3f}s</p>
                <p><strong>99th Percentile:</strong> {rt_analysis.get('percentiles', {}).get('p99', 0):.3f}s</p>
                <p><strong>Standard Deviation:</strong> {rt_analysis.get('std_dev', 0):.3f}s</p>
            </div>
            '''
        
        # Recommendations
        if analysis.get('recommendations'):
            html += '<div class="recommendations"><h3>Recommendations</h3><ul>'
            for recommendation in analysis['recommendations']:
                html += f'<li>{recommendation}</li>'
            html += '</ul></div>'
        
        # Bottlenecks
        if analysis.get('bottlenecks'):
            html += '<div class="bottlenecks"><h3>Identified Bottlenecks</h3><ul>'
            for bottleneck in analysis['bottlenecks']:
                html += f'<li>{bottleneck}</li>'
            html += '</ul></div>'
        
        html += '</div>'
        return html
    
    def _generate_test_results_html(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate HTML for detailed test results."""
        html = '''
        <div class="section">
            <h2>Detailed Test Results</h2>
            <table class="test-results-table">
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Avg Response</th>
                        <th>Throughput</th>
                        <th>Error Rate</th>
                        <th>Memory</th>
                    </tr>
                </thead>
                <tbody>
        '''
        
        for test in test_results:
            metrics = test.get('metrics', {})
            status_class = 'status-passed' if test['status'] == 'passed' else 'status-failed'
            
            html += f'''
                <tr>
                    <td>{test['test_name']}</td>
                    <td class="{status_class}">{test['status'].upper()}</td>
                    <td>{test['duration']:.3f}s</td>
                    <td>{metrics.get('average_response_time', 'N/A')}</td>
                    <td>{metrics.get('requests_per_second', 'N/A')}</td>
                    <td>{metrics.get('error_rate', 'N/A')}</td>
                    <td>{metrics.get('memory_usage_mb', 'N/A')}</td>
                </tr>
            '''
        
        html += '</tbody></table></div>'
        return html
    
    async def _save_reports(self, html_content: str, analysis: Dict[str, Any], 
                           performance_data: Dict[str, Any]) -> Dict[str, str]:
        """Save reports in multiple formats."""
        paths = {}
        
        # Save HTML report
        html_path = self.output_dir / "performance_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        paths['html'] = str(html_path)
        
        # Save JSON report
        json_data = {
            'performance_data': performance_data,
            'analysis': analysis,
            'generated_at': datetime.now().isoformat()
        }
        
        json_path = self.output_dir / "performance_report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        paths['json'] = str(json_path)
        
        return paths
    
    def _generate_empty_report(self) -> str:
        """Generate empty report when no performance data is available."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Report - No Data</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .message { color: #666; font-size: 1.2em; }
            </style>
        </head>
        <body>
            <h1>Performance Test Report</h1>
            <div class="message">No performance test data available to generate report.</div>
        </body>
        </html>
        """
        
        empty_path = self.output_dir / "performance_report.html"
        with open(empty_path, 'w') as f:
            f.write(html)
        
        return str(empty_path)
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _generate_recommendations(self, analysis: Dict[str, Any], 
                                 test_results: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations based on analysis."""
        recommendations = []
        
        # Response time recommendations
        if 'response_time_analysis' in analysis:
            rt_analysis = analysis['response_time_analysis']
            if rt_analysis.get('mean', 0) > 1.0:
                recommendations.append("Consider optimizing response time - average exceeds 1 second")
            if rt_analysis.get('std_dev', 0) > rt_analysis.get('mean', 0) * 0.5:
                recommendations.append("High response time variability detected - investigate inconsistent performance")
        
        # Error rate recommendations
        if 'error_analysis' in analysis:
            error_analysis = analysis['error_analysis']
            if error_analysis.get('mean_error_rate', 0) > 0.01:  # > 1%
                recommendations.append("Error rate exceeds 1% - investigate error causes")
        
        # Resource usage recommendations
        if 'memory_analysis' in analysis:
            memory_analysis = analysis['memory_analysis']
            if memory_analysis.get('peak_usage', 0) > 1000:  # > 1GB
                recommendations.append("High memory usage detected - consider memory optimization")
        
        if 'cpu_analysis' in analysis:
            cpu_analysis = analysis['cpu_analysis']
            if cpu_analysis.get('mean_usage', 0) > 80:  # > 80%
                recommendations.append("High CPU usage - consider performance optimization or scaling")
        
        return recommendations
    
    def _identify_bottlenecks(self, analysis: Dict[str, Any], 
                            test_results: List[Dict[str, Any]]) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        # Find slowest tests
        sorted_tests = sorted(test_results, 
                            key=lambda x: x.get('metrics', {}).get('average_response_time', 0), 
                            reverse=True)
        
        if sorted_tests and len(sorted_tests) > 1:
            slowest_test = sorted_tests[0]
            slowest_time = slowest_test.get('metrics', {}).get('average_response_time', 0)
            if slowest_time > 0:
                bottlenecks.append(f"Slowest test: {slowest_test['test_name']} ({slowest_time:.3f}s)")
        
        # Find tests with high error rates
        high_error_tests = [
            test for test in test_results 
            if test.get('metrics', {}).get('error_rate', 0) > 0.05  # > 5%
        ]
        
        for test in high_error_tests:
            error_rate = test.get('metrics', {}).get('error_rate', 0) * 100
            bottlenecks.append(f"High error rate in {test['test_name']} ({error_rate:.1f}%)")
        
        return bottlenecks

if __name__ == "__main__":
    # Test the performance reporter
    print("Performance reporter module loaded successfully")