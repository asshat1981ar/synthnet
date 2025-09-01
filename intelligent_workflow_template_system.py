#!/usr/bin/env python3
"""
Intelligent Workflow Template System for SynthNet AI
===================================================

Advanced template system that uses AI learning to create, evolve, and optimize
n8n workflow templates based on usage patterns, success metrics, and meta-learning insights.

Features:
- Self-evolving workflow templates
- Context-aware template selection
- Performance-driven template optimization
- Cross-domain template knowledge transfer
- Adaptive parameter inference
- Intelligent template composition
"""

import asyncio
import json
import logging
import datetime
import uuid
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import statistics

from problem_solving_memory_system import ProblemSolvingMemorySystem, ProblemPattern
from meta_learning_system import MetaLearningSystem
from enhanced_workflow_optimization_engine import EnhancedWorkflowOptimizationEngine, WorkflowMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowTemplate:
    """Intelligent workflow template with learning capabilities"""
    template_id: str
    name: str
    description: str
    category: str  # "android_dev", "data_processing", "ai_training", "monitoring"
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    parameters: Dict[str, Any]
    success_metrics: Dict[str, float]
    usage_count: int = 0
    success_rate: float = 0.0
    performance_score: float = 0.0
    learning_insights: List[str] = field(default_factory=list)
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    version: int = 1
    parent_template_id: Optional[str] = None
    adaptation_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemplateGenerationContext:
    """Context for intelligent template generation"""
    objective: str
    domain: str
    requirements: List[str]
    constraints: Dict[str, Any]
    expected_performance: Dict[str, float]
    user_preferences: Dict[str, Any]
    historical_context: List[str]
    meta_learning_guidance: Dict[str, Any]

@dataclass
class TemplateEvolution:
    """Records template evolution and learning"""
    evolution_id: str
    original_template_id: str
    evolved_template_id: str
    evolution_type: str  # "optimization", "adaptation", "composition", "learning"
    changes_made: List[Dict[str, Any]]
    performance_improvement: float
    learning_source: str
    timestamp: str
    confidence: float

class IntelligentWorkflowTemplateSystem:
    """
    Advanced template system with AI-driven learning and optimization
    """
    
    def __init__(self, memory_system: ProblemSolvingMemorySystem, 
                 meta_learner: MetaLearningSystem,
                 optimization_engine: EnhancedWorkflowOptimizationEngine):
        self.memory_system = memory_system
        self.meta_learner = meta_learner
        self.optimization_engine = optimization_engine
        
        # Template storage and management
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.template_categories: Dict[str, List[str]] = defaultdict(list)
        self.template_evolution_history: Dict[str, List[TemplateEvolution]] = defaultdict(list)
        
        # Learning and optimization
        self.template_performance_tracker: Dict[str, List[WorkflowMetrics]] = defaultdict(list)
        self.adaptation_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.cross_domain_insights: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
        
        # Template intelligence
        self.template_embeddings: Dict[str, List[float]] = {}
        self.similarity_cache: Dict[Tuple[str, str], float] = {}
        self.generation_models: Dict[str, Dict[str, Any]] = {}
        
        # Initialize with base templates
        asyncio.create_task(self._initialize_base_templates())
        
        logger.info("Intelligent Workflow Template System initialized")
    
    async def generate_intelligent_template(self, context: TemplateGenerationContext) -> WorkflowTemplate:
        """Generate intelligent workflow template based on context and learning"""
        
        logger.info(f"Generating intelligent template for: {context.objective}")
        
        # Apply meta-learning to template generation
        meta_guidance = await self.meta_learner.apply_meta_learning_to_problem(
            f"Generate workflow template for: {context.objective}",
            asdict(context)
        )
        
        # Find similar existing templates for inspiration
        similar_templates = await self._find_similar_templates(context)
        
        # Generate base template structure
        base_template = await self._generate_base_template(context, meta_guidance)
        
        # Apply learned optimizations from similar templates
        optimized_template = await self._apply_learned_optimizations(
            base_template, similar_templates, context
        )
        
        # Add adaptive intelligence
        intelligent_template = await self._add_adaptive_intelligence(
            optimized_template, context, meta_guidance
        )
        
        # Store and index template
        await self._store_template(intelligent_template)
        
        # Record template generation pattern
        await self._record_template_generation_pattern(context, intelligent_template)
        
        logger.info(f"Generated intelligent template: {intelligent_template.template_id}")
        return intelligent_template
    
    async def evolve_template(self, template_id: str, 
                            performance_data: List[WorkflowMetrics]) -> Optional[WorkflowTemplate]:
        """Evolve template based on performance data and learning"""
        
        if template_id not in self.templates:
            return None
        
        original_template = self.templates[template_id]
        
        # Analyze performance patterns
        performance_analysis = await self._analyze_template_performance(
            template_id, performance_data
        )
        
        # Identify evolution opportunities
        evolution_opportunities = await self._identify_evolution_opportunities(
            original_template, performance_analysis
        )
        
        if not evolution_opportunities:
            return original_template
        
        # Apply meta-learning to guide evolution
        evolution_guidance = await self.meta_learner.apply_meta_learning_to_problem(
            f"Evolve template {template_id} based on performance",
            {
                "template": asdict(original_template),
                "performance_analysis": performance_analysis,
                "evolution_opportunities": evolution_opportunities
            }
        )
        
        # Generate evolved template
        evolved_template = await self._generate_evolved_template(
            original_template, evolution_opportunities, evolution_guidance
        )
        
        # Validate evolution improvement
        if evolved_template and await self._validate_evolution_improvement(
            original_template, evolved_template
        ):
            # Store evolved template
            await self._store_template(evolved_template)
            
            # Record evolution
            await self._record_template_evolution(original_template, evolved_template)
            
            logger.info(f"Evolved template {template_id} to {evolved_template.template_id}")
            return evolved_template
        
        return original_template
    
    async def intelligent_template_composition(self, 
                                             objective: str,
                                             component_requirements: List[str]) -> WorkflowTemplate:
        """Compose intelligent template from multiple existing templates"""
        
        # Find templates for each component requirement
        component_templates = {}
        for requirement in component_requirements:
            templates = await self._find_templates_for_requirement(requirement)
            if templates:
                component_templates[requirement] = templates[0]  # Best match
        
        # Apply meta-learning to composition strategy
        composition_guidance = await self.meta_learner.apply_meta_learning_to_problem(
            f"Compose workflow template for: {objective}",
            {
                "objective": objective,
                "component_requirements": component_requirements,
                "available_components": list(component_templates.keys())
            }
        )
        
        # Generate composition plan
        composition_plan = await self._generate_composition_plan(
            component_templates, composition_guidance
        )
        
        # Execute composition
        composed_template = await self._execute_template_composition(
            composition_plan, objective
        )
        
        # Optimize composed template
        optimized_composition = await self._optimize_composed_template(
            composed_template, composition_guidance
        )
        
        await self._store_template(optimized_composition)
        
        logger.info(f"Composed intelligent template: {optimized_composition.template_id}")
        return optimized_composition
    
    async def adaptive_template_selection(self, context: TemplateGenerationContext) -> WorkflowTemplate:
        """Select and adapt best template for given context"""
        
        # Find candidate templates
        candidates = await self._find_candidate_templates(context)
        
        if not candidates:
            # Generate new template if no candidates
            return await self.generate_intelligent_template(context)
        
        # Score candidates based on context fit
        scored_candidates = []
        for template in candidates:
            score = await self._calculate_template_context_score(template, context)
            scored_candidates.append((template, score))
        
        # Select best candidate
        best_template, best_score = max(scored_candidates, key=lambda x: x[1])
        
        # Adapt template to context if needed
        if best_score < 0.8:  # Adaptation threshold
            adapted_template = await self._adapt_template_to_context(best_template, context)
            return adapted_template
        
        return best_template
    
    async def cross_domain_knowledge_transfer(self, source_domain: str, 
                                            target_domain: str) -> List[Dict[str, Any]]:
        """Transfer knowledge between template domains"""
        
        # Get high-performing templates from source domain
        source_templates = await self._get_high_performing_templates(source_domain)
        
        # Identify transferable patterns
        transferable_patterns = []
        for template in source_templates:
            patterns = await self._extract_transferable_patterns(template, target_domain)
            transferable_patterns.extend(patterns)
        
        # Apply meta-learning to guide transfer
        transfer_guidance = await self.meta_learner.apply_meta_learning_to_problem(
            f"Transfer knowledge from {source_domain} to {target_domain}",
            {
                "source_domain": source_domain,
                "target_domain": target_domain,
                "transferable_patterns": transferable_patterns
            }
        )
        
        # Generate transfer insights
        transfer_insights = await self._generate_transfer_insights(
            source_domain, target_domain, transferable_patterns, transfer_guidance
        )
        
        # Store cross-domain insights
        self.cross_domain_insights[(source_domain, target_domain)].extend(transfer_insights)
        
        logger.info(f"Transferred {len(transfer_insights)} insights from {source_domain} to {target_domain}")
        return transfer_insights
    
    async def predict_template_performance(self, template: WorkflowTemplate, 
                                         context: Dict[str, Any]) -> Dict[str, float]:
        """Predict template performance in given context"""
        
        # Get historical performance data for similar contexts
        similar_contexts = await self._find_similar_contexts(context)
        historical_performance = []
        
        for similar_context in similar_contexts:
            if template.template_id in self.template_performance_tracker:
                for metrics in self.template_performance_tracker[template.template_id]:
                    if self._context_similarity(metrics.context, similar_context) > 0.7:
                        historical_performance.append({
                            'success_rate': metrics.success_rate,
                            'throughput': metrics.throughput,
                            'execution_time': metrics.execution_time
                        })
        
        if not historical_performance:
            # Use template's base performance metrics
            return {
                'predicted_success_rate': template.success_rate,
                'predicted_throughput': 1.0,
                'predicted_execution_time': 60.0,
                'confidence': 0.3
            }
        
        # Calculate predicted performance
        predicted_success_rate = statistics.mean([p['success_rate'] for p in historical_performance])
        predicted_throughput = statistics.mean([p['throughput'] for p in historical_performance])
        predicted_execution_time = statistics.mean([p['execution_time'] for p in historical_performance])
        
        # Apply meta-learning adjustments
        meta_adjustments = await self._apply_meta_learning_to_prediction(
            template, context, historical_performance
        )
        
        return {
            'predicted_success_rate': predicted_success_rate * meta_adjustments.get('success_rate_multiplier', 1.0),
            'predicted_throughput': predicted_throughput * meta_adjustments.get('throughput_multiplier', 1.0),
            'predicted_execution_time': predicted_execution_time * meta_adjustments.get('execution_time_multiplier', 1.0),
            'confidence': min(len(historical_performance) / 10.0, 1.0)
        }
    
    # Helper methods for template intelligence
    
    async def _initialize_base_templates(self):
        """Initialize system with base workflow templates"""
        
        # Android Development Templates
        android_ci_template = WorkflowTemplate(
            template_id=str(uuid.uuid4()),
            name="Android CI/CD Pipeline",
            description="Comprehensive Android continuous integration and deployment",
            category="android_dev",
            nodes=[
                {
                    "id": "git_trigger",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"httpMethod": "POST", "path": "android-ci"}
                },
                {
                    "id": "build_gradle",
                    "type": "n8n-nodes-base.executeCommand",
                    "parameters": {"command": "./gradlew assembleDebug testDebugUnitTest"}
                },
                {
                    "id": "run_tests",
                    "type": "n8n-nodes-base.executeCommand", 
                    "parameters": {"command": "./gradlew connectedAndroidTest"}
                },
                {
                    "id": "static_analysis",
                    "type": "n8n-nodes-base.executeCommand",
                    "parameters": {"command": "./gradlew lintDebug detekt"}
                },
                {
                    "id": "deploy_artifacts",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "POST", "url": "https://api.github.com/releases"}
                }
            ],
            connections={
                "git_trigger": {"main": [["build_gradle"]]},
                "build_gradle": {"main": [["run_tests", "static_analysis"]]},
                "run_tests": {"main": [["deploy_artifacts"]]},
                "static_analysis": {"main": [["deploy_artifacts"]]}
            },
            parameters={
                "build_timeout": 1800,
                "test_timeout": 3600,
                "parallel_execution": True
            },
            success_metrics={
                "build_success_rate": 0.95,
                "test_coverage": 0.80,
                "deployment_success": 0.90
            }
        )
        
        await self._store_template(android_ci_template)
        
        # AI Training Pipeline Template
        ai_training_template = WorkflowTemplate(
            template_id=str(uuid.uuid4()),
            name="AI Model Training Pipeline",
            description="Automated machine learning model training and evaluation",
            category="ai_training", 
            nodes=[
                {
                    "id": "data_ingestion",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "GET", "url": "{{$parameter[\"data_source_url\"]}}"}
                },
                {
                    "id": "data_preprocessing",
                    "type": "n8n-nodes-base.code",
                    "parameters": {"jsCode": "// Data preprocessing logic"}
                },
                {
                    "id": "model_training",
                    "type": "n8n-nodes-base.executeCommand",
                    "parameters": {"command": "python train_model.py --config {{$parameter[\"training_config\"]}}"}
                },
                {
                    "id": "model_evaluation", 
                    "type": "n8n-nodes-base.executeCommand",
                    "parameters": {"command": "python evaluate_model.py --model {{$parameter[\"model_path\"]}}"}
                },
                {
                    "id": "model_deployment",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "POST", "url": "{{$parameter[\"deployment_endpoint\"]}}"}
                }
            ],
            connections={
                "data_ingestion": {"main": [["data_preprocessing"]]},
                "data_preprocessing": {"main": [["model_training"]]}, 
                "model_training": {"main": [["model_evaluation"]]},
                "model_evaluation": {"main": [["model_deployment"]]}
            },
            parameters={
                "training_epochs": 100,
                "batch_size": 32,
                "learning_rate": 0.001,
                "validation_split": 0.2
            },
            success_metrics={
                "training_accuracy": 0.90,
                "validation_accuracy": 0.85,
                "deployment_success": 0.95
            }
        )
        
        await self._store_template(ai_training_template)
        
        # Data Processing Template
        data_processing_template = WorkflowTemplate(
            template_id=str(uuid.uuid4()),
            name="Real-time Data Processing Pipeline",
            description="High-throughput data processing and analysis",
            category="data_processing",
            nodes=[
                {
                    "id": "data_stream",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"httpMethod": "POST", "path": "data-stream"}
                },
                {
                    "id": "data_validation",
                    "type": "n8n-nodes-base.code",
                    "parameters": {"jsCode": "// Data validation logic"}
                },
                {
                    "id": "data_transformation",
                    "type": "n8n-nodes-base.code", 
                    "parameters": {"jsCode": "// Data transformation logic"}
                },
                {
                    "id": "data_enrichment",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "GET", "url": "{{$parameter[\"enrichment_api\"]}}"}
                },
                {
                    "id": "data_storage",
                    "type": "n8n-nodes-base.postgres",
                    "parameters": {"operation": "insert"}
                }
            ],
            connections={
                "data_stream": {"main": [["data_validation"]]},
                "data_validation": {"main": [["data_transformation"]]},
                "data_transformation": {"main": [["data_enrichment"]]},
                "data_enrichment": {"main": [["data_storage"]]}
            },
            parameters={
                "batch_size": 1000,
                "processing_timeout": 300,
                "retry_attempts": 3
            },
            success_metrics={
                "processing_throughput": 1000.0,
                "data_quality_score": 0.95,
                "storage_success_rate": 0.99
            }
        )
        
        await self._store_template(data_processing_template)
        
        logger.info("Initialized base workflow templates")
    
    async def _store_template(self, template: WorkflowTemplate):
        """Store template and update indices"""
        self.templates[template.template_id] = template
        self.template_categories[template.category].append(template.template_id)
        
        # Update template embedding for similarity search
        await self._update_template_embedding(template)
    
    async def _update_template_embedding(self, template: WorkflowTemplate):
        """Update template embedding for semantic similarity"""
        # Simple embedding based on template characteristics
        # In production, this would use a proper embedding model
        embedding_features = []
        
        # Node type features
        node_types = [node.get('type', '') for node in template.nodes]
        embedding_features.extend([hash(nt) % 1000 / 1000.0 for nt in node_types])
        
        # Performance features
        embedding_features.extend([
            template.success_rate,
            template.performance_score,
            len(template.nodes),
            template.usage_count / 100.0  # Normalized usage
        ])
        
        # Pad or truncate to fixed size
        target_size = 50
        if len(embedding_features) < target_size:
            embedding_features.extend([0.0] * (target_size - len(embedding_features)))
        else:
            embedding_features = embedding_features[:target_size]
        
        self.template_embeddings[template.template_id] = embedding_features
    
    async def _find_similar_templates(self, context: TemplateGenerationContext) -> List[WorkflowTemplate]:
        """Find templates similar to generation context"""
        similar_templates = []
        
        # Get templates from same category
        category_templates = self.template_categories.get(context.domain, [])
        
        for template_id in category_templates:
            if template_id in self.templates:
                template = self.templates[template_id]
                
                # Calculate similarity score
                similarity = await self._calculate_context_template_similarity(context, template)
                
                if similarity > 0.5:  # Similarity threshold
                    similar_templates.append((template, similarity))
        
        # Sort by similarity and return top templates
        similar_templates.sort(key=lambda x: x[1], reverse=True)
        return [template for template, _ in similar_templates[:5]]
    
    async def _calculate_context_template_similarity(self, 
                                                   context: TemplateGenerationContext, 
                                                   template: WorkflowTemplate) -> float:
        """Calculate similarity between context and template"""
        similarity_score = 0.0
        
        # Domain similarity
        if template.category == context.domain:
            similarity_score += 0.4
        
        # Objective similarity (simplified text matching)
        objective_words = set(context.objective.lower().split())
        template_words = set((template.name + " " + template.description).lower().split())
        word_overlap = len(objective_words.intersection(template_words))
        word_total = len(objective_words.union(template_words))
        if word_total > 0:
            similarity_score += 0.3 * (word_overlap / word_total)
        
        # Requirements similarity
        requirements_matched = 0
        for requirement in context.requirements:
            if any(requirement.lower() in node.get('type', '').lower() for node in template.nodes):
                requirements_matched += 1
        if context.requirements:
            similarity_score += 0.3 * (requirements_matched / len(context.requirements))
        
        return similarity_score

    async def get_template_performance_report(self, template_id: str) -> Dict[str, Any]:
        """Generate comprehensive template performance report"""
        if template_id not in self.templates:
            return {"error": "Template not found"}
        
        template = self.templates[template_id]
        performance_metrics = self.template_performance_tracker.get(template_id, [])
        
        if not performance_metrics:
            return {
                "template_id": template_id,
                "template_name": template.name,
                "usage_count": template.usage_count,
                "base_success_rate": template.success_rate,
                "performance_score": template.performance_score,
                "status": "No execution data available"
            }
        
        # Calculate performance statistics
        recent_metrics = performance_metrics[-10:] if len(performance_metrics) >= 10 else performance_metrics
        
        avg_success_rate = statistics.mean([m.success_rate for m in recent_metrics])
        avg_throughput = statistics.mean([m.throughput for m in recent_metrics])
        avg_execution_time = statistics.mean([m.execution_time for m in recent_metrics])
        
        # Calculate performance trends
        if len(performance_metrics) > 5:
            early_metrics = performance_metrics[:5]
            late_metrics = performance_metrics[-5:]
            
            success_trend = statistics.mean([m.success_rate for m in late_metrics]) - \
                           statistics.mean([m.success_rate for m in early_metrics])
            throughput_trend = statistics.mean([m.throughput for m in late_metrics]) - \
                              statistics.mean([m.throughput for m in early_metrics])
        else:
            success_trend = throughput_trend = 0.0
        
        # Evolution history
        evolutions = self.template_evolution_history.get(template_id, [])
        total_improvement = sum([e.performance_improvement for e in evolutions])
        
        return {
            "template_id": template_id,
            "template_name": template.name,
            "category": template.category,
            "version": template.version,
            "performance_summary": {
                "usage_count": template.usage_count,
                "total_executions": len(performance_metrics),
                "average_success_rate": avg_success_rate,
                "average_throughput": avg_throughput,
                "average_execution_time": avg_execution_time,
                "success_rate_trend": success_trend,
                "throughput_trend": throughput_trend
            },
            "evolution_summary": {
                "total_evolutions": len(evolutions),
                "total_performance_improvement": total_improvement,
                "latest_evolution": evolutions[-1].timestamp if evolutions else None
            },
            "learning_insights": template.learning_insights,
            "recommendations": await self._generate_template_recommendations(template_id)
        }
    
    async def _generate_template_recommendations(self, template_id: str) -> List[str]:
        """Generate recommendations for template improvement"""
        template = self.templates[template_id]
        recommendations = []
        
        # Performance-based recommendations
        if template.success_rate < 0.8:
            recommendations.append("Consider optimizing node configurations to improve success rate")
        
        if template.usage_count > 50 and len(self.template_evolution_history.get(template_id, [])) == 0:
            recommendations.append("Template has high usage but no evolutions - consider performance analysis")
        
        # Learning-based recommendations
        if len(template.learning_insights) < 3:
            recommendations.append("Gather more execution data to enable better learning insights")
        
        return recommendations

# Export the template system for integration
async def create_template_system(memory_system: ProblemSolvingMemorySystem,
                                meta_learner: MetaLearningSystem,
                                optimization_engine: EnhancedWorkflowOptimizationEngine) -> IntelligentWorkflowTemplateSystem:
    """Factory function to create and initialize template system"""
    template_system = IntelligentWorkflowTemplateSystem(memory_system, meta_learner, optimization_engine)
    return template_system

if __name__ == "__main__":
    print("Intelligent Workflow Template System - SynthNet AI Integration")
    print("Provides AI-driven workflow template generation and optimization")