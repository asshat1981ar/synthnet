#!/usr/bin/env python3
"""
MCP Performance and Load Testing Framework
Comprehensive performance, load, and stress testing for MCP servers.
"""

import asyncio
import logging
import time
import json
import statistics
import subprocess
import psutil
import resource
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import aiohttp
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a test run."""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    duration: float
    requests_per_second: float
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    network_bytes_sent: int = 0
    network_bytes_received: int = 0

@dataclass
class LoadTestConfig:
    """Configuration for load testing."""
    concurrent_users: int = 10
    requests_per_user: int = 100
    ramp_up_duration: int = 30  # seconds
    test_duration: int = 300    # seconds
    request_timeout: int = 30
    think_time: float = 0.1     # seconds between requests
    test_scenario: str = "basic"

@dataclass
class StressTestConfig:
    """Configuration for stress testing."""
    max_concurrent_users: int = 1000
    increment_users: int = 10
    increment_duration: int = 30  # seconds
    failure_threshold: float = 0.05  # 5% error rate
    response_time_threshold: float = 5.0  # seconds

class PerformanceTester:
    """Comprehensive performance testing for MCP servers."""
    
    def __init__(self):
        """Initialize the performance tester."""
        self.server_process: Optional[subprocess.Popen] = None
        self.monitoring_active = False
        self.resource_monitor_task: Optional[asyncio.Task] = None
        self.metrics_history: List[Dict[str, Any]] = []
        
    async def run_performance_suite(self, server_path: str) -> List[Dict[str, Any]]:
        """Run complete performance test suite."""
        logger.info(f"Starting performance testing for: {server_path}")
        
        results = []
        
        try:
            # Start server for testing
            await self._start_server_for_testing(server_path)
            
            # Basic performance test
            basic_result = await self.run_basic_performance_test()
            results.append(basic_result)
            
            # Load testing with different concurrency levels
            for concurrent_users in [1, 5, 10, 25, 50]:
                load_config = LoadTestConfig(
                    concurrent_users=concurrent_users,
                    requests_per_user=50,
                    test_duration=60
                )
                load_result = await self.run_load_test(load_config)
                results.append(load_result)
            
            # Stress testing
            stress_config = StressTestConfig(
                max_concurrent_users=200,
                increment_users=20,
                increment_duration=30
            )
            stress_result = await self.run_stress_test(stress_config)
            results.append(stress_result)
            
            # Endurance testing
            endurance_result = await self.run_endurance_test(duration_minutes=10)
            results.append(endurance_result)
            
            # Memory leak detection
            memory_result = await self.run_memory_leak_test()
            results.append(memory_result)
            
        except Exception as e:
            logger.error(f"Performance testing failed: {e}")
            results.append({
                "test_name": "performance_suite_error",
                "passed": False,
                "message": f"Performance suite failed: {str(e)}",
                "duration": 0.0,
                "error": str(e)
            })
        
        finally:
            await self._cleanup_server()
        
        return results
    
    async def run_basic_performance_test(self) -> Dict[str, Any]:
        """Run basic performance test with single user."""
        logger.info("Running basic performance test")
        
        start_time = time.time()
        response_times = []
        errors = 0
        
        # Start monitoring
        await self._start_resource_monitoring()
        
        try:
            # Run 100 sequential requests
            for i in range(100):
                try:
                    request_start = time.time()
                    await self._make_test_request()
                    response_time = time.time() - request_start
                    response_times.append(response_time)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    errors += 1
                    logger.warning(f"Request {i} failed: {e}")
            
            duration = time.time() - start_time
            
            if response_times:
                metrics = PerformanceMetrics(
                    test_name="basic_performance",
                    total_requests=100,
                    successful_requests=len(response_times),
                    failed_requests=errors,
                    duration=duration,
                    requests_per_second=len(response_times) / duration,
                    average_response_time=statistics.mean(response_times),
                    median_response_time=statistics.median(response_times),
                    p95_response_time=self._percentile(response_times, 95),
                    p99_response_time=self._percentile(response_times, 99),
                    min_response_time=min(response_times),
                    max_response_time=max(response_times),
                    error_rate=errors / 100,
                    memory_usage_mb=self._get_server_memory_usage(),
                    cpu_usage_percent=self._get_server_cpu_usage()
                )
            else:
                metrics = PerformanceMetrics(
                    test_name="basic_performance",
                    total_requests=100,
                    successful_requests=0,
                    failed_requests=100,
                    duration=duration,
                    requests_per_second=0,
                    average_response_time=0,
                    median_response_time=0,
                    p95_response_time=0,
                    p99_response_time=0,
                    min_response_time=0,
                    max_response_time=0,
                    error_rate=1.0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0
                )
            
            return self._format_performance_result(metrics, errors == 0)
            
        except Exception as e:
            return {
                "test_name": "basic_performance",
                "passed": False,
                "message": f"Basic performance test failed: {str(e)}",
                "duration": time.time() - start_time,
                "error": str(e)
            }
        
        finally:
            await self._stop_resource_monitoring()
    
    async def run_load_test(self, config: LoadTestConfig) -> Dict[str, Any]:
        """Run load test with multiple concurrent users."""
        logger.info(f"Running load test - {config.concurrent_users} users, {config.requests_per_user} requests each")
        
        start_time = time.time()
        all_response_times = []
        total_errors = 0
        
        # Start monitoring
        await self._start_resource_monitoring()
        
        try:
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(config.concurrent_users)
            
            # Create tasks for concurrent users
            tasks = []
            for user_id in range(config.concurrent_users):
                task = asyncio.create_task(
                    self._simulate_user_load(user_id, config, semaphore)
                )
                tasks.append(task)
                
                # Gradual ramp-up
                if config.ramp_up_duration > 0:
                    ramp_delay = config.ramp_up_duration / config.concurrent_users
                    await asyncio.sleep(ramp_delay)
            
            # Wait for all users to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate results
            for result in results:
                if isinstance(result, dict):
                    all_response_times.extend(result.get('response_times', []))
                    total_errors += result.get('errors', 0)
                elif isinstance(result, Exception):
                    total_errors += config.requests_per_user
            
            duration = time.time() - start_time
            total_requests = config.concurrent_users * config.requests_per_user
            
            if all_response_times:
                metrics = PerformanceMetrics(
                    test_name=f"load_test_{config.concurrent_users}_users",
                    total_requests=total_requests,
                    successful_requests=len(all_response_times),
                    failed_requests=total_errors,
                    duration=duration,
                    requests_per_second=len(all_response_times) / duration,
                    average_response_time=statistics.mean(all_response_times),
                    median_response_time=statistics.median(all_response_times),
                    p95_response_time=self._percentile(all_response_times, 95),
                    p99_response_time=self._percentile(all_response_times, 99),
                    min_response_time=min(all_response_times),
                    max_response_time=max(all_response_times),
                    error_rate=total_errors / total_requests,
                    memory_usage_mb=self._get_server_memory_usage(),
                    cpu_usage_percent=self._get_server_cpu_usage()
                )
                
                passed = (metrics.error_rate < 0.05 and 
                         metrics.p95_response_time < 5.0)
            else:
                metrics = PerformanceMetrics(
                    test_name=f"load_test_{config.concurrent_users}_users",
                    total_requests=total_requests,
                    successful_requests=0,
                    failed_requests=total_requests,
                    duration=duration,
                    requests_per_second=0,
                    average_response_time=0,
                    median_response_time=0,
                    p95_response_time=0,
                    p99_response_time=0,
                    min_response_time=0,
                    max_response_time=0,
                    error_rate=1.0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0
                )
                passed = False
            
            return self._format_performance_result(metrics, passed)
            
        except Exception as e:
            return {
                "test_name": f"load_test_{config.concurrent_users}_users",
                "passed": False,
                "message": f"Load test failed: {str(e)}",
                "duration": time.time() - start_time,
                "error": str(e)
            }
        
        finally:
            await self._stop_resource_monitoring()
    
    async def run_stress_test(self, config: StressTestConfig) -> Dict[str, Any]:
        """Run stress test to find breaking point."""
        logger.info(f"Running stress test - up to {config.max_concurrent_users} users")
        
        start_time = time.time()
        breaking_point = None
        stress_results = []
        
        try:
            current_users = config.increment_users
            
            while current_users <= config.max_concurrent_users:
                logger.info(f"Stress testing with {current_users} concurrent users")
                
                # Run load test at current concurrency level
                load_config = LoadTestConfig(
                    concurrent_users=current_users,
                    requests_per_user=20,
                    test_duration=config.increment_duration,
                    ramp_up_duration=10
                )
                
                result = await self.run_load_test(load_config)
                metrics_data = result.get('metrics', {})
                
                stress_results.append({
                    'concurrent_users': current_users,
                    'error_rate': metrics_data.get('error_rate', 0),
                    'avg_response_time': metrics_data.get('average_response_time', 0),
                    'p95_response_time': metrics_data.get('p95_response_time', 0),
                    'requests_per_second': metrics_data.get('requests_per_second', 0)
                })
                
                # Check if we've hit the breaking point
                error_rate = metrics_data.get('error_rate', 0)
                avg_response_time = metrics_data.get('average_response_time', 0)
                
                if (error_rate > config.failure_threshold or 
                    avg_response_time > config.response_time_threshold):
                    breaking_point = current_users
                    logger.info(f"Breaking point found at {current_users} concurrent users")
                    break
                
                current_users += config.increment_users
                
                # Brief pause between stress levels
                await asyncio.sleep(5)
            
            duration = time.time() - start_time
            
            return {
                "test_name": "stress_test",
                "passed": breaking_point is not None,
                "message": (f"Breaking point: {breaking_point} users" if breaking_point 
                           else f"No breaking point found up to {config.max_concurrent_users} users"),
                "duration": duration,
                "metrics": {
                    "breaking_point_users": breaking_point,
                    "max_tested_users": current_users - config.increment_users,
                    "stress_results": stress_results
                }
            }
            
        except Exception as e:
            return {
                "test_name": "stress_test",
                "passed": False,
                "message": f"Stress test failed: {str(e)}",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    async def run_endurance_test(self, duration_minutes: int = 30) -> Dict[str, Any]:
        """Run endurance test to detect performance degradation over time."""
        logger.info(f"Running endurance test for {duration_minutes} minutes")
        
        start_time = time.time()
        target_duration = duration_minutes * 60
        
        response_times_over_time = []
        memory_usage_over_time = []
        error_counts_over_time = []
        
        # Start monitoring
        await self._start_resource_monitoring()
        
        try:
            end_time = start_time + target_duration
            interval_duration = 60  # 1 minute intervals
            
            while time.time() < end_time:
                interval_start = time.time()
                interval_response_times = []
                interval_errors = 0
                
                # Run requests for this interval
                while time.time() - interval_start < interval_duration:
                    try:
                        request_start = time.time()
                        await self._make_test_request()
                        response_time = time.time() - request_start
                        interval_response_times.append(response_time)
                        
                        await asyncio.sleep(0.5)  # 2 requests per second
                        
                    except Exception:
                        interval_errors += 1
                
                # Record metrics for this interval
                if interval_response_times:
                    avg_response_time = statistics.mean(interval_response_times)
                    response_times_over_time.append(avg_response_time)
                
                memory_usage = self._get_server_memory_usage()
                memory_usage_over_time.append(memory_usage)
                error_counts_over_time.append(interval_errors)
                
                logger.info(f"Endurance test interval - Avg response: {avg_response_time:.3f}s, "
                           f"Memory: {memory_usage:.1f}MB, Errors: {interval_errors}")
            
            duration = time.time() - start_time
            
            # Analyze endurance test results
            performance_degradation = self._analyze_performance_degradation(response_times_over_time)
            memory_leak_detected = self._analyze_memory_trend(memory_usage_over_time)
            error_rate_trend = self._analyze_error_trend(error_counts_over_time)
            
            passed = (not performance_degradation and 
                     not memory_leak_detected and 
                     not error_rate_trend)
            
            return {
                "test_name": "endurance_test",
                "passed": passed,
                "message": f"Endurance test completed - {duration_minutes} minutes",
                "duration": duration,
                "metrics": {
                    "duration_minutes": duration_minutes,
                    "performance_degradation": performance_degradation,
                    "memory_leak_detected": memory_leak_detected,
                    "error_rate_increasing": error_rate_trend,
                    "response_times_over_time": response_times_over_time,
                    "memory_usage_over_time": memory_usage_over_time,
                    "error_counts_over_time": error_counts_over_time
                }
            }
            
        except Exception as e:
            return {
                "test_name": "endurance_test",
                "passed": False,
                "message": f"Endurance test failed: {str(e)}",
                "duration": time.time() - start_time,
                "error": str(e)
            }
        
        finally:
            await self._stop_resource_monitoring()
    
    async def run_memory_leak_test(self) -> Dict[str, Any]:
        """Test for memory leaks by monitoring memory usage over time."""
        logger.info("Running memory leak detection test")
        
        start_time = time.time()
        memory_samples = []
        
        try:
            # Take baseline memory measurement
            baseline_memory = self._get_server_memory_usage()
            memory_samples.append(baseline_memory)
            
            # Run requests while monitoring memory
            for cycle in range(10):  # 10 cycles of activity
                # High activity period
                for _ in range(100):
                    try:
                        await self._make_test_request()
                        await asyncio.sleep(0.01)
                    except Exception:
                        pass
                
                # Measure memory after activity
                memory_usage = self._get_server_memory_usage()
                memory_samples.append(memory_usage)
                
                # Allow some time for garbage collection
                await asyncio.sleep(5)
                
                # Measure memory after GC opportunity
                memory_after_gc = self._get_server_memory_usage()
                memory_samples.append(memory_after_gc)
                
                logger.info(f"Memory leak test cycle {cycle + 1}: "
                           f"After activity: {memory_usage:.1f}MB, "
                           f"After GC: {memory_after_gc:.1f}MB")
            
            duration = time.time() - start_time
            
            # Analyze memory trend
            memory_increase = memory_samples[-1] - baseline_memory
            memory_leak_threshold = 50  # MB
            
            # Check for consistent memory growth
            growing_samples = 0
            for i in range(1, len(memory_samples)):
                if memory_samples[i] > memory_samples[i-1]:
                    growing_samples += 1
            
            growth_rate = growing_samples / (len(memory_samples) - 1)
            memory_leak_detected = (memory_increase > memory_leak_threshold or 
                                   growth_rate > 0.8)
            
            return {
                "test_name": "memory_leak_test",
                "passed": not memory_leak_detected,
                "message": (f"Memory leak detected - increased by {memory_increase:.1f}MB" 
                           if memory_leak_detected else "No memory leak detected"),
                "duration": duration,
                "metrics": {
                    "baseline_memory_mb": baseline_memory,
                    "final_memory_mb": memory_samples[-1],
                    "memory_increase_mb": memory_increase,
                    "growth_rate": growth_rate,
                    "memory_samples": memory_samples,
                    "leak_detected": memory_leak_detected
                }
            }
            
        except Exception as e:
            return {
                "test_name": "memory_leak_test",
                "passed": False,
                "message": f"Memory leak test failed: {str(e)}",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    async def _start_server_for_testing(self, server_path: str):
        """Start server for performance testing."""
        # This is a simplified implementation - in practice, you'd want
        # more robust server management
        logger.info(f"Starting server for performance testing: {server_path}")
        
        server_path_obj = Path(server_path)
        
        if server_path_obj.suffix == '.py':
            cmd = [sys.executable, str(server_path)]
        elif server_path_obj.suffix == '.js':
            cmd = ['node', str(server_path)]
        else:
            raise ValueError("Unsupported server type for performance testing")
        
        self.server_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        if self.server_process.poll() is not None:
            raise RuntimeError("Server failed to start")
    
    async def _make_test_request(self):
        """Make a test request to the server."""
        if not self.server_process:
            raise RuntimeError("Server not started")
        
        # Send a simple tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": f"perf-{time.time()}",
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(request) + '\n'
        self.server_process.stdin.write(request_json)
        self.server_process.stdin.flush()
        
        # Read response (simplified)
        response_line = self.server_process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")
        
        response = json.loads(response_line.strip())
        if 'error' in response:
            raise RuntimeError(f"Server error: {response['error']}")
    
    async def _simulate_user_load(self, user_id: int, config: LoadTestConfig, 
                                  semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Simulate load from a single user."""
        async with semaphore:
            response_times = []
            errors = 0
            
            for request_num in range(config.requests_per_user):
                try:
                    request_start = time.time()
                    await self._make_test_request()
                    response_time = time.time() - request_start
                    response_times.append(response_time)
                    
                    # Think time between requests
                    if config.think_time > 0:
                        await asyncio.sleep(config.think_time)
                        
                except Exception as e:
                    errors += 1
                    logger.debug(f"User {user_id} request {request_num} failed: {e}")
            
            return {
                'user_id': user_id,
                'response_times': response_times,
                'errors': errors
            }
    
    async def _start_resource_monitoring(self):
        """Start monitoring server resource usage."""
        self.monitoring_active = True
        self.resource_monitor_task = asyncio.create_task(self._monitor_resources())
    
    async def _stop_resource_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring_active = False
        if self.resource_monitor_task:
            self.resource_monitor_task.cancel()
            try:
                await self.resource_monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_resources(self):
        """Monitor server resource usage continuously."""
        while self.monitoring_active:
            try:
                timestamp = time.time()
                memory_mb = self._get_server_memory_usage()
                cpu_percent = self._get_server_cpu_usage()
                
                self.metrics_history.append({
                    'timestamp': timestamp,
                    'memory_mb': memory_mb,
                    'cpu_percent': cpu_percent
                })
                
                await asyncio.sleep(1)  # Sample every second
                
            except Exception as e:
                logger.warning(f"Resource monitoring error: {e}")
                await asyncio.sleep(1)
    
    def _get_server_memory_usage(self) -> float:
        """Get server process memory usage in MB."""
        try:
            if self.server_process:
                process = psutil.Process(self.server_process.pid)
                memory_info = process.memory_info()
                return memory_info.rss / 1024 / 1024  # Convert bytes to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return 0.0
    
    def _get_server_cpu_usage(self) -> float:
        """Get server process CPU usage percentage."""
        try:
            if self.server_process:
                process = psutil.Process(self.server_process.pid)
                return process.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return 0.0
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _format_performance_result(self, metrics: PerformanceMetrics, passed: bool) -> Dict[str, Any]:
        """Format performance metrics into result dictionary."""
        return {
            "test_name": metrics.test_name,
            "passed": passed,
            "message": f"Performance test completed - {metrics.requests_per_second:.1f} req/s",
            "duration": metrics.duration,
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "requests_per_second": metrics.requests_per_second,
                "average_response_time": metrics.average_response_time,
                "median_response_time": metrics.median_response_time,
                "p95_response_time": metrics.p95_response_time,
                "p99_response_time": metrics.p99_response_time,
                "min_response_time": metrics.min_response_time,
                "max_response_time": metrics.max_response_time,
                "error_rate": metrics.error_rate,
                "memory_usage_mb": metrics.memory_usage_mb,
                "cpu_usage_percent": metrics.cpu_usage_percent
            }
        }
    
    def _analyze_performance_degradation(self, response_times: List[float]) -> bool:
        """Analyze if performance degraded over time."""
        if len(response_times) < 3:
            return False
        
        # Compare first third with last third
        first_third = response_times[:len(response_times)//3]
        last_third = response_times[-len(response_times)//3:]
        
        if first_third and last_third:
            first_avg = statistics.mean(first_third)
            last_avg = statistics.mean(last_third)
            
            # Performance degraded if last third is 50% slower
            return last_avg > first_avg * 1.5
        
        return False
    
    def _analyze_memory_trend(self, memory_samples: List[float]) -> bool:
        """Analyze if memory usage shows upward trend (potential leak)."""
        if len(memory_samples) < 3:
            return False
        
        # Check if memory generally increases over time
        increases = 0
        for i in range(1, len(memory_samples)):
            if memory_samples[i] > memory_samples[i-1]:
                increases += 1
        
        # Memory leak if more than 70% of samples show increase
        growth_rate = increases / (len(memory_samples) - 1)
        return growth_rate > 0.7
    
    def _analyze_error_trend(self, error_counts: List[int]) -> bool:
        """Analyze if error rate is increasing over time."""
        if len(error_counts) < 3:
            return False
        
        # Compare first half with second half
        mid_point = len(error_counts) // 2
        first_half = error_counts[:mid_point]
        second_half = error_counts[mid_point:]
        
        if first_half and second_half:
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            # Error rate trend if second half has significantly more errors
            return second_avg > first_avg * 2
        
        return False
    
    async def _cleanup_server(self):
        """Clean up server process and resources."""
        await self._stop_resource_monitoring()
        
        if self.server_process:
            try:
                self.server_process.terminate()
                await asyncio.sleep(1)
                
                if self.server_process.poll() is None:
                    self.server_process.kill()
                    
            except Exception as e:
                logger.error(f"Error cleaning up server: {e}")
            finally:
                self.server_process = None

if __name__ == "__main__":
    import sys
    
    async def main():
        parser = argparse.ArgumentParser(description="MCP Performance Tester")
        parser.add_argument("server_path", help="Path to MCP server to test")
        parser.add_argument("--output", help="Output file for results (JSON)")
        parser.add_argument("--test-type", choices=['basic', 'load', 'stress', 'endurance'], 
                           default='basic', help="Type of performance test")
        parser.add_argument("--concurrent-users", type=int, default=10, 
                           help="Number of concurrent users (load test)")
        parser.add_argument("--duration", type=int, default=60, 
                           help="Test duration in seconds")
        
        args = parser.parse_args()
        
        tester = PerformanceTester()
        
        if args.test_type == 'basic':
            results = [await tester.run_basic_performance_test()]
        elif args.test_type == 'load':
            config = LoadTestConfig(concurrent_users=args.concurrent_users, 
                                   test_duration=args.duration)
            results = [await tester.run_load_test(config)]
        elif args.test_type == 'stress':
            config = StressTestConfig()
            results = [await tester.run_stress_test(config)]
        elif args.test_type == 'endurance':
            results = [await tester.run_endurance_test(args.duration // 60)]
        else:
            results = await tester.run_performance_suite(args.server_path)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            print(json.dumps(results, indent=2))
    
    asyncio.run(main())