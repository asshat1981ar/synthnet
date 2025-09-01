#!/usr/bin/env python3
"""
Comprehensive n8n Orchestrator for SynthNet AI
==============================================

Master orchestrator that integrates all n8n systems into a unified,
intelligent workflow automation platform with complete AI-driven optimization.

This system brings together:
- Enhanced Workflow Optimization Engine
- Intelligent Template System  
- Production Integration & Monitoring
- Self-Optimizing Deployment System
- SynthNet AI Learning Systems

Features:
- Unified workflow lifecycle management
- End-to-end AI-driven optimization
- Comprehensive monitoring and analytics
- Intelligent decision making
- Self-healing and adaptive capabilities
"""

import asyncio
import json
import logging
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# SynthNet Core Systems
from problem_solving_memory_system import ProblemSolvingMemorySystem
from meta_learning_system import MetaLearningSystem
from self_improvement_orchestrator import SelfImprovementOrchestrator

# n8n Integration Systems
from enhanced_workflow_optimization_engine import EnhancedWorkflowOptimizationEngine, create_optimization_engine
from intelligent_workflow_template_system import IntelligentWorkflowTemplateSystem, create_template_system, TemplateGenerationContext
from production_n8n_integration import ProductionN8NIntegration, create_production_integration, N8NServerConfig
from self_optimizing_workflow_deployment import SelfOptimizingWorkflowDeployment, create_deployment_system, DeploymentConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class N8NOrchestrationConfig:
    """Configuration for the complete n8n orchestration system"""
    # Server configuration
    n8n_server_config: N8NServerConfig
    
    # Optimization settings
    optimization_enabled: bool = True
    optimization_interval_minutes: int = 5
    auto_optimization_threshold: float = 0.8
    
    # Template system settings
    template_learning_enabled: bool = True
    template_evolution_threshold: float = 0.7
    cross_domain_learning: bool = True
    
    # Deployment settings
    default_deployment_strategy: str = "canary"
    auto_scaling_enabled: bool = True
    self_healing_enabled: bool = True
    
    # Monitoring settings
    monitoring_interval_seconds: int = 10
    health_check_interval_seconds: int = 30
    alert_thresholds: Dict[str, float] = None
    
    # Learning settings
    meta_learning_interval_minutes: int = 30
    problem_solving_integration: bool = True
    continuous_improvement: bool = True

class ComprehensiveN8NOrchestrator:
    """
    Master orchestrator for all n8n AI systems
    """
    
    def __init__(self, config: N8NOrchestrationConfig):
        self.config = config
        
        # Initialize core SynthNet systems
        self.memory_system = ProblemSolvingMemorySystem()
        self.meta_learner = MetaLearningSystem(self.memory_system)
        self.improvement_orchestrator = SelfImprovementOrchestrator(
            self.memory_system, self.meta_learner
        )
        
        # n8n Integration systems (to be initialized)
        self.optimization_engine: Optional[EnhancedWorkflowOptimizationEngine] = None
        self.template_system: Optional[IntelligentWorkflowTemplateSystem] = None
        self.production_integration: Optional[ProductionN8NIntegration] = None
        self.deployment_system: Optional[SelfOptimizingWorkflowDeployment] = None
        
        # Orchestration state
        self.orchestration_active = False
        self.initialization_complete = False
        self.system_health: Dict[str, Any] = {}
        
        # Performance tracking
        self.orchestration_metrics: Dict[str, Any] = {}
        self.system_analytics: Dict[str, Any] = {}
        
        logger.info("Comprehensive n8n Orchestrator initialized")
    
    async def initialize_all_systems(self):
        """Initialize all n8n integration systems"""
        logger.info("Initializing comprehensive n8n orchestration systems...")
        
        try:
            # Initialize systems in correct dependency order
            
            # 1. Optimization Engine
            self.optimization_engine = await create_optimization_engine(
                self.memory_system, self.meta_learner, self.improvement_orchestrator
            )
            logger.info("✓ Optimization Engine initialized")
            
            # 2. Template System
            self.template_system = await create_template_system(
                self.memory_system, self.meta_learner, self.optimization_engine
            )
            logger.info("✓ Template System initialized")
            
            # 3. Production Integration
            self.production_integration = create_production_integration(
                self.config.n8n_server_config,
                self.memory_system,
                self.meta_learner, 
                self.optimization_engine,
                self.template_system
            )
            logger.info("✓ Production Integration initialized")
            
            # 4. Deployment System
            self.deployment_system = create_deployment_system(
                self.memory_system,
                self.meta_learner,
                self.optimization_engine,
                self.template_system,
                self.production_integration
            )
            logger.info("✓ Deployment System initialized")
            
            self.initialization_complete = True
            logger.info("🎉 All n8n orchestration systems initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize systems: {e}")
            raise
    
    async def start_orchestration(self):
        """Start the complete n8n orchestration system"""
        if not self.initialization_complete:
            await self.initialize_all_systems()
        
        logger.info("Starting comprehensive n8n orchestration...")
        
        try:
            # Start production server
            server_started = await self.production_integration.start_production_server()
            if not server_started:
                raise Exception("Failed to start production n8n server")
            
            # Start optimization engine
            if self.config.optimization_enabled:
                asyncio.create_task(self.optimization_engine.start_optimization_engine())
            
            # Start deployment system optimization
            asyncio.create_task(self.deployment_system.start_continuous_optimization())
            
            # Start orchestration loops
            orchestration_tasks = [
                self._master_orchestration_loop(),
                self._system_health_monitoring_loop(),
                self._analytics_collection_loop(),
                self._learning_integration_loop()
            ]
            
            self.orchestration_active = True
            
            logger.info("🚀 Comprehensive n8n orchestration started successfully")
            
            # Run all orchestration tasks
            await asyncio.gather(*orchestration_tasks)
            
        except Exception as e:
            logger.error(f"Failed to start orchestration: {e}")
            await self.stop_orchestration()
            raise
    
    async def stop_orchestration(self):
        """Stop all orchestration systems gracefully"""
        logger.info("Stopping comprehensive n8n orchestration...")
        
        self.orchestration_active = False
        
        # Stop production server
        if self.production_integration:
            await self.production_integration.stop_production_server()
        
        # Stop optimization engines
        if self.optimization_engine:
            self.optimization_engine.monitoring_active = False
        
        if self.deployment_system:
            self.deployment_system.optimization_active = False
        
        logger.info("Comprehensive n8n orchestration stopped")
    
    async def create_intelligent_workflow(self, objective: str, 
                                        requirements: List[str],
                                        domain: str = "general",
                                        deployment_environment: str = "development") -> Dict[str, Any]:
        """Create workflow using full AI intelligence"""
        
        logger.info(f"Creating intelligent workflow: {objective}")
        
        # Generate template using AI
        context = TemplateGenerationContext(
            objective=objective,
            domain=domain,
            requirements=requirements,
            constraints={},
            expected_performance={"success_rate": 0.9, "throughput": 100.0},
            user_preferences={},
            historical_context=[],
            meta_learning_guidance={}
        )
        
        template = await self.template_system.generate_intelligent_template(context)
        
        # Create deployment configuration
        deployment_config = DeploymentConfig(
            deployment_id=f"deploy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            workflow_template_id=template.template_id,
            environment=deployment_environment,
            deployment_strategy=self.config.default_deployment_strategy,
            resource_allocation={"cpu": "1", "memory": "512Mi"},
            scaling_config={"min_replicas": 1, "max_replicas": 3},
            monitoring_config={"enabled": True, "interval": 30},
            rollback_config={"enabled": True, "threshold": 0.5},
            optimization_settings={"enabled": True, "target_improvement": 0.15}
        )
        
        # Deploy with optimization
        deployment = await self.deployment_system.deploy_workflow(
            template.template_id, deployment_config
        )
        
        # Predict performance
        performance_prediction = await self.deployment_system.predict_deployment_performance(
            template.template_id, deployment_environment
        )
        
        # Record creation pattern for learning
        await self._record_workflow_creation_pattern(
            objective, template, deployment, performance_prediction
        )
        
        return {
            "workflow_created": True,
            "template": asdict(template),
            "deployment": asdict(deployment),
            "performance_prediction": performance_prediction,
            "learning_insights": template.learning_insights,
            "next_steps": [
                "Monitor deployment performance",
                "Wait for optimization cycle",
                "Review analytics dashboard"
            ]
        }
    
    async def optimize_all_workflows(self) -> Dict[str, Any]:
        """Run comprehensive optimization on all active workflows"""
        
        logger.info("Running comprehensive workflow optimization...")
        
        optimization_results = {}
        
        # Optimize all active deployments
        for deployment_id in self.deployment_system.active_deployments.keys():
            try:
                result = await self.deployment_system.optimize_deployment(deployment_id)
                optimization_results[deployment_id] = result
            except Exception as e:
                optimization_results[deployment_id] = {"error": str(e)}
        
        # Evolve templates based on performance
        template_evolutions = {}
        for template_id, template in self.template_system.templates.items():
            if template.usage_count > 5:  # Only evolve used templates
                try:
                    performance_data = self.optimization_engine.workflow_metrics.get(template_id, [])
                    evolved = await self.template_system.evolve_template(template_id, performance_data)
                    if evolved and evolved.template_id != template_id:
                        template_evolutions[template_id] = evolved.template_id
                except Exception as e:
                    template_evolutions[template_id] = {"error": str(e)}
        
        # Apply cross-domain learning
        cross_domain_insights = []
        domains = list(set(template.category for template in self.template_system.templates.values()))
        for i, source_domain in enumerate(domains):
            for target_domain in domains[i+1:]:
                insights = await self.template_system.cross_domain_knowledge_transfer(
                    source_domain, target_domain
                )
                cross_domain_insights.extend(insights)
        
        return {
            "optimization_completed": True,
            "deployments_optimized": len(optimization_results),
            "deployment_results": optimization_results,
            "templates_evolved": len(template_evolutions),
            "template_evolutions": template_evolutions,
            "cross_domain_insights": len(cross_domain_insights),
            "insights_details": cross_domain_insights[:5]  # First 5 insights
        }
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        
        # Collect analytics from all systems
        optimization_analytics = {}
        template_analytics = {}
        production_analytics = {}
        deployment_analytics = {}
        
        try:
            # Get optimization engine analytics
            for workflow_id in self.optimization_engine.workflow_metrics.keys():
                optimization_analytics[workflow_id] = await self.optimization_engine.get_optimization_report(workflow_id)
        except Exception as e:
            logger.error(f"Error collecting optimization analytics: {e}")
        
        try:
            # Get template system analytics
            for template_id in self.template_system.templates.keys():
                template_analytics[template_id] = await self.template_system.get_template_performance_report(template_id)
        except Exception as e:
            logger.error(f"Error collecting template analytics: {e}")
        
        try:
            # Get production system analytics
            production_analytics = await self.production_integration.generate_performance_report(24)
        except Exception as e:
            logger.error(f"Error collecting production analytics: {e}")
        
        try:
            # Get deployment analytics
            deployment_analytics = await self.deployment_system.get_deployment_analytics()
        except Exception as e:
            logger.error(f"Error collecting deployment analytics: {e}")
        
        # Meta-learning insights
        meta_learning_summary = {}
        try:
            meta_learning_summary = await self._get_meta_learning_summary()
        except Exception as e:
            logger.error(f"Error collecting meta-learning summary: {e}")
        
        return {
            "generated_at": datetime.datetime.now().isoformat(),
            "system_status": {
                "orchestration_active": self.orchestration_active,
                "initialization_complete": self.initialization_complete,
                "systems_healthy": await self._check_all_systems_health()
            },
            "optimization_analytics": optimization_analytics,
            "template_analytics": template_analytics,
            "production_analytics": production_analytics,
            "deployment_analytics": deployment_analytics,
            "meta_learning_summary": meta_learning_summary,
            "overall_performance": await self._calculate_overall_performance()
        }
    
    # Background orchestration loops
    
    async def _master_orchestration_loop(self):
        """Master orchestration control loop"""
        while self.orchestration_active:
            try:
                # Coordinate system operations
                await self._coordinate_system_operations()
                
                # Check for orchestration opportunities
                await self._check_orchestration_opportunities()
                
                # Update orchestration metrics
                await self._update_orchestration_metrics()
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Master orchestration loop error: {e}")
                await asyncio.sleep(60)
    
    async def _system_health_monitoring_loop(self):
        """Monitor health of all integrated systems"""
        while self.orchestration_active:
            try:
                # Check each system's health
                self.system_health = {
                    "optimization_engine": self.optimization_engine is not None,
                    "template_system": self.template_system is not None,
                    "production_integration": (
                        self.production_integration is not None and 
                        self.production_integration.server_status == "running"
                    ),
                    "deployment_system": (
                        self.deployment_system is not None and
                        self.deployment_system.optimization_active
                    ),
                    "meta_learning": self.meta_learner is not None,
                    "memory_system": self.memory_system is not None
                }
                
                # Take corrective action if needed
                await self._handle_system_health_issues()
                
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"System health monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _analytics_collection_loop(self):
        """Collect and aggregate analytics from all systems"""
        while self.orchestration_active:
            try:
                # Collect analytics from all systems
                self.system_analytics = await self.get_system_analytics()
                
                # Store historical analytics
                await self._store_historical_analytics()
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                logger.error(f"Analytics collection error: {e}")
                await asyncio.sleep(300)
    
    async def _learning_integration_loop(self):
        """Integrate learning across all systems"""
        while self.orchestration_active:
            try:
                # Run meta-learning cycle
                meta_results = await self.meta_learner.meta_learning_cycle()
                
                # Apply insights across all systems
                await self._apply_cross_system_learning(meta_results)
                
                await asyncio.sleep(self.config.meta_learning_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Learning integration error: {e}")
                await asyncio.sleep(1800)  # 30 minutes fallback

    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get complete orchestration status"""
        return {
            "orchestration_active": self.orchestration_active,
            "initialization_complete": self.initialization_complete,
            "system_health": self.system_health,
            "active_workflows": len(self.deployment_system.active_deployments) if self.deployment_system else 0,
            "total_templates": len(self.template_system.templates) if self.template_system else 0,
            "server_status": self.production_integration.server_status if self.production_integration else "unknown",
            "optimization_active": self.optimization_engine.monitoring_active if self.optimization_engine else False,
            "meta_learning_active": True,
            "configuration": asdict(self.config)
        }

# Factory function for easy initialization
async def create_comprehensive_orchestrator(config: N8NOrchestrationConfig) -> ComprehensiveN8NOrchestrator:
    """Create and initialize comprehensive n8n orchestrator"""
    orchestrator = ComprehensiveN8NOrchestrator(config)
    await orchestrator.initialize_all_systems()
    return orchestrator

# Convenience function for quick setup
async def quick_start_n8n_orchestration(
    n8n_host: str = "localhost",
    n8n_port: int = 5678,
    optimization_enabled: bool = True
) -> ComprehensiveN8NOrchestrator:
    """Quick start n8n orchestration with default settings"""
    
    config = N8NOrchestrationConfig(
        n8n_server_config=N8NServerConfig(
            host=n8n_host,
            port=n8n_port,
            mcp_mode="http"
        ),
        optimization_enabled=optimization_enabled,
        template_learning_enabled=True,
        auto_scaling_enabled=True,
        self_healing_enabled=True
    )
    
    orchestrator = await create_comprehensive_orchestrator(config)
    return orchestrator

if __name__ == "__main__":
    print("Comprehensive n8n Orchestrator - SynthNet AI")
    print("Master system for intelligent workflow automation with complete AI integration")
    
    # Example usage
    async def example_usage():
        orchestrator = await quick_start_n8n_orchestration()
        await orchestrator.start_orchestration()
    
    # Uncomment to run example
    # asyncio.run(example_usage())