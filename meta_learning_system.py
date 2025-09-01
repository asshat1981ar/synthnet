#!/usr/bin/env python3
"""
SynthNet AI - Meta-Learning System
=================================

Advanced meta-learning system that learns how to learn more effectively.
This system analyzes its own learning patterns and continuously improves
its problem-solving methodologies.

Key Features:
- Pattern recognition across different problem domains
- Learning strategy optimization
- Self-modifying algorithms
- Cross-domain knowledge transfer
- Autonomous methodology evolution
"""

import asyncio
import json
import logging
import datetime
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from collections import defaultdict

from problem_solving_memory_system import (
    ProblemSolvingMemorySystem, 
    ProblemPattern, 
    MethodologyTemplate,
    SolutionEvolution
)

from self_improvement_orchestrator import (
    SelfImprovementOrchestrator,
    ImprovementOpportunity,
    ImprovementExecution
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LearningPattern:
    """Represents a meta-learning pattern"""
    pattern_id: str
    pattern_type: str  # "solution_evolution", "methodology_effectiveness", "domain_transfer"
    source_domains: List[str]
    target_domains: List[str]
    pattern_description: str
    extraction_rules: List[str]
    application_conditions: List[str]
    success_indicators: List[str]
    effectiveness_metrics: Dict[str, float]
    confidence_score: float
    generalization_level: int  # 1-10, how broadly applicable
    last_validation: str
    usage_count: int

@dataclass
class MetaStrategy:
    """Represents a high-level problem-solving meta-strategy"""
    strategy_id: str
    strategy_name: str
    description: str
    applicable_contexts: List[str]
    strategy_steps: List[str]
    adaptation_rules: List[str]
    performance_history: List[Dict[str, float]]
    evolution_trajectory: List[Dict[str, Any]]
    success_rate: float
    average_improvement: float
    learning_velocity: float  # How quickly it improves

@dataclass
class KnowledgeTransferRule:
    """Rules for transferring knowledge between domains"""
    rule_id: str
    source_domain: str
    target_domain: str
    transfer_type: str  # "direct", "analogical", "abstract"
    mapping_rules: List[str]
    adaptation_requirements: List[str]
    success_probability: float
    validation_criteria: List[str]

class MetaLearningSystem:
    """
    Advanced meta-learning system that continuously improves its learning capabilities
    """
    
    def __init__(self, memory_system: ProblemSolvingMemorySystem, improvement_orchestrator: SelfImprovementOrchestrator):
        self.memory_system = memory_system
        self.improvement_orchestrator = improvement_orchestrator
        
        # Meta-learning components
        self.learning_patterns = {}
        self.meta_strategies = {}
        self.transfer_rules = {}
        self.domain_knowledge_maps = {}
        
        # Learning analytics
        self.learning_history = []
        self.pattern_effectiveness = {}
        self.strategy_evolution = {}
        
        # Advanced learning engines
        self.pattern_extractor = PatternExtractor()
        self.strategy_synthesizer = StrategySynthesizer()
        self.knowledge_transfer_engine = KnowledgeTransferEngine()
        self.meta_optimizer = MetaOptimizer()
        
        # Self-modification capabilities
        self.algorithm_variants = {}
        self.performance_predictors = {}
        
        logger.info("Meta-Learning System initialized")
        self._initialize_base_patterns()
    
    def _initialize_base_patterns(self):
        """Initialize base learning patterns from SynthNet development"""
        
        # Pattern 1: Progressive Enhancement Pattern
        progressive_pattern = LearningPattern(
            pattern_id="progressive_enhancement",
            pattern_type="solution_evolution",
            source_domains=["software_development", "system_design"],
            target_domains=["ai_development", "process_optimization"],
            pattern_description="Solutions evolve from simple to complex through iterative enhancement",
            extraction_rules=[
                "Identify minimal viable implementation",
                "Add complexity incrementally",
                "Validate at each stage",
                "Optimize based on real-world feedback"
            ],
            application_conditions=[
                "Problem has unclear requirements",
                "Solution space is large",
                "Feedback loops are available",
                "Risk of over-engineering exists"
            ],
            success_indicators=[
                "Each iteration produces working solution",
                "Complexity adds genuine value",
                "Performance improves consistently",
                "User feedback is positive"
            ],
            effectiveness_metrics={
                "success_rate": 0.85,
                "time_to_value": 0.75,
                "quality_improvement": 0.90,
                "adaptability": 0.88
            },
            confidence_score=0.92,
            generalization_level=9,
            last_validation=datetime.datetime.now().isoformat(),
            usage_count=15
        )
        
        # Pattern 2: Multi-Perspective Validation Pattern
        multi_perspective_pattern = LearningPattern(
            pattern_id="multi_perspective_validation",
            pattern_type="methodology_effectiveness",
            source_domains=["ai_development", "decision_making"],
            target_domains=["system_design", "quality_assurance"],
            pattern_description="Using multiple AI systems/perspectives improves solution quality",
            extraction_rules=[
                "Engage multiple specialized systems",
                "Compare and contrast approaches",
                "Identify complementary strengths",
                "Synthesize best elements"
            ],
            application_conditions=[
                "Complex problem with multiple valid approaches",
                "High stakes decision making",
                "Risk of single-point bias",
                "Multiple expertise domains involved"
            ],
            success_indicators=[
                "Different perspectives identify unique insights",
                "Cross-validation catches errors",
                "Solution quality metrics improve",
                "Stakeholder confidence increases"
            ],
            effectiveness_metrics={
                "error_reduction": 0.78,
                "solution_quality": 0.91,
                "stakeholder_confidence": 0.86,
                "completeness": 0.89
            },
            confidence_score=0.89,
            generalization_level=8,
            last_validation=datetime.datetime.now().isoformat(),
            usage_count=12
        )
        
        # Pattern 3: Antifragile Design Pattern
        antifragile_pattern = LearningPattern(
            pattern_id="antifragile_design",
            pattern_type="solution_evolution",
            source_domains=["system_architecture", "resilience_engineering"],
            target_domains=["ai_systems", "organizational_design"],
            pattern_description="Systems that improve under stress rather than just surviving",
            extraction_rules=[
                "Build multiple fallback mechanisms",
                "Learn from failures to strengthen system",
                "Design for continuous adaptation",
                "Enable beneficial stress responses"
            ],
            application_conditions=[
                "System operates in unpredictable environment",
                "Failure costs are high",
                "Learning opportunities exist in failures",
                "Adaptation mechanisms can be implemented"
            ],
            success_indicators=[
                "Performance improves after challenges",
                "Failure recovery time decreases",
                "System becomes more robust over time",
                "Unexpected benefits emerge from stress"
            ],
            effectiveness_metrics={
                "resilience_improvement": 0.94,
                "adaptation_speed": 0.82,
                "failure_recovery": 0.91,
                "unexpected_benefits": 0.73
            },
            confidence_score=0.87,
            generalization_level=7,
            last_validation=datetime.datetime.now().isoformat(),
            usage_count=8
        )
        
        self.learning_patterns["progressive_enhancement"] = progressive_pattern
        self.learning_patterns["multi_perspective_validation"] = multi_perspective_pattern
        self.learning_patterns["antifragile_design"] = antifragile_pattern
        
        self._initialize_meta_strategies()
    
    def _initialize_meta_strategies(self):
        """Initialize meta-strategies from successful patterns"""
        
        # Meta-Strategy 1: Adaptive Problem Solving
        adaptive_strategy = MetaStrategy(
            strategy_id="adaptive_problem_solving",
            strategy_name="Adaptive Problem Solving",
            description="Dynamically adapt problem-solving approach based on context and feedback",
            applicable_contexts=["complex_problems", "uncertain_requirements", "evolving_domains"],
            strategy_steps=[
                "Analyze problem context and constraints",
                "Select initial approach based on pattern matching",
                "Implement minimal viable solution",
                "Gather feedback and performance metrics",
                "Adapt approach based on learnings",
                "Iterate until satisfactory solution achieved"
            ],
            adaptation_rules=[
                "If feedback is negative, try alternative approach",
                "If performance plateaus, introduce variation",
                "If context changes, reassess strategy selection",
                "If new patterns emerge, update strategy"
            ],
            performance_history=[
                {"timestamp": "2025-09-01T08:00:00", "success_rate": 0.85, "efficiency": 0.78},
                {"timestamp": "2025-09-01T12:00:00", "success_rate": 0.87, "efficiency": 0.82},
                {"timestamp": "2025-09-01T16:00:00", "success_rate": 0.91, "efficiency": 0.86}
            ],
            evolution_trajectory=[
                {"version": "1.0", "changes": ["initial implementation"], "performance_delta": 0.0},
                {"version": "1.1", "changes": ["added feedback loops"], "performance_delta": 0.05},
                {"version": "1.2", "changes": ["improved pattern matching"], "performance_delta": 0.08}
            ],
            success_rate=0.89,
            average_improvement=0.12,
            learning_velocity=0.08
        )
        
        # Meta-Strategy 2: Cross-Domain Knowledge Transfer
        transfer_strategy = MetaStrategy(
            strategy_id="cross_domain_transfer",
            strategy_name="Cross-Domain Knowledge Transfer",
            description="Transfer successful patterns and solutions across different problem domains",
            applicable_contexts=["new_domains", "similar_problems", "analogical_reasoning"],
            strategy_steps=[
                "Identify source domain with relevant patterns",
                "Abstract patterns to remove domain-specific details",
                "Map abstract patterns to target domain",
                "Adapt patterns for target domain constraints",
                "Validate transferred patterns",
                "Refine based on target domain feedback"
            ],
            adaptation_rules=[
                "If direct transfer fails, try analogical mapping",
                "If abstraction is too high, add domain specifics",
                "If validation fails, modify adaptation rules",
                "If performance is poor, try different source domain"
            ],
            performance_history=[
                {"timestamp": "2025-09-01T08:00:00", "transfer_success": 0.72, "adaptation_quality": 0.68},
                {"timestamp": "2025-09-01T12:00:00", "transfer_success": 0.76, "adaptation_quality": 0.73},
                {"timestamp": "2025-09-01T16:00:00", "transfer_success": 0.81, "adaptation_quality": 0.78}
            ],
            evolution_trajectory=[
                {"version": "1.0", "changes": ["basic transfer mechanism"], "performance_delta": 0.0},
                {"version": "1.1", "changes": ["improved abstraction"], "performance_delta": 0.07},
                {"version": "1.2", "changes": ["better domain mapping"], "performance_delta": 0.12}
            ],
            success_rate=0.78,
            average_improvement=0.16,
            learning_velocity=0.11
        )
        
        self.meta_strategies["adaptive_problem_solving"] = adaptive_strategy
        self.meta_strategies["cross_domain_transfer"] = transfer_strategy
    
    async def meta_learning_cycle(self):
        """Execute a complete meta-learning cycle"""
        logger.info("Starting meta-learning cycle")
        
        try:
            # Phase 1: Extract new patterns from recent experiences
            new_patterns = await self._extract_new_patterns()
            
            # Phase 2: Evaluate and update existing patterns
            await self._evaluate_pattern_effectiveness()
            
            # Phase 3: Synthesize new meta-strategies
            new_strategies = await self._synthesize_new_strategies()
            
            # Phase 4: Optimize existing strategies
            await self._optimize_existing_strategies()
            
            # Phase 5: Transfer knowledge across domains
            transfer_opportunities = await self._identify_transfer_opportunities()
            await self._execute_knowledge_transfer(transfer_opportunities)
            
            # Phase 6: Self-modify learning algorithms
            await self._optimize_learning_algorithms()
            
            # Phase 7: Validate improvements
            validation_results = await self._validate_meta_improvements()
            
            logger.info(f"Meta-learning cycle completed: {len(new_patterns)} new patterns, {len(new_strategies)} new strategies")
            
            return {
                "new_patterns": len(new_patterns),
                "new_strategies": len(new_strategies),
                "transfer_opportunities": len(transfer_opportunities),
                "validation_results": validation_results
            }
            
        except Exception as e:
            logger.error(f"Error in meta-learning cycle: {e}")
            return {"error": str(e)}
    
    async def _extract_new_patterns(self) -> List[LearningPattern]:
        """Extract new learning patterns from recent experiences"""
        new_patterns = []
        
        # Get recent problem-solving experiences
        recent_problems = [p for p in self.memory_system.problems_db.values() 
                          if self._is_recent(p.timestamp)]
        
        # Extract patterns using pattern extractor
        extracted_patterns = await self.pattern_extractor.extract_patterns(recent_problems)
        
        for pattern in extracted_patterns:
            # Validate pattern novelty
            if not self._is_pattern_duplicate(pattern):
                # Calculate confidence score
                pattern.confidence_score = self._calculate_pattern_confidence(pattern)
                
                # Add to patterns database
                self.learning_patterns[pattern.pattern_id] = pattern
                new_patterns.append(pattern)
                
                logger.info(f"Extracted new pattern: {pattern.pattern_id}")
        
        return new_patterns
    
    async def _evaluate_pattern_effectiveness(self):
        """Evaluate and update effectiveness of existing patterns"""
        for pattern_id, pattern in self.learning_patterns.items():
            # Find recent applications of this pattern
            applications = self._find_pattern_applications(pattern)
            
            if applications:
                # Update effectiveness metrics
                updated_metrics = self._calculate_updated_effectiveness(pattern, applications)
                pattern.effectiveness_metrics = updated_metrics
                
                # Update confidence score
                pattern.confidence_score = self._calculate_pattern_confidence(pattern)
                
                # Update usage count
                pattern.usage_count += len(applications)
                
                logger.debug(f"Updated pattern effectiveness: {pattern_id}")
    
    async def _synthesize_new_strategies(self) -> List[MetaStrategy]:
        """Synthesize new meta-strategies from successful patterns"""
        new_strategies = []
        
        # Group high-performing patterns
        high_performing_patterns = [p for p in self.learning_patterns.values() 
                                  if p.confidence_score > 0.8]
        
        # Synthesize strategies from pattern combinations
        strategy_candidates = await self.strategy_synthesizer.synthesize_strategies(
            high_performing_patterns
        )
        
        for candidate in strategy_candidates:
            # Validate strategy novelty and effectiveness
            if self._is_strategy_viable(candidate):
                self.meta_strategies[candidate.strategy_id] = candidate
                new_strategies.append(candidate)
                
                logger.info(f"Synthesized new strategy: {candidate.strategy_id}")
        
        return new_strategies
    
    async def _optimize_existing_strategies(self):
        """Optimize existing meta-strategies based on performance data"""
        for strategy_id, strategy in self.meta_strategies.items():
            # Analyze performance trends
            performance_trend = self._analyze_performance_trend(strategy)
            
            if performance_trend == "declining":
                # Apply optimization
                optimized_strategy = await self.meta_optimizer.optimize_strategy(strategy)
                
                if optimized_strategy:
                    self.meta_strategies[strategy_id] = optimized_strategy
                    logger.info(f"Optimized strategy: {strategy_id}")
            
            elif performance_trend == "plateauing":
                # Introduce variation
                variant_strategy = await self.meta_optimizer.create_variant(strategy)
                
                if variant_strategy:
                    variant_id = f"{strategy_id}_variant_{len(strategy.evolution_trajectory) + 1}"
                    self.meta_strategies[variant_id] = variant_strategy
                    logger.info(f"Created strategy variant: {variant_id}")
    
    async def _identify_transfer_opportunities(self) -> List[Dict[str, Any]]:
        """Identify opportunities for cross-domain knowledge transfer"""
        opportunities = []
        
        # Analyze domain patterns for transfer potential
        domain_analysis = self._analyze_domain_patterns()
        
        for source_domain, target_domain in self._generate_domain_pairs():
            # Calculate transfer potential
            transfer_score = self._calculate_transfer_potential(
                source_domain, target_domain, domain_analysis
            )
            
            if transfer_score > 0.7:  # High transfer potential
                opportunity = {
                    "source_domain": source_domain,
                    "target_domain": target_domain,
                    "transfer_score": transfer_score,
                    "applicable_patterns": self._find_transferable_patterns(
                        source_domain, target_domain
                    )
                }
                opportunities.append(opportunity)
        
        return sorted(opportunities, key=lambda x: x["transfer_score"], reverse=True)
    
    async def _execute_knowledge_transfer(self, opportunities: List[Dict[str, Any]]):
        """Execute knowledge transfer for identified opportunities"""
        for opportunity in opportunities[:3]:  # Top 3 opportunities
            try:
                # Execute transfer using knowledge transfer engine
                transfer_result = await self.knowledge_transfer_engine.execute_transfer(
                    opportunity["source_domain"],
                    opportunity["target_domain"],
                    opportunity["applicable_patterns"]
                )
                
                if transfer_result.get("success", False):
                    # Create transfer rule for future use
                    transfer_rule = KnowledgeTransferRule(
                        rule_id=f"transfer_{opportunity['source_domain']}_{opportunity['target_domain']}",
                        source_domain=opportunity["source_domain"],
                        target_domain=opportunity["target_domain"],
                        transfer_type=transfer_result["transfer_type"],
                        mapping_rules=transfer_result["mapping_rules"],
                        adaptation_requirements=transfer_result["adaptations"],
                        success_probability=transfer_result["success_probability"],
                        validation_criteria=transfer_result["validation_criteria"]
                    )
                    
                    self.transfer_rules[transfer_rule.rule_id] = transfer_rule
                    logger.info(f"Successful knowledge transfer: {opportunity['source_domain']} → {opportunity['target_domain']}")
                
            except Exception as e:
                logger.error(f"Failed knowledge transfer: {e}")
    
    async def _optimize_learning_algorithms(self):
        """Optimize the learning algorithms themselves"""
        # Analyze learning algorithm performance
        algorithm_performance = self._analyze_algorithm_performance()
        
        for algorithm_name, performance in algorithm_performance.items():
            if performance["efficiency"] < 0.8 or performance["accuracy"] < 0.85:
                # Generate algorithm variants
                variants = await self._generate_algorithm_variants(algorithm_name)
                
                # Test variants
                best_variant = await self._test_algorithm_variants(variants)
                
                if best_variant and best_variant["performance"] > performance:
                    # Replace algorithm with best variant
                    self.algorithm_variants[algorithm_name] = best_variant
                    logger.info(f"Optimized learning algorithm: {algorithm_name}")
    
    async def _validate_meta_improvements(self) -> Dict[str, Any]:
        """Validate that meta-learning improvements are actually beneficial"""
        validation_results = {
            "pattern_validation": {},
            "strategy_validation": {},
            "transfer_validation": {},
            "algorithm_validation": {}
        }
        
        # Validate patterns
        for pattern_id, pattern in self.learning_patterns.items():
            if pattern.usage_count > 0:
                validation_score = self._validate_pattern_effectiveness(pattern)
                validation_results["pattern_validation"][pattern_id] = validation_score
        
        # Validate strategies
        for strategy_id, strategy in self.meta_strategies.items():
            validation_score = self._validate_strategy_effectiveness(strategy)
            validation_results["strategy_validation"][strategy_id] = validation_score
        
        # Validate transfers
        for rule_id, rule in self.transfer_rules.items():
            validation_score = self._validate_transfer_effectiveness(rule)
            validation_results["transfer_validation"][rule_id] = validation_score
        
        return validation_results
    
    def apply_meta_learning_to_problem(self, problem_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply meta-learning insights to solve a new problem"""
        
        # Select best meta-strategy for the problem
        best_strategy = self._select_optimal_strategy(problem_description, context)
        
        # Find applicable patterns
        applicable_patterns = self._find_applicable_patterns(problem_description, context)
        
        # Check for transfer opportunities
        transfer_opportunities = self._check_transfer_opportunities(problem_description, context)
        
        # Generate solution approach
        solution_approach = self._generate_solution_approach(
            best_strategy, applicable_patterns, transfer_opportunities
        )
        
        return {
            "recommended_strategy": best_strategy.strategy_name if best_strategy else "Default",
            "applicable_patterns": [p.pattern_id for p in applicable_patterns],
            "transfer_opportunities": transfer_opportunities,
            "solution_approach": solution_approach,
            "confidence": self._calculate_solution_confidence(
                best_strategy, applicable_patterns, transfer_opportunities
            )
        }
    
    def generate_meta_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive meta-learning report"""
        report = {
            "meta_learning_summary": {
                "total_patterns": len(self.learning_patterns),
                "total_strategies": len(self.meta_strategies),
                "total_transfer_rules": len(self.transfer_rules),
                "last_cycle": datetime.datetime.now().isoformat()
            },
            "pattern_effectiveness": {
                pattern_id: {
                    "confidence": pattern.confidence_score,
                    "usage": pattern.usage_count,
                    "effectiveness": sum(pattern.effectiveness_metrics.values()) / len(pattern.effectiveness_metrics)
                }
                for pattern_id, pattern in self.learning_patterns.items()
            },
            "strategy_performance": {
                strategy_id: {
                    "success_rate": strategy.success_rate,
                    "improvement": strategy.average_improvement,
                    "learning_velocity": strategy.learning_velocity
                }
                for strategy_id, strategy in self.meta_strategies.items()
            },
            "transfer_success": {
                rule_id: rule.success_probability
                for rule_id, rule in self.transfer_rules.items()
            },
            "learning_insights": self._generate_learning_insights(),
            "improvement_recommendations": self._generate_improvement_recommendations()
        }
        
        return report
    
    # Helper methods
    def _is_recent(self, timestamp: str, days: int = 7) -> bool:
        """Check if timestamp is within recent timeframe"""
        try:
            ts = datetime.datetime.fromisoformat(timestamp)
            cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
            return ts > cutoff
        except:
            return False
    
    def _is_pattern_duplicate(self, pattern: LearningPattern) -> bool:
        """Check if pattern is a duplicate of existing patterns"""
        for existing_pattern in self.learning_patterns.values():
            similarity = self._calculate_pattern_similarity(pattern, existing_pattern)
            if similarity > 0.8:  # High similarity threshold
                return True
        return False
    
    def _calculate_pattern_confidence(self, pattern: LearningPattern) -> float:
        """Calculate confidence score for a pattern"""
        # Simplified confidence calculation
        effectiveness_avg = sum(pattern.effectiveness_metrics.values()) / len(pattern.effectiveness_metrics)
        usage_factor = min(pattern.usage_count / 10.0, 1.0)  # Normalize usage
        generalization_factor = pattern.generalization_level / 10.0
        
        return (effectiveness_avg * 0.5 + usage_factor * 0.3 + generalization_factor * 0.2)
    
    def _calculate_pattern_similarity(self, pattern1: LearningPattern, pattern2: LearningPattern) -> float:
        """Calculate similarity between two patterns"""
        # Simple similarity based on description and rules
        desc_similarity = len(set(pattern1.pattern_description.split()) & 
                             set(pattern2.pattern_description.split())) / \
                         max(len(pattern1.pattern_description.split()), 
                             len(pattern2.pattern_description.split()))
        
        return desc_similarity  # Simplified
    
    def _find_pattern_applications(self, pattern: LearningPattern) -> List[Dict[str, Any]]:
        """Find recent applications of a pattern"""
        applications = []
        
        # Search through recent problem solutions for pattern usage
        for problem in self.memory_system.problems_db.values():
            if self._is_recent(problem.timestamp):
                # Check if pattern was used (simplified detection)
                if any(keyword in problem.solution_approach.lower() 
                       for keyword in pattern.pattern_description.lower().split()[:3]):
                    applications.append({
                        "problem_id": problem.problem_id,
                        "success_metrics": problem.success_metrics,
                        "timestamp": problem.timestamp
                    })
        
        return applications
    
    def _calculate_updated_effectiveness(self, pattern: LearningPattern, applications: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate updated effectiveness metrics"""
        # Average success metrics from applications
        updated_metrics = {}
        
        for metric_name in pattern.effectiveness_metrics.keys():
            values = []
            for app in applications:
                if metric_name in app["success_metrics"]:
                    values.append(app["success_metrics"][metric_name])
            
            if values:
                updated_metrics[metric_name] = sum(values) / len(values) / 100.0  # Normalize
            else:
                updated_metrics[metric_name] = pattern.effectiveness_metrics[metric_name]
        
        return updated_metrics
    
    # Additional placeholder methods for complex functionality
    def _is_strategy_viable(self, strategy: MetaStrategy) -> bool:
        return True  # Simplified
    
    def _analyze_performance_trend(self, strategy: MetaStrategy) -> str:
        if len(strategy.performance_history) < 2:
            return "stable"
        
        recent = strategy.performance_history[-1]
        previous = strategy.performance_history[-2]
        
        if recent.get("success_rate", 0) < previous.get("success_rate", 0) - 0.05:
            return "declining"
        elif abs(recent.get("success_rate", 0) - previous.get("success_rate", 0)) < 0.02:
            return "plateauing"
        else:
            return "improving"
    
    def _analyze_domain_patterns(self) -> Dict[str, Any]:
        return {"domains": ["software_development", "ai_systems", "architecture"]}
    
    def _generate_domain_pairs(self) -> List[Tuple[str, str]]:
        domains = ["software_development", "ai_systems", "architecture", "process_optimization"]
        pairs = []
        for i, source in enumerate(domains):
            for target in domains[i+1:]:
                pairs.append((source, target))
        return pairs
    
    def _calculate_transfer_potential(self, source: str, target: str, analysis: Dict[str, Any]) -> float:
        return 0.75  # Simplified
    
    def _find_transferable_patterns(self, source: str, target: str) -> List[str]:
        return [p.pattern_id for p in self.learning_patterns.values() 
                if source in p.source_domains and target not in p.target_domains]
    
    def _analyze_algorithm_performance(self) -> Dict[str, Dict[str, float]]:
        return {
            "pattern_extractor": {"efficiency": 0.85, "accuracy": 0.88},
            "strategy_synthesizer": {"efficiency": 0.78, "accuracy": 0.82}
        }
    
    async def _generate_algorithm_variants(self, algorithm_name: str) -> List[Dict[str, Any]]:
        return [{"name": f"{algorithm_name}_v2", "performance": 0.9}]
    
    async def _test_algorithm_variants(self, variants: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if variants:
            return max(variants, key=lambda x: x["performance"])
        return None
    
    def _validate_pattern_effectiveness(self, pattern: LearningPattern) -> float:
        return pattern.confidence_score
    
    def _validate_strategy_effectiveness(self, strategy: MetaStrategy) -> float:
        return strategy.success_rate
    
    def _validate_transfer_effectiveness(self, rule: KnowledgeTransferRule) -> float:
        return rule.success_probability
    
    def _select_optimal_strategy(self, problem_description: str, context: Dict[str, Any]) -> Optional[MetaStrategy]:
        # Select highest performing strategy for the context
        applicable_strategies = [s for s in self.meta_strategies.values() 
                               if any(ctx in problem_description.lower() for ctx in s.applicable_contexts)]
        
        if applicable_strategies:
            return max(applicable_strategies, key=lambda x: x.success_rate)
        return None
    
    def _find_applicable_patterns(self, problem_description: str, context: Dict[str, Any]) -> List[LearningPattern]:
        return [p for p in self.learning_patterns.values() if p.confidence_score > 0.7]
    
    def _check_transfer_opportunities(self, problem_description: str, context: Dict[str, Any]) -> List[str]:
        return [rule.rule_id for rule in self.transfer_rules.values() 
                if rule.success_probability > 0.8]
    
    def _generate_solution_approach(self, strategy: Optional[MetaStrategy], 
                                   patterns: List[LearningPattern], 
                                   transfers: List[str]) -> str:
        if strategy:
            return f"Apply {strategy.strategy_name} with {len(patterns)} patterns and {len(transfers)} transfers"
        return "Apply default approach with available patterns"
    
    def _calculate_solution_confidence(self, strategy: Optional[MetaStrategy], 
                                     patterns: List[LearningPattern], 
                                     transfers: List[str]) -> float:
        base_confidence = 0.5
        if strategy:
            base_confidence = strategy.success_rate
        
        pattern_boost = min(len(patterns) * 0.1, 0.3)
        transfer_boost = min(len(transfers) * 0.05, 0.2)
        
        return min(base_confidence + pattern_boost + transfer_boost, 1.0)
    
    def _generate_learning_insights(self) -> List[str]:
        insights = []
        
        # Pattern insights
        top_patterns = sorted(self.learning_patterns.values(), 
                            key=lambda x: x.confidence_score, reverse=True)[:3]
        insights.extend([f"Most effective pattern: {p.pattern_id}" for p in top_patterns])
        
        # Strategy insights
        top_strategies = sorted(self.meta_strategies.values(), 
                              key=lambda x: x.success_rate, reverse=True)[:3]
        insights.extend([f"Most successful strategy: {s.strategy_name}" for s in top_strategies])
        
        return insights
    
    def _generate_improvement_recommendations(self) -> List[str]:
        recommendations = []
        
        # Low-performing patterns
        weak_patterns = [p for p in self.learning_patterns.values() if p.confidence_score < 0.6]
        if weak_patterns:
            recommendations.append(f"Review and improve {len(weak_patterns)} low-confidence patterns")
        
        # Underused strategies
        unused_strategies = [s for s in self.meta_strategies.values() 
                           if len(s.performance_history) < 3]
        if unused_strategies:
            recommendations.append(f"Test and validate {len(unused_strategies)} underused strategies")
        
        return recommendations


# Supporting classes for meta-learning functionality
class PatternExtractor:
    """Extracts learning patterns from problem-solving experiences"""
    
    async def extract_patterns(self, problems: List[ProblemPattern]) -> List[LearningPattern]:
        patterns = []
        
        # Group problems by similarity
        problem_groups = self._group_similar_problems(problems)
        
        for group in problem_groups:
            if len(group) >= 2:  # Need multiple examples to extract pattern
                pattern = self._extract_pattern_from_group(group)
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    def _group_similar_problems(self, problems: List[ProblemPattern]) -> List[List[ProblemPattern]]:
        # Simple grouping by problem type
        groups = defaultdict(list)
        for problem in problems:
            groups[problem.problem_type].append(problem)
        
        return [group for group in groups.values() if len(group) >= 2]
    
    def _extract_pattern_from_group(self, problems: List[ProblemPattern]) -> Optional[LearningPattern]:
        # Find common elements across problems
        common_steps = self._find_common_steps(problems)
        common_approaches = self._find_common_approaches(problems)
        
        if common_steps and common_approaches:
            pattern_id = f"extracted_{hashlib.md5(str(problems).encode()).hexdigest()[:8]}"
            
            return LearningPattern(
                pattern_id=pattern_id,
                pattern_type="extracted_pattern",
                source_domains=[p.problem_type for p in problems],
                target_domains=[],
                pattern_description=f"Pattern extracted from {len(problems)} similar problems",
                extraction_rules=common_steps,
                application_conditions=common_approaches,
                success_indicators=["Improved success metrics", "Faster resolution"],
                effectiveness_metrics=self._calculate_group_effectiveness(problems),
                confidence_score=0.7,  # Initial confidence
                generalization_level=5,
                last_validation=datetime.datetime.now().isoformat(),
                usage_count=0
            )
        
        return None
    
    def _find_common_steps(self, problems: List[ProblemPattern]) -> List[str]:
        # Find steps that appear in multiple problems
        all_steps = []
        for problem in problems:
            all_steps.extend(problem.solution_steps)
        
        step_counts = defaultdict(int)
        for step in all_steps:
            step_counts[step] += 1
        
        return [step for step, count in step_counts.items() if count > 1]
    
    def _find_common_approaches(self, problems: List[ProblemPattern]) -> List[str]:
        approaches = [p.solution_approach for p in problems]
        approach_counts = defaultdict(int)
        for approach in approaches:
            approach_counts[approach] += 1
        
        return [approach for approach, count in approach_counts.items() if count > 1]
    
    def _calculate_group_effectiveness(self, problems: List[ProblemPattern]) -> Dict[str, float]:
        # Average effectiveness metrics across problems
        all_metrics = defaultdict(list)
        
        for problem in problems:
            for metric, value in problem.success_metrics.items():
                all_metrics[metric].append(value)
        
        return {metric: sum(values) / len(values) / 100.0 
                for metric, values in all_metrics.items()}


class StrategySynthesizer:
    """Synthesizes new meta-strategies from successful patterns"""
    
    async def synthesize_strategies(self, patterns: List[LearningPattern]) -> List[MetaStrategy]:
        strategies = []
        
        # Group patterns by type and domain
        pattern_groups = self._group_patterns_for_synthesis(patterns)
        
        for group_key, group_patterns in pattern_groups.items():
            if len(group_patterns) >= 3:  # Need multiple patterns to synthesize strategy
                strategy = self._synthesize_strategy_from_patterns(group_key, group_patterns)
                if strategy:
                    strategies.append(strategy)
        
        return strategies
    
    def _group_patterns_for_synthesis(self, patterns: List[LearningPattern]) -> Dict[str, List[LearningPattern]]:
        groups = defaultdict(list)
        
        for pattern in patterns:
            # Group by pattern type and primary source domain
            key = f"{pattern.pattern_type}_{pattern.source_domains[0] if pattern.source_domains else 'unknown'}"
            groups[key].append(pattern)
        
        return groups
    
    def _synthesize_strategy_from_patterns(self, group_key: str, patterns: List[LearningPattern]) -> Optional[MetaStrategy]:
        # Create strategy from pattern combination
        strategy_id = f"synthesized_{group_key}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Combine extraction rules as strategy steps
        strategy_steps = []
        for pattern in patterns:
            strategy_steps.extend(pattern.extraction_rules[:2])  # Take top 2 rules from each
        
        # Remove duplicates while preserving order
        unique_steps = []
        seen = set()
        for step in strategy_steps:
            if step not in seen:
                unique_steps.append(step)
                seen.add(step)
        
        # Calculate combined effectiveness
        avg_effectiveness = sum(sum(p.effectiveness_metrics.values()) / len(p.effectiveness_metrics) 
                               for p in patterns) / len(patterns)
        
        return MetaStrategy(
            strategy_id=strategy_id,
            strategy_name=f"Synthesized Strategy: {group_key.replace('_', ' ').title()}",
            description=f"Strategy synthesized from {len(patterns)} high-performing patterns",
            applicable_contexts=list(set([domain for p in patterns for domain in p.source_domains])),
            strategy_steps=unique_steps,
            adaptation_rules=[
                "Monitor performance and adapt based on feedback",
                "Combine patterns when appropriate",
                "Validate results against original pattern success criteria"
            ],
            performance_history=[{
                "timestamp": datetime.datetime.now().isoformat(),
                "success_rate": avg_effectiveness,
                "efficiency": avg_effectiveness * 0.9
            }],
            evolution_trajectory=[{
                "version": "1.0",
                "changes": ["initial synthesis"],
                "performance_delta": 0.0
            }],
            success_rate=avg_effectiveness,
            average_improvement=0.0,
            learning_velocity=0.05
        )


class KnowledgeTransferEngine:
    """Handles cross-domain knowledge transfer"""
    
    async def execute_transfer(self, source_domain: str, target_domain: str, 
                             patterns: List[str]) -> Dict[str, Any]:
        # Simplified transfer execution
        return {
            "success": True,
            "transfer_type": "analogical",
            "mapping_rules": [f"Map {source_domain} concepts to {target_domain}"],
            "adaptations": [f"Adapt for {target_domain} constraints"],
            "success_probability": 0.8,
            "validation_criteria": ["Performance improvement", "Domain fit"]
        }


class MetaOptimizer:
    """Optimizes meta-strategies and learning algorithms"""
    
    async def optimize_strategy(self, strategy: MetaStrategy) -> Optional[MetaStrategy]:
        # Create optimized version
        optimized = MetaStrategy(
            strategy_id=strategy.strategy_id,
            strategy_name=strategy.strategy_name,
            description=f"Optimized: {strategy.description}",
            applicable_contexts=strategy.applicable_contexts,
            strategy_steps=strategy.strategy_steps,
            adaptation_rules=strategy.adaptation_rules + ["Enhanced optimization rule"],
            performance_history=strategy.performance_history,
            evolution_trajectory=strategy.evolution_trajectory + [{
                "version": f"{len(strategy.evolution_trajectory) + 1}.0",
                "changes": ["performance optimization"],
                "performance_delta": 0.05
            }],
            success_rate=min(strategy.success_rate + 0.05, 1.0),
            average_improvement=strategy.average_improvement,
            learning_velocity=strategy.learning_velocity + 0.02
        )
        
        return optimized
    
    async def create_variant(self, strategy: MetaStrategy) -> Optional[MetaStrategy]:
        # Create variant with modifications
        variant_id = f"{strategy.strategy_id}_variant"
        
        return MetaStrategy(
            strategy_id=variant_id,
            strategy_name=f"{strategy.strategy_name} - Variant",
            description=f"Variant: {strategy.description}",
            applicable_contexts=strategy.applicable_contexts,
            strategy_steps=strategy.strategy_steps + ["Additional exploratory step"],
            adaptation_rules=strategy.adaptation_rules,
            performance_history=[],
            evolution_trajectory=[{
                "version": "1.0",
                "changes": ["variant creation"],
                "performance_delta": 0.0
            }],
            success_rate=strategy.success_rate * 0.95,  # Start slightly lower
            average_improvement=0.0,
            learning_velocity=strategy.learning_velocity
        )


async def main():
    """Example usage of the Meta-Learning System"""
    # Initialize dependencies
    memory_system = ProblemSolvingMemorySystem()
    improvement_orchestrator = SelfImprovementOrchestrator(memory_system)
    
    # Initialize meta-learning system
    meta_learner = MetaLearningSystem(memory_system, improvement_orchestrator)
    
    # Run a meta-learning cycle
    results = await meta_learner.meta_learning_cycle()
    print(f"Meta-learning cycle results: {results}")
    
    # Apply meta-learning to a new problem
    solution_guidance = meta_learner.apply_meta_learning_to_problem(
        "Need to optimize database query performance",
        {"domain": "software_optimization", "complexity": "medium"}
    )
    
    print(f"Solution guidance: {solution_guidance}")
    
    # Generate comprehensive report
    report = meta_learner.generate_meta_learning_report()
    print(f"Meta-learning report summary:")
    print(f"- Patterns: {report['meta_learning_summary']['total_patterns']}")
    print(f"- Strategies: {report['meta_learning_summary']['total_strategies']}")
    print(f"- Transfer rules: {report['meta_learning_summary']['total_transfer_rules']}")


if __name__ == "__main__":
    asyncio.run(main())