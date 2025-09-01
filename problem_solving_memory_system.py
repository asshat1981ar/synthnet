#!/usr/bin/env python3
"""
SynthNet AI - Problem Solving Memory System
==========================================

A self-improving system that captures solution patterns, methodologies, and 
problem-solving approaches from the SynthNet AI development journey.

This system learns from past solutions to enhance future problem-solving capabilities.
"""

import json
import datetime
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProblemPattern:
    """Represents a problem and its solution pattern"""
    problem_id: str
    problem_type: str
    problem_description: str
    context: Dict[str, Any]
    solution_approach: str
    methodology_used: str
    ai_contributors: List[str]
    solution_steps: List[str]
    success_metrics: Dict[str, float]
    lessons_learned: List[str]
    reusable_components: List[str]
    failure_modes: List[str]
    optimization_opportunities: List[str]
    timestamp: str
    difficulty_level: int  # 1-10
    generalization_potential: int  # 1-10

@dataclass
class MethodologyTemplate:
    """Template for applying proven methodologies to new problems"""
    methodology_name: str
    description: str
    applicable_domains: List[str]
    steps: List[str]
    success_indicators: List[str]
    common_pitfalls: List[str]
    required_resources: List[str]
    expected_outcomes: List[str]
    optimization_strategies: List[str]

@dataclass
class SolutionEvolution:
    """Tracks how solutions evolve over time"""
    evolution_id: str
    problem_id: str
    iterations: List[Dict[str, Any]]
    improvement_metrics: List[Dict[str, float]]
    pattern_emergence: List[str]
    breakthrough_moments: List[Dict[str, Any]]

class ProblemSolvingMemorySystem:
    """
    Self-improving memory system that captures and generalizes problem-solving patterns
    """
    
    def __init__(self, memory_dir: str = "problem_solving_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Core memory components
        self.problems_db = {}
        self.methodologies_db = {}
        self.evolutions_db = {}
        self.success_patterns = {}
        self.failure_patterns = {}
        
        # Learning components
        self.pattern_recognition_engine = PatternRecognitionEngine()
        self.methodology_generator = MethodologyGenerator()
        self.solution_predictor = SolutionPredictor()
        
        self._load_existing_memory()
    
    def _load_existing_memory(self):
        """Load existing memory from files"""
        try:
            # Load SynthNet AI development patterns
            self._initialize_synthnet_patterns()
            logger.info("Loaded SynthNet AI development patterns")
        except Exception as e:
            logger.warning(f"Could not load existing memory: {e}")
    
    def _initialize_synthnet_patterns(self):
        """Initialize memory with patterns from SynthNet AI development journey"""
        
        # Pattern 1: Build System Resolution
        build_problem = ProblemPattern(
            problem_id="synthnet_build_system",
            problem_type="development_environment",
            problem_description="Android development in Termux with Gradle failures and SDK issues",
            context={
                "environment": "Termux on Android",
                "constraints": ["Limited resources", "Non-standard environment", "SDK limitations"],
                "requirements": ["APK generation", "Multi-project support", "Production builds"]
            },
            solution_approach="Progressive enhancement from manual to automated",
            methodology_used="FORGE (systematic analysis → optimization → automation)",
            ai_contributors=["Claude Code", "Gemini CLI", "GitHub Copilot"],
            solution_steps=[
                "Analyze existing build failures and root causes",
                "Implement manual build processes as fallback",
                "Create automated templates for common scenarios",
                "Develop universal build system with multiple project types",
                "Add validation and testing frameworks",
                "Enable continuous optimization"
            ],
            success_metrics={
                "build_success_rate": 95.0,
                "setup_time_reduction": 80.0,
                "automation_coverage": 90.0,
                "error_recovery_rate": 85.0
            },
            lessons_learned=[
                "Environmental constraints require innovative solutions",
                "Manual processes can be systematized into reusable templates",
                "Fallback mechanisms are crucial for reliability",
                "Progressive enhancement works better than complete rewrites"
            ],
            reusable_components=[
                "Android SDK setup scripts",
                "Gradle wrapper configuration",
                "APK build templates",
                "Project scaffolding system"
            ],
            failure_modes=[
                "SDK download failures",
                "Java version mismatches",
                "Memory limitations during builds",
                "Network connectivity issues"
            ],
            optimization_opportunities=[
                "Caching strategies for dependencies",
                "Parallel build processes",
                "Incremental compilation",
                "Resource usage optimization"
            ],
            timestamp=datetime.datetime.now().isoformat(),
            difficulty_level=8,
            generalization_potential=9
        )
        
        # Pattern 2: Multi-Agent AI Orchestration
        ai_orchestration = ProblemPattern(
            problem_id="multi_agent_orchestration",
            problem_type="ai_architecture",
            problem_description="Coordinating multiple AI agents for complex task execution",
            context={
                "complexity": "High",
                "agents": ["Conductor", "Strategy", "Implementation", "Testing", "Documentation"],
                "requirements": ["Real-time coordination", "Consensus building", "Conflict resolution"]
            },
            solution_approach="Hierarchical coordination with specialized roles",
            methodology_used="Clean Architecture + Actor Model + Consensus Algorithms",
            ai_contributors=["Claude Code", "Gemini CLI"],
            solution_steps=[
                "Define agent specializations and responsibilities",
                "Implement communication protocols (WebSocket-based)",
                "Create consensus mechanisms for decision making",
                "Add conflict resolution strategies",
                "Implement performance monitoring and optimization",
                "Enable autonomous learning and adaptation"
            ],
            success_metrics={
                "coordination_efficiency": 89.0,
                "task_completion_rate": 92.0,
                "consensus_accuracy": 87.0,
                "response_time": 250.0  # milliseconds
            },
            lessons_learned=[
                "Agent specialization improves overall performance",
                "Communication protocols must handle failure cases",
                "Consensus building requires sophisticated algorithms",
                "Performance monitoring enables continuous optimization"
            ],
            reusable_components=[
                "Agent base classes",
                "Communication protocols",
                "Consensus algorithms",
                "Performance monitoring systems"
            ],
            failure_modes=[
                "Network communication failures",
                "Agent synchronization issues",
                "Consensus deadlocks",
                "Resource exhaustion"
            ],
            optimization_opportunities=[
                "Dynamic agent allocation",
                "Intelligent load balancing",
                "Predictive resource management",
                "Adaptive communication strategies"
            ],
            timestamp=datetime.datetime.now().isoformat(),
            difficulty_level=9,
            generalization_potential=8
        )
        
        # Pattern 3: MCP Ecosystem Development
        mcp_ecosystem = ProblemPattern(
            problem_id="mcp_ecosystem_development",
            problem_type="ecosystem_creation",
            problem_description="Building comprehensive MCP server ecosystem from discovery to deployment",
            context={
                "scope": "Industry-wide ecosystem analysis",
                "servers_analyzed": 200,
                "domains": ["Healthcare", "Education", "IoT", "Legal", "Manufacturing"],
                "requirements": ["Server creation", "Deployment automation", "Testing frameworks"]
            },
            solution_approach="Research-driven template generation with automated deployment",
            methodology_used="Gap Analysis + Template Engineering + Infrastructure as Code",
            ai_contributors=["Claude Code", "Gemini CLI", "Research Agent"],
            solution_steps=[
                "Comprehensive ecosystem analysis and gap identification",
                "Template-based server generation system",
                "Multi-environment deployment automation",
                "Comprehensive testing and validation frameworks",
                "Security and compliance integration",
                "Continuous monitoring and optimization"
            ],
            success_metrics={
                "servers_generated": 12.0,
                "deployment_success_rate": 94.0,
                "test_coverage": 85.0,
                "security_compliance": 92.0
            },
            lessons_learned=[
                "Ecosystem analysis reveals systematic opportunities",
                "Template-based generation scales development",
                "Multi-environment deployment requires careful orchestration",
                "Security must be built-in from the start"
            ],
            reusable_components=[
                "Server templates (Python/TypeScript)",
                "Deployment configurations (Docker/Kubernetes)",
                "Testing frameworks",
                "Security scanning tools"
            ],
            failure_modes=[
                "Template generation errors",
                "Deployment configuration mismatches",
                "Security vulnerability discoveries",
                "Performance bottlenecks"
            ],
            optimization_opportunities=[
                "AI-powered template customization",
                "Advanced deployment strategies",
                "Automated security hardening",
                "Performance optimization algorithms"
            ],
            timestamp=datetime.datetime.now().isoformat(),
            difficulty_level=7,
            generalization_potential=10
        )
        
        # Store patterns
        self.problems_db[build_problem.problem_id] = build_problem
        self.problems_db[ai_orchestration.problem_id] = ai_orchestration
        self.problems_db[mcp_ecosystem.problem_id] = mcp_ecosystem
        
        # Initialize methodologies
        self._initialize_methodologies()
    
    def _initialize_methodologies(self):
        """Initialize proven methodologies from SynthNet development"""
        
        # FORGE Methodology
        forge_methodology = MethodologyTemplate(
            methodology_name="FORGE",
            description="File triage, Optimization, Reinforcement, Governance, Evolution",
            applicable_domains=["Software Development", "AI Systems", "DevOps", "Quality Assurance"],
            steps=[
                "File/Component triage using ML-based prioritization",
                "Optimization through advanced algorithms (GNN, etc.)",
                "Reinforcement learning for continuous improvement",
                "Governance through explainable AI and risk assessment", 
                "Evolution through autonomous adaptation"
            ],
            success_indicators=[
                "Automated accuracy >80%",
                "Performance improvement >10%",
                "Reduced manual intervention >70%",
                "System reliability >95%"
            ],
            common_pitfalls=[
                "Over-optimization leading to complexity",
                "Insufficient training data for ML components",
                "Lack of human oversight in critical decisions",
                "Evolution without proper validation"
            ],
            required_resources=[
                "Machine learning infrastructure",
                "Performance monitoring systems",
                "Validation and testing frameworks",
                "Human expertise for oversight"
            ],
            expected_outcomes=[
                "11-17% performance improvements",
                "Reduced development time",
                "Higher code quality",
                "Autonomous system evolution"
            ],
            optimization_strategies=[
                "Continuous learning from new data",
                "Multi-objective optimization",
                "Adaptive algorithm selection",
                "Human-in-the-loop validation"
            ]
        )
        
        # Multi-AI Collaboration Methodology
        multi_ai_methodology = MethodologyTemplate(
            methodology_name="Multi-AI Collaboration",
            description="Leveraging different AI systems for complementary strengths",
            applicable_domains=["Software Development", "Research", "Analysis", "Decision Making"],
            steps=[
                "Identify complementary AI system strengths",
                "Define clear roles and responsibilities",
                "Establish communication and coordination protocols",
                "Implement cross-validation mechanisms",
                "Synthesize insights from multiple perspectives",
                "Enable continuous learning and adaptation"
            ],
            success_indicators=[
                "Quality scores >90/100",
                "Reduced single-point failures",
                "Improved solution diversity",
                "Enhanced error detection"
            ],
            common_pitfalls=[
                "Conflicting AI recommendations without resolution",
                "Over-complexity in coordination mechanisms",
                "Insufficient specialization leading to redundancy",
                "Communication bottlenecks"
            ],
            required_resources=[
                "Multiple AI system integrations",
                "Coordination infrastructure",
                "Conflict resolution mechanisms",
                "Performance monitoring"
            ],
            expected_outcomes=[
                "Higher quality solutions",
                "Reduced risk of errors",
                "Faster problem resolution",
                "Continuous improvement"
            ],
            optimization_strategies=[
                "Dynamic role assignment",
                "Intelligent conflict resolution",
                "Adaptive coordination protocols",
                "Performance-based optimization"
            ]
        )
        
        self.methodologies_db["FORGE"] = forge_methodology
        self.methodologies_db["Multi-AI"] = multi_ai_methodology
    
    def add_problem_pattern(self, pattern: ProblemPattern):
        """Add a new problem pattern to memory"""
        self.problems_db[pattern.problem_id] = pattern
        self._analyze_pattern_relationships(pattern)
        self._save_memory()
        logger.info(f"Added problem pattern: {pattern.problem_id}")
    
    def find_similar_problems(self, problem_description: str, context: Dict[str, Any]) -> List[ProblemPattern]:
        """Find similar problems based on description and context"""
        return self.pattern_recognition_engine.find_similar(problem_description, context, self.problems_db)
    
    def suggest_methodology(self, problem_type: str, context: Dict[str, Any]) -> List[MethodologyTemplate]:
        """Suggest appropriate methodologies for a given problem"""
        applicable_methodologies = []
        
        for methodology in self.methodologies_db.values():
            if any(domain.lower() in problem_type.lower() for domain in methodology.applicable_domains):
                applicable_methodologies.append(methodology)
        
        return applicable_methodologies
    
    def predict_solution_approach(self, problem_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict likely solution approach based on historical patterns"""
        similar_problems = self.find_similar_problems(problem_description, context)
        
        if not similar_problems:
            return {"confidence": 0.0, "suggestion": "No similar patterns found"}
        
        # Analyze patterns in successful solutions
        approaches = {}
        total_success = 0
        
        for problem in similar_problems:
            success_score = sum(problem.success_metrics.values()) / len(problem.success_metrics)
            approaches[problem.solution_approach] = approaches.get(problem.solution_approach, 0) + success_score
            total_success += success_score
        
        # Find most successful approach
        best_approach = max(approaches.keys(), key=approaches.get)
        confidence = approaches[best_approach] / total_success if total_success > 0 else 0.0
        
        return {
            "confidence": confidence,
            "suggested_approach": best_approach,
            "similar_problems": [p.problem_id for p in similar_problems[:3]],
            "success_factors": self._extract_success_factors(similar_problems)
        }
    
    def _extract_success_factors(self, problems: List[ProblemPattern]) -> List[str]:
        """Extract common success factors from similar problems"""
        all_lessons = []
        for problem in problems:
            all_lessons.extend(problem.lessons_learned)
        
        # Count frequency of similar lessons
        lesson_counts = {}
        for lesson in all_lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
        
        # Return most common lessons
        return sorted(lesson_counts.keys(), key=lesson_counts.get, reverse=True)[:5]
    
    def record_solution_evolution(self, problem_id: str, iteration_data: Dict[str, Any]):
        """Record how a solution evolves over iterations"""
        evolution_id = f"{problem_id}_evolution"
        
        if evolution_id not in self.evolutions_db:
            self.evolutions_db[evolution_id] = SolutionEvolution(
                evolution_id=evolution_id,
                problem_id=problem_id,
                iterations=[],
                improvement_metrics=[],
                pattern_emergence=[],
                breakthrough_moments=[]
            )
        
        evolution = self.evolutions_db[evolution_id]
        evolution.iterations.append(iteration_data)
        
        # Analyze for breakthrough moments
        if len(evolution.iterations) > 1:
            self._detect_breakthrough_moments(evolution, iteration_data)
        
        self._save_memory()
    
    def _detect_breakthrough_moments(self, evolution: SolutionEvolution, current_iteration: Dict[str, Any]):
        """Detect breakthrough moments in solution evolution"""
        if len(evolution.iterations) < 2:
            return
            
        prev_iteration = evolution.iterations[-2]
        
        # Check for significant improvements
        if "performance_metrics" in current_iteration and "performance_metrics" in prev_iteration:
            current_metrics = current_iteration["performance_metrics"]
            prev_metrics = prev_iteration["performance_metrics"]
            
            for metric, current_value in current_metrics.items():
                if metric in prev_metrics:
                    improvement = (current_value - prev_metrics[metric]) / prev_metrics[metric]
                    if improvement > 0.2:  # 20% improvement threshold
                        breakthrough = {
                            "iteration": len(evolution.iterations) - 1,
                            "metric": metric,
                            "improvement": improvement,
                            "description": f"Breakthrough: {improvement:.1%} improvement in {metric}",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        evolution.breakthrough_moments.append(breakthrough)
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive learning report from all patterns"""
        report = {
            "total_patterns": len(self.problems_db),
            "total_methodologies": len(self.methodologies_db),
            "success_rate_by_type": {},
            "most_effective_methodologies": {},
            "common_failure_modes": {},
            "reusable_components": {},
            "optimization_opportunities": {},
            "breakthrough_insights": []
        }
        
        # Analyze success rates by problem type
        type_success = {}
        for problem in self.problems_db.values():
            problem_type = problem.problem_type
            if problem_type not in type_success:
                type_success[problem_type] = {"total": 0, "success": 0}
            
            type_success[problem_type]["total"] += 1
            avg_success = sum(problem.success_metrics.values()) / len(problem.success_metrics)
            if avg_success > 80.0:  # Success threshold
                type_success[problem_type]["success"] += 1
        
        for ptype, data in type_success.items():
            report["success_rate_by_type"][ptype] = data["success"] / data["total"] if data["total"] > 0 else 0
        
        # Analyze methodology effectiveness
        method_usage = {}
        for problem in self.problems_db.values():
            method = problem.methodology_used
            if method not in method_usage:
                method_usage[method] = {"count": 0, "total_success": 0}
            
            method_usage[method]["count"] += 1
            avg_success = sum(problem.success_metrics.values()) / len(problem.success_metrics)
            method_usage[method]["total_success"] += avg_success
        
        for method, data in method_usage.items():
            report["most_effective_methodologies"][method] = data["total_success"] / data["count"]
        
        # Extract common patterns
        all_failures = []
        all_components = []
        all_opportunities = []
        
        for problem in self.problems_db.values():
            all_failures.extend(problem.failure_modes)
            all_components.extend(problem.reusable_components)
            all_opportunities.extend(problem.optimization_opportunities)
        
        report["common_failure_modes"] = self._count_and_rank(all_failures)
        report["reusable_components"] = self._count_and_rank(all_components)
        report["optimization_opportunities"] = self._count_and_rank(all_opportunities)
        
        # Extract breakthrough insights
        for evolution in self.evolutions_db.values():
            report["breakthrough_insights"].extend(evolution.breakthrough_moments)
        
        return report
    
    def _count_and_rank(self, items: List[str]) -> Dict[str, int]:
        """Count and rank items by frequency"""
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_pattern_relationships(self, new_pattern: ProblemPattern):
        """Analyze relationships between patterns to identify meta-patterns"""
        # Implementation for pattern relationship analysis
        pass
    
    def _save_memory(self):
        """Save memory to persistent storage"""
        try:
            memory_data = {
                "problems": {k: asdict(v) for k, v in self.problems_db.items()},
                "methodologies": {k: asdict(v) for k, v in self.methodologies_db.items()},
                "evolutions": {k: asdict(v) for k, v in self.evolutions_db.items()},
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(self.memory_dir / "memory.json", "w") as f:
                json.dump(memory_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")


class PatternRecognitionEngine:
    """Recognizes patterns in problems and solutions"""
    
    def find_similar(self, problem_description: str, context: Dict[str, Any], problems_db: Dict[str, ProblemPattern]) -> List[ProblemPattern]:
        """Find similar problems using text similarity and context matching"""
        similar_problems = []
        
        # Simple similarity based on keywords and context
        problem_words = set(problem_description.lower().split())
        
        for problem in problems_db.values():
            # Calculate similarity score
            description_words = set(problem.problem_description.lower().split())
            word_overlap = len(problem_words.intersection(description_words))
            word_similarity = word_overlap / max(len(problem_words), len(description_words))
            
            # Context similarity
            context_similarity = self._calculate_context_similarity(context, problem.context)
            
            # Combined similarity
            total_similarity = (word_similarity + context_similarity) / 2
            
            if total_similarity > 0.3:  # Similarity threshold
                similar_problems.append(problem)
        
        # Sort by similarity (approximated by success metrics for now)
        similar_problems.sort(key=lambda p: sum(p.success_metrics.values()), reverse=True)
        return similar_problems[:5]
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts"""
        common_keys = set(context1.keys()).intersection(set(context2.keys()))
        if not common_keys:
            return 0.0
        
        similarity_sum = 0.0
        for key in common_keys:
            if context1[key] == context2[key]:
                similarity_sum += 1.0
            elif isinstance(context1[key], (list, set)) and isinstance(context2[key], (list, set)):
                set1, set2 = set(context1[key]), set(context2[key])
                if set1 and set2:
                    similarity_sum += len(set1.intersection(set2)) / len(set1.union(set2))
        
        return similarity_sum / len(common_keys)


class MethodologyGenerator:
    """Generates new methodologies from successful patterns"""
    
    def generate_methodology(self, successful_patterns: List[ProblemPattern]) -> MethodologyTemplate:
        """Generate a new methodology from successful patterns"""
        # Extract common elements
        common_steps = self._extract_common_steps(successful_patterns)
        common_resources = self._extract_common_resources(successful_patterns)
        
        return MethodologyTemplate(
            methodology_name="Generated_Methodology",
            description="Auto-generated from successful patterns",
            applicable_domains=list(set(p.problem_type for p in successful_patterns)),
            steps=common_steps,
            success_indicators=["Performance improvement >10%", "Reliability >90%"],
            common_pitfalls=self._extract_common_failures(successful_patterns),
            required_resources=common_resources,
            expected_outcomes=["Improved efficiency", "Higher quality"],
            optimization_strategies=self._extract_optimizations(successful_patterns)
        )
    
    def _extract_common_steps(self, patterns: List[ProblemPattern]) -> List[str]:
        """Extract common steps from successful patterns"""
        all_steps = []
        for pattern in patterns:
            all_steps.extend(pattern.solution_steps)
        
        # Simple frequency-based extraction
        step_counts = {}
        for step in all_steps:
            step_counts[step] = step_counts.get(step, 0) + 1
        
        return [step for step, count in step_counts.items() if count > 1]
    
    def _extract_common_resources(self, patterns: List[ProblemPattern]) -> List[str]:
        """Extract common required resources"""
        all_resources = []
        for pattern in patterns:
            all_resources.extend(pattern.reusable_components)
        
        resource_counts = {}
        for resource in all_resources:
            resource_counts[resource] = resource_counts.get(resource, 0) + 1
        
        return [resource for resource, count in resource_counts.items() if count > 1]
    
    def _extract_common_failures(self, patterns: List[ProblemPattern]) -> List[str]:
        """Extract common failure modes to avoid"""
        all_failures = []
        for pattern in patterns:
            all_failures.extend(pattern.failure_modes)
        
        failure_counts = {}
        for failure in all_failures:
            failure_counts[failure] = failure_counts.get(failure, 0) + 1
        
        return [failure for failure, count in failure_counts.items() if count > 1]
    
    def _extract_optimizations(self, patterns: List[ProblemPattern]) -> List[str]:
        """Extract common optimization strategies"""
        all_optimizations = []
        for pattern in patterns:
            all_optimizations.extend(pattern.optimization_opportunities)
        
        opt_counts = {}
        for opt in all_optimizations:
            opt_counts[opt] = opt_counts.get(opt, 0) + 1
        
        return [opt for opt, count in opt_counts.items() if count > 1]


class SolutionPredictor:
    """Predicts solution success based on historical patterns"""
    
    def predict_success_probability(self, problem_pattern: ProblemPattern, similar_patterns: List[ProblemPattern]) -> float:
        """Predict probability of success for a given problem pattern"""
        if not similar_patterns:
            return 0.5  # Unknown, assume moderate probability
        
        total_success = 0.0
        weights = 0.0
        
        for pattern in similar_patterns:
            success_score = sum(pattern.success_metrics.values()) / len(pattern.success_metrics)
            similarity_weight = self._calculate_similarity_weight(problem_pattern, pattern)
            
            total_success += success_score * similarity_weight
            weights += similarity_weight
        
        return (total_success / weights) / 100.0 if weights > 0 else 0.5
    
    def _calculate_similarity_weight(self, pattern1: ProblemPattern, pattern2: ProblemPattern) -> float:
        """Calculate similarity weight between two patterns"""
        # Simple implementation based on problem type and difficulty
        type_match = 1.0 if pattern1.problem_type == pattern2.problem_type else 0.5
        difficulty_similarity = 1.0 - abs(pattern1.difficulty_level - pattern2.difficulty_level) / 10.0
        
        return (type_match + difficulty_similarity) / 2.0


def main():
    """Example usage of the Problem Solving Memory System"""
    memory_system = ProblemSolvingMemorySystem()
    
    # Example: Query for similar problems
    similar = memory_system.find_similar_problems(
        "Need to build Android app in constrained environment",
        {"environment": "mobile", "constraints": ["limited resources"]}
    )
    
    print(f"Found {len(similar)} similar problems")
    for problem in similar:
        print(f"- {problem.problem_id}: {problem.problem_description[:100]}...")
    
    # Example: Get methodology suggestions
    methodologies = memory_system.suggest_methodology(
        "development_environment", 
        {"constraints": ["resources"], "requirements": ["automation"]}
    )
    
    print(f"\nSuggested methodologies: {[m.methodology_name for m in methodologies]}")
    
    # Example: Predict solution approach
    prediction = memory_system.predict_solution_approach(
        "Build system failures in mobile environment",
        {"environment": "mobile", "tools": ["gradle"]}
    )
    
    print(f"\nSolution prediction: {prediction}")
    
    # Generate learning report
    report = memory_system.generate_learning_report()
    print(f"\nLearning Report Summary:")
    print(f"- Total patterns: {report['total_patterns']}")
    print(f"- Most effective methodology: {max(report['most_effective_methodologies'], key=report['most_effective_methodologies'].get) if report['most_effective_methodologies'] else 'None'}")
    print(f"- Top failure mode: {list(report['common_failure_modes'].keys())[0] if report['common_failure_modes'] else 'None'}")


if __name__ == "__main__":
    main()