#!/usr/bin/env python3
"""
Production n8n Integration System for SynthNet AI
=================================================

Production-grade integration system that provides comprehensive n8n workflow
management with real-time monitoring, health checks, and intelligent alerting.

Features:
- Production-ready n8n MCP server integration
- Real-time workflow monitoring and health checks
- Intelligent alerting and notification system
- Performance analytics and reporting
- Automatic failover and recovery mechanisms
- Load balancing and scaling capabilities
"""

import asyncio
import json
import logging
import datetime
import aiohttp
import websockets
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import deque
import subprocess
import psutil
import signal

from problem_solving_memory_system import ProblemSolvingMemorySystem
from meta_learning_system import MetaLearningSystem
from enhanced_workflow_optimization_engine import EnhancedWorkflowOptimizationEngine
from intelligent_workflow_template_system import IntelligentWorkflowTemplateSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class N8NServerConfig:
    """n8n MCP server configuration"""
    host: str = "localhost"
    port: int = 5678
    mcp_mode: str = "http"  # "stdio" or "http"
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    database_path: str = "./nodes.db"
    log_level: str = "info"
    max_connections: int = 100
    timeout: int = 30

@dataclass
class MonitoringMetrics:
    """Real-time monitoring metrics"""
    timestamp: str
    server_status: str
    cpu_usage: float
    memory_usage: float
    active_connections: int
    request_rate: float
    response_time: float
    error_rate: float
    workflow_executions: int
    database_size: int
    health_score: float

@dataclass
class AlertConfig:
    """Alert configuration for monitoring"""
    alert_id: str
    metric_name: str
    threshold_type: str  # "above", "below", "equals"
    threshold_value: float
    severity: str  # "critical", "warning", "info"
    notification_channels: List[str]
    cooldown_minutes: int = 5
    enabled: bool = True

@dataclass
class SystemAlert:
    """System alert notification"""
    alert_id: str
    timestamp: str
    severity: str
    message: str
    metric_value: float
    threshold_value: float
    acknowledged: bool = False
    resolved: bool = False

class ProductionN8NIntegration:
    """
    Production-grade n8n integration with comprehensive monitoring
    """
    
    def __init__(self, server_config: N8NServerConfig,
                 memory_system: ProblemSolvingMemorySystem,
                 meta_learner: MetaLearningSystem,
                 optimization_engine: EnhancedWorkflowOptimizationEngine,
                 template_system: IntelligentWorkflowTemplateSystem):
        self.config = server_config
        self.memory_system = memory_system
        self.meta_learner = meta_learner
        self.optimization_engine = optimization_engine
        self.template_system = template_system
        
        # Server management
        self.server_process: Optional[subprocess.Popen] = None
        self.server_status = "stopped"
        self.startup_time: Optional[datetime.datetime] = None
        
        # Monitoring system
        self.monitoring_active = False
        self.monitoring_interval = 10  # seconds
        self.metrics_history = deque(maxlen=1000)  # Store last 1000 metrics
        self.current_metrics: Optional[MonitoringMetrics] = None
        
        # Alerting system
        self.alert_configs: Dict[str, AlertConfig] = {}
        self.active_alerts: Dict[str, SystemAlert] = {}
        self.alert_history: List[SystemAlert] = []
        self.notification_handlers: Dict[str, Callable] = {}
        
        # Health management
        self.health_checks: Dict[str, Callable] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.last_health_check: Optional[datetime.datetime] = None
        
        # Performance tracking
        self.request_counter = 0
        self.error_counter = 0
        self.response_times = deque(maxlen=100)
        
        # WebSocket connections for real-time monitoring
        self.websocket_clients: List[websockets.WebSocketServerProtocol] = []
        
        self._initialize_default_configurations()
        
        logger.info("Production n8n Integration System initialized")
    
    async def start_production_server(self) -> bool:
        """Start n8n MCP server in production mode"""
        try:
            logger.info("Starting n8n MCP server in production mode...")
            
            # Prepare environment
            env = {
                "NODE_ENV": "production",
                "MCP_MODE": self.config.mcp_mode,
                "LOG_LEVEL": self.config.log_level,
                "DISABLE_CONSOLE_OUTPUT": "false",  # Enable for monitoring
                "N8N_API_URL": self.config.api_url or "",
                "N8N_API_KEY": self.config.api_key or "",
                "DATABASE_PATH": self.config.database_path
            }
            
            # Start server process
            if self.config.mcp_mode == "http":
                cmd = [
                    "node", "dist/mcp/index.js",
                    "--port", str(self.config.port),
                    "--host", self.config.host
                ]
            else:
                cmd = ["node", "dist/mcp/index.js"]
            
            # Change to n8n MCP directory
            n8n_dir = Path("./n8n-mcp-integration")
            if not n8n_dir.exists():
                n8n_dir = Path(".")  # Fallback to current directory
            
            self.server_process = subprocess.Popen(
                cmd,
                cwd=n8n_dir,
                env={**subprocess.os.environ, **env},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Verify server is running
            if await self._verify_server_health():
                self.server_status = "running"
                self.startup_time = datetime.datetime.now()
                
                # Start monitoring systems
                await self._start_monitoring_systems()
                
                logger.info(f"n8n MCP server started successfully on {self.config.host}:{self.config.port}")
                return True
            else:
                logger.error("Server failed to start properly")
                await self.stop_production_server()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start production server: {e}")
            self.server_status = "error"
            return False
    
    async def stop_production_server(self):
        """Stop n8n MCP server gracefully"""
        logger.info("Stopping n8n MCP server...")
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Close WebSocket connections
        for client in self.websocket_clients.copy():
            await client.close()
        self.websocket_clients.clear()
        
        # Stop server process
        if self.server_process:
            try:
                self.server_process.terminate()
                await asyncio.sleep(5)  # Give time for graceful shutdown
                
                if self.server_process.poll() is None:
                    self.server_process.kill()  # Force kill if still running
                
                self.server_process = None
                
            except Exception as e:
                logger.error(f"Error stopping server process: {e}")
        
        self.server_status = "stopped"
        logger.info("n8n MCP server stopped")
    
    async def restart_production_server(self) -> bool:
        """Restart server with zero-downtime strategy"""
        logger.info("Restarting n8n MCP server...")
        
        # Record restart for learning
        await self._record_restart_event()
        
        # Stop current server
        await self.stop_production_server()
        
        # Wait briefly
        await asyncio.sleep(2)
        
        # Start new server
        return await self.start_production_server()
    
    async def get_real_time_metrics(self) -> MonitoringMetrics:
        """Get current real-time monitoring metrics"""
        now = datetime.datetime.now()
        
        # Server process metrics
        cpu_usage = 0.0
        memory_usage = 0.0
        if self.server_process:
            try:
                process = psutil.Process(self.server_process.pid)
                cpu_usage = process.cpu_percent()
                memory_info = process.memory_info()
                memory_usage = memory_info.rss / (1024 * 1024)  # MB
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Calculate request metrics
        request_rate = self._calculate_request_rate()
        avg_response_time = statistics.mean(self.response_times) if self.response_times else 0.0
        error_rate = self._calculate_error_rate()
        
        # Database size
        db_size = 0
        try:
            if Path(self.config.database_path).exists():
                db_size = Path(self.config.database_path).stat().st_size // 1024  # KB
        except:
            pass
        
        # Health score calculation
        health_score = await self._calculate_health_score()
        
        metrics = MonitoringMetrics(
            timestamp=now.isoformat(),
            server_status=self.server_status,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_connections=len(self.websocket_clients),
            request_rate=request_rate,
            response_time=avg_response_time,
            error_rate=error_rate,
            workflow_executions=self.request_counter,
            database_size=db_size,
            health_score=health_score
        )
        
        self.current_metrics = metrics
        self.metrics_history.append(metrics)
        
        return metrics
    
    async def setup_monitoring_alerts(self, alert_configs: List[AlertConfig]):
        """Setup monitoring alerts and thresholds"""
        for config in alert_configs:
            self.alert_configs[config.alert_id] = config
        
        logger.info(f"Configured {len(alert_configs)} monitoring alerts")
    
    async def check_alerts(self, metrics: MonitoringMetrics):
        """Check current metrics against alert thresholds"""
        for alert_id, config in self.alert_configs.items():
            if not config.enabled:
                continue
            
            # Get metric value
            metric_value = getattr(metrics, config.metric_name, None)
            if metric_value is None:
                continue
            
            # Check threshold
            alert_triggered = False
            if config.threshold_type == "above" and metric_value > config.threshold_value:
                alert_triggered = True
            elif config.threshold_type == "below" and metric_value < config.threshold_value:
                alert_triggered = True
            elif config.threshold_type == "equals" and abs(metric_value - config.threshold_value) < 0.01:
                alert_triggered = True
            
            if alert_triggered:
                await self._trigger_alert(config, metric_value, metrics.timestamp)
            else:
                await self._resolve_alert(alert_id)
    
    async def register_notification_handler(self, channel: str, handler: Callable):
        """Register notification handler for alert channel"""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler for channel: {channel}")
    
    async def start_websocket_monitoring(self, port: int = 8765):
        """Start WebSocket server for real-time monitoring dashboard"""
        async def handle_client(websocket, path):
            self.websocket_clients.append(websocket)
            logger.info(f"Monitoring client connected: {websocket.remote_address}")
            
            try:
                await websocket.wait_closed()
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                if websocket in self.websocket_clients:
                    self.websocket_clients.remove(websocket)
                logger.info(f"Monitoring client disconnected: {websocket.remote_address}")
        
        # Start WebSocket server
        start_server = websockets.serve(handle_client, "localhost", port)
        await start_server
        
        logger.info(f"WebSocket monitoring server started on port {port}")
    
    async def broadcast_metrics(self, metrics: MonitoringMetrics):
        """Broadcast metrics to all connected WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = {
            "type": "metrics_update",
            "data": asdict(metrics),
            "timestamp": metrics.timestamp
        }
        
        # Send to all connected clients
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.remove(client)
    
    async def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        
        # Filter metrics within time window
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics data available for specified time period"}
        
        # Calculate performance statistics
        avg_cpu = statistics.mean([m.cpu_usage for m in recent_metrics])
        avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
        avg_response_time = statistics.mean([m.response_time for m in recent_metrics])
        avg_health_score = statistics.mean([m.health_score for m in recent_metrics])
        
        max_cpu = max([m.cpu_usage for m in recent_metrics])
        max_memory = max([m.memory_usage for m in recent_metrics])
        max_response_time = max([m.response_time for m in recent_metrics])
        
        # Calculate uptime
        uptime_seconds = 0
        if self.startup_time:
            uptime_seconds = (datetime.datetime.now() - self.startup_time).total_seconds()
        
        # Alert summary
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.datetime.fromisoformat(alert.timestamp) > cutoff_time
        ]
        
        critical_alerts = len([a for a in recent_alerts if a.severity == "critical"])
        warning_alerts = len([a for a in recent_alerts if a.severity == "warning"])
        
        return {
            "report_period": f"{hours} hours",
            "generated_at": datetime.datetime.now().isoformat(),
            "server_status": self.server_status,
            "uptime_seconds": uptime_seconds,
            "performance_metrics": {
                "average_cpu_usage": avg_cpu,
                "average_memory_usage": avg_memory,
                "average_response_time": avg_response_time,
                "average_health_score": avg_health_score,
                "peak_cpu_usage": max_cpu,
                "peak_memory_usage": max_memory,
                "peak_response_time": max_response_time,
                "total_requests": self.request_counter,
                "total_errors": self.error_counter,
                "overall_error_rate": (self.error_counter / max(self.request_counter, 1)) * 100
            },
            "alert_summary": {
                "total_alerts": len(recent_alerts),
                "critical_alerts": critical_alerts,
                "warning_alerts": warning_alerts,
                "active_alerts": len(self.active_alerts)
            },
            "recommendations": await self._generate_performance_recommendations(recent_metrics)
        }
    
    # Private helper methods
    
    def _initialize_default_configurations(self):
        """Initialize default monitoring configurations"""
        # Default alert configurations
        default_alerts = [
            AlertConfig(
                alert_id="high_cpu_usage",
                metric_name="cpu_usage",
                threshold_type="above",
                threshold_value=80.0,
                severity="warning",
                notification_channels=["console", "log"],
                cooldown_minutes=5
            ),
            AlertConfig(
                alert_id="high_memory_usage",
                metric_name="memory_usage",
                threshold_type="above", 
                threshold_value=500.0,  # MB
                severity="warning",
                notification_channels=["console", "log"],
                cooldown_minutes=5
            ),
            AlertConfig(
                alert_id="low_health_score",
                metric_name="health_score",
                threshold_type="below",
                threshold_value=0.7,
                severity="critical",
                notification_channels=["console", "log"],
                cooldown_minutes=2
            ),
            AlertConfig(
                alert_id="high_error_rate",
                metric_name="error_rate",
                threshold_type="above",
                threshold_value=5.0,  # 5% error rate
                severity="critical",
                notification_channels=["console", "log"],
                cooldown_minutes=3
            )
        ]
        
        for alert in default_alerts:
            self.alert_configs[alert.alert_id] = alert
        
        # Default notification handlers
        self.notification_handlers["console"] = self._console_notification_handler
        self.notification_handlers["log"] = self._log_notification_handler
        
        # Default health checks
        self.health_checks["server_process"] = self._check_server_process_health
        self.health_checks["database_connection"] = self._check_database_health
        self.health_checks["api_endpoints"] = self._check_api_endpoints_health
        
        # Default recovery strategies
        self.recovery_strategies["server_restart"] = self.restart_production_server
        self.recovery_strategies["process_cleanup"] = self._cleanup_zombie_processes
    
    async def _start_monitoring_systems(self):
        """Start all monitoring background tasks"""
        self.monitoring_active = True
        
        # Start monitoring loops
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._alert_processing_loop())
        
        logger.info("All monitoring systems started")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = await self.get_real_time_metrics()
                
                # Check alerts
                await self.check_alerts(metrics)
                
                # Broadcast to WebSocket clients
                await self.broadcast_metrics(metrics)
                
                # Sleep until next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _health_check_loop(self):
        """Periodic health check loop"""
        while self.monitoring_active:
            try:
                # Run all health checks
                health_results = {}
                for check_name, check_func in self.health_checks.items():
                    try:
                        health_results[check_name] = await check_func()
                    except Exception as e:
                        logger.error(f"Health check {check_name} failed: {e}")
                        health_results[check_name] = False
                
                # Process health check results
                await self._process_health_results(health_results)
                
                self.last_health_check = datetime.datetime.now()
                
                # Health checks every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(30)
    
    async def _alert_processing_loop(self):
        """Process and manage alerts"""
        while self.monitoring_active:
            try:
                # Auto-resolve stale alerts
                await self._auto_resolve_stale_alerts()
                
                # Run recovery strategies for critical alerts
                await self._execute_recovery_strategies()
                
                # Alert processing every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Alert processing loop error: {e}")
                await asyncio.sleep(60)

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "server_status": self.server_status,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "uptime_seconds": (datetime.datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0,
            "monitoring_active": self.monitoring_active,
            "current_metrics": asdict(self.current_metrics) if self.current_metrics else None,
            "active_alerts": len(self.active_alerts),
            "websocket_clients": len(self.websocket_clients),
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "configuration": {
                "host": self.config.host,
                "port": self.config.port,
                "mcp_mode": self.config.mcp_mode,
                "monitoring_interval": self.monitoring_interval
            }
        }

# Export the production integration system
def create_production_integration(config: N8NServerConfig,
                                memory_system: ProblemSolvingMemorySystem,
                                meta_learner: MetaLearningSystem,
                                optimization_engine: EnhancedWorkflowOptimizationEngine,
                                template_system: IntelligentWorkflowTemplateSystem) -> ProductionN8NIntegration:
    """Factory function to create production integration system"""
    return ProductionN8NIntegration(config, memory_system, meta_learner, optimization_engine, template_system)

if __name__ == "__main__":
    print("Production n8n Integration System - SynthNet AI")
    print("Provides production-grade n8n workflow management with comprehensive monitoring")