#!/usr/bin/env python3
"""
n8n Workflow Generator with Semantic CoT Integration
Generates intelligent n8n workflows that leverage MCP servers with semantic reasoning
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowTemplate:
    """Template for generating n8n workflows"""
    template_id: str
    name: str
    description: str
    domain: str
    complexity_level: str
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    variables: Dict[str, Any]
    semantic_requirements: Dict[str, Any]

class N8NWorkflowGenerator:
    """Generate semantically enhanced n8n workflows"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, WorkflowTemplate]:
        """Initialize workflow templates"""
        templates = {}
        
        # Android Development Workflow Template
        android_template = self._create_android_development_template()
        templates[android_template.template_id] = android_template
        
        # Semantic Analysis Workflow Template  
        semantic_template = self._create_semantic_analysis_template()
        templates[semantic_template.template_id] = semantic_template
        
        # Testing Ecosystem Workflow Template
        testing_template = self._create_testing_ecosystem_template()
        templates[testing_template.template_id] = testing_template
        
        # Architecture Intelligence Workflow Template
        architecture_template = self._create_architecture_intelligence_template()
        templates[architecture_template.template_id] = architecture_template
        
        return templates
        
    def _create_android_development_template(self) -> WorkflowTemplate:
        """Create Android development workflow template"""
        
        nodes = [
            {
                "id": "webhook_trigger",
                "type": "Webhook",
                "typeVersion": 1,
                "position": [100, 100],
                "name": "Development Request",
                "parameters": {
                    "path": "android-dev",
                    "httpMethod": "POST",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "semantic_cot_reasoning",
                "type": "HTTP Request", 
                "typeVersion": 2,
                "position": [300, 100],
                "name": "Semantic CoT Analysis",
                "parameters": {
                    "url": "http://localhost:8772/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "semantic_cot_reasoning",
                                "arguments": {
                                    "objective": "={{ $json.objective }}",
                                    "context": "={{ $json.context }}",
                                    "constraints": "={{ $json.constraints }}"
                                }
                            }
                        }
                    },
                    "options": {
                        "timeout": 60000
                    }
                }
            },
            {
                "id": "synthnet_hub_integration",
                "type": "HTTP Request",
                "typeVersion": 2, 
                "position": [500, 100],
                "name": "SynthNet Android Hub",
                "parameters": {
                    "url": "http://localhost:8767/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "create_app_from_description",
                                "arguments": {
                                    "description": "={{ $json.reasoning_chain.objective }}",
                                    "quality_level": "BALANCED",
                                    "semantic_context": "={{ $json.reasoning_chain.semantic_context }}"
                                }
                            }
                        }
                    }
                }
            },
            {
                "id": "response_formatting",
                "type": "Function",
                "typeVersion": 1,
                "position": [700, 100], 
                "name": "Format Response",
                "parameters": {
                    "jsCode": "return {\n  workflow_id: $input.all()[0].workflow_id,\n  reasoning_chain: $input.all()[0].reasoning_chain,\n  app_generation_result: $input.all()[1].result,\n  timestamp: new Date().toISOString(),\n  semantic_coherence: $input.all()[0].semantic_coherence_score\n};"
                }
            },
            {
                "id": "webhook_response",
                "type": "Respond to Webhook",
                "typeVersion": 1,
                "position": [900, 100],
                "name": "Send Response",
                "parameters": {
                    "httpStatusCode": 200,
                    "options": {}
                }
            }
        ]
        
        connections = {
            "webhook_trigger": {
                "main": [
                    [
                        {
                            "node": "semantic_cot_reasoning",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "semantic_cot_reasoning": {
                "main": [
                    [
                        {
                            "node": "synthnet_hub_integration",
                            "type": "main", 
                            "index": 0
                        }
                    ]
                ]
            },
            "synthnet_hub_integration": {
                "main": [
                    [
                        {
                            "node": "response_formatting",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "response_formatting": {
                "main": [
                    [
                        {
                            "node": "webhook_response", 
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
        
        return WorkflowTemplate(
            template_id="android_dev_with_semantic_cot",
            name="Android Development with Semantic CoT",
            description="Intelligent Android app development using semantic Chain-of-Thought reasoning",
            domain="android_development",
            complexity_level="balanced",
            nodes=nodes,
            connections=connections,
            variables={
                "semantic_reasoning_enabled": True,
                "quality_level": "BALANCED",
                "timeout_seconds": 300
            },
            semantic_requirements={
                "reasoning_depth": "comprehensive",
                "context_preservation": True,
                "semantic_validation": True
            }
        )
        
    def _create_semantic_analysis_template(self) -> WorkflowTemplate:
        """Create semantic analysis workflow template"""
        
        nodes = [
            {
                "id": "manual_trigger",
                "type": "Manual Trigger",
                "typeVersion": 1,
                "position": [100, 100],
                "name": "Start Analysis"
            },
            {
                "id": "data_input",
                "type": "Edit Fields",
                "typeVersion": 1,
                "position": [300, 100],
                "name": "Prepare Analysis Data",
                "parameters": {
                    "fields": {
                        "values": [
                            {
                                "name": "concepts",
                                "type": "string"
                            },
                            {
                                "name": "analysis_type", 
                                "type": "string"
                            },
                            {
                                "name": "semantic_context",
                                "type": "object"
                            }
                        ]
                    }
                }
            },
            {
                "id": "semantic_concept_analysis",
                "type": "HTTP Request",
                "typeVersion": 2,
                "position": [500, 100],
                "name": "Semantic Concept Analysis",
                "parameters": {
                    "url": "http://localhost:8772/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "semantic_concept_analysis",
                                "arguments": {
                                    "concepts": "={{ $json.concepts }}",
                                    "analysis_type": "={{ $json.analysis_type }}"
                                }
                            }
                        }
                    }
                }
            },
            {
                "id": "bridge_integration",
                "type": "HTTP Request",
                "typeVersion": 2,
                "position": [500, 250],
                "name": "n8n-MCP Bridge Enhancement",
                "parameters": {
                    "url": "http://localhost:8773/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "create_semantic_template",
                                "arguments": {
                                    "domain": "semantic_analysis",
                                    "use_case": "concept_analysis",
                                    "complexity_level": "advanced"
                                }
                            }
                        }
                    }
                }
            },
            {
                "id": "results_merger",
                "type": "Merge",
                "typeVersion": 2,
                "position": [700, 175],
                "name": "Merge Analysis Results",
                "parameters": {
                    "mode": "mergeByIndex"
                }
            }
        ]
        
        connections = {
            "manual_trigger": {
                "main": [
                    [
                        {
                            "node": "data_input",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "data_input": {
                "main": [
                    [
                        {
                            "node": "semantic_concept_analysis",
                            "type": "main",
                            "index": 0
                        },
                        {
                            "node": "bridge_integration",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "semantic_concept_analysis": {
                "main": [
                    [
                        {
                            "node": "results_merger",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "bridge_integration": {
                "main": [
                    [
                        {
                            "node": "results_merger",
                            "type": "main",
                            "index": 1
                        }
                    ]
                ]
            }
        }
        
        return WorkflowTemplate(
            template_id="semantic_analysis_comprehensive",
            name="Comprehensive Semantic Analysis",
            description="Deep semantic analysis with concept relationships and bridge enhancement",
            domain="semantic_analysis", 
            complexity_level="advanced",
            nodes=nodes,
            connections=connections,
            variables={
                "analysis_depth": "comprehensive",
                "bridge_enhancement": True
            },
            semantic_requirements={
                "concept_mapping": True,
                "relationship_analysis": True,
                "cross_domain_insights": True
            }
        )
        
    def _create_testing_ecosystem_template(self) -> WorkflowTemplate:
        """Create testing ecosystem workflow template"""
        
        nodes = [
            {
                "id": "cron_trigger",
                "type": "Cron",
                "typeVersion": 1,
                "position": [100, 100],
                "name": "Schedule Testing",
                "parameters": {
                    "rule": {
                        "interval": [
                            {
                                "field": "cronExpression",
                                "expression": "0 */4 * * *"
                            }
                        ]
                    }
                }
            },
            {
                "id": "project_analysis",
                "type": "Function",
                "typeVersion": 1,
                "position": [300, 100],
                "name": "Analyze Project Context", 
                "parameters": {
                    "jsCode": "return {\n  project_path: '/data/data/com.termux/files/home/synthnet',\n  analysis_timestamp: new Date().toISOString(),\n  testing_requirements: {\n    population_size: 50,\n    generations: 20,\n    mutation_rate: 0.1\n  }\n};"
                }
            },
            {
                "id": "evolutionary_test_generation",
                "type": "HTTP Request",
                "typeVersion": 2,
                "position": [500, 100],
                "name": "Generate Evolutionary Tests",
                "parameters": {
                    "url": "http://localhost:8770/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "generate_evolutionary_tests",
                                "arguments": {
                                    "project_path": "={{ $json.project_path }}",
                                    "requirements": "={{ $json.testing_requirements }}"
                                }
                            }
                        }
                    }
                }
            },
            {
                "id": "defect_prediction",
                "type": "HTTP Request",
                "typeVersion": 2,
                "position": [500, 250],
                "name": "Predict Defects",
                "parameters": {
                    "url": "http://localhost:8770/mcp",
                    "method": "POST", 
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "predict_defects",
                                "arguments": {
                                    "project_path": "={{ $json.project_path }}"
                                }
                            }
                        }
                    }
                }
            },
            {
                "id": "sentient_execution",
                "type": "HTTP Request",
                "typeVersion": 2,
                "position": [700, 175],
                "name": "Execute Sentient Testing",
                "parameters": {
                    "url": "http://localhost:8770/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "execute_sentient_testing",
                                "arguments": {
                                    "project_path": "={{ $('project_analysis').item.json.project_path }}",
                                    "test_config": {
                                        "test_suite": "={{ $('evolutionary_test_generation').item.json.test_suite }}",
                                        "defect_predictions": "={{ $('defect_prediction').item.json }}"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ]
        
        connections = {
            "cron_trigger": {
                "main": [
                    [
                        {
                            "node": "project_analysis",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "project_analysis": {
                "main": [
                    [
                        {
                            "node": "evolutionary_test_generation",
                            "type": "main",
                            "index": 0
                        },
                        {
                            "node": "defect_prediction",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "evolutionary_test_generation": {
                "main": [
                    [
                        {
                            "node": "sentient_execution",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "defect_prediction": {
                "main": [
                    [
                        {
                            "node": "sentient_execution",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
        
        return WorkflowTemplate(
            template_id="sentient_testing_automation",
            name="Sentient Testing Ecosystem Automation",
            description="Automated testing with evolutionary algorithms and defect prediction",
            domain="software_testing",
            complexity_level="enterprise",
            nodes=nodes,
            connections=connections,
            variables={
                "testing_schedule": "every_4_hours",
                "evolutionary_enabled": True,
                "self_healing": True
            },
            semantic_requirements={
                "test_evolution": True,
                "defect_correlation": True,
                "adaptive_execution": True
            }
        )
        
    def _create_architecture_intelligence_template(self) -> WorkflowTemplate:
        """Create architecture intelligence workflow template"""
        
        nodes = [
            {
                "id": "webhook_trigger",
                "type": "Webhook",
                "typeVersion": 1,
                "position": [100, 100],
                "name": "Architecture Analysis Request",
                "parameters": {
                    "path": "architecture-analysis",
                    "httpMethod": "POST"
                }
            },
            {
                "id": "architecture_analysis",
                "type": "HTTP Request",
                "typeVersion": 2,
                "position": [300, 100],
                "name": "Analyze Architecture",
                "parameters": {
                    "url": "http://localhost:8769/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "analyze_architecture",
                                "arguments": {
                                    "project_path": "={{ $json.project_path }}"
                                }
                            }
                        }
                    }
                }
            },
            {
                "id": "if_evolution_needed",
                "type": "If", 
                "typeVersion": 1,
                "position": [500, 100],
                "name": "Evolution Needed?",
                "parameters": {
                    "conditions": {
                        "number": [
                            {
                                "value1": "={{ $json.architecture_dna.fitness_score }}",
                                "operation": "smaller",
                                "value2": 0.8
                            }
                        ]
                    }
                }
            },
            {
                "id": "evolve_architecture",
                "type": "HTTP Request", 
                "typeVersion": 2,
                "position": [700, 50],
                "name": "Evolve Architecture",
                "parameters": {
                    "url": "http://localhost:8769/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "evolve_architecture",
                                "arguments": {
                                    "project_path": "={{ $('webhook_trigger').item.json.project_path }}",
                                    "feedback": {
                                        "performance": 0.7,
                                        "maintainability": 0.6,
                                        "scalability": 0.8
                                    }
                                }
                            }
                        }
                    }
                }
            },
            {
                "id": "pattern_recommendations",
                "type": "HTTP Request",
                "typeVersion": 2, 
                "position": [700, 150],
                "name": "Get Pattern Recommendations",
                "parameters": {
                    "url": "http://localhost:8769/mcp",
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": {
                            "method": "tools/call",
                            "params": {
                                "name": "get_pattern_recommendations",
                                "arguments": {
                                    "project_path": "={{ $('webhook_trigger').item.json.project_path }}"
                                }
                            }
                        }
                    }
                }
            }
        ]
        
        connections = {
            "webhook_trigger": {
                "main": [
                    [
                        {
                            "node": "architecture_analysis",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "architecture_analysis": {
                "main": [
                    [
                        {
                            "node": "if_evolution_needed",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "if_evolution_needed": {
                "main": [
                    [
                        {
                            "node": "evolve_architecture",
                            "type": "main",
                            "index": 0
                        }
                    ],
                    [
                        {
                            "node": "pattern_recommendations",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
        
        return WorkflowTemplate(
            template_id="architecture_intelligence_analysis",
            name="Architecture Intelligence Analysis",
            description="Intelligent architecture analysis with SCAMPER, TRIZ, and genetic evolution",
            domain="software_architecture",
            complexity_level="enterprise", 
            nodes=nodes,
            connections=connections,
            variables={
                "fitness_threshold": 0.8,
                "evolution_enabled": True,
                "pattern_analysis": "comprehensive"
            },
            semantic_requirements={
                "architecture_dna": True,
                "pattern_evolution": True,
                "six_thinking_hats": True
            }
        )
        
    def generate_workflow_json(self, template_id: str, custom_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate n8n workflow JSON from template"""
        
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
            
        template = self.templates[template_id]
        
        # Generate workflow JSON
        workflow_json = {
            "name": template.name,
            "active": True,
            "nodes": template.nodes.copy(),
            "connections": template.connections.copy(),
            "variables": template.variables.copy(),
            "settings": {
                "saveExecutionProgress": True,
                "saveDataErrorExecution": "all",
                "saveDataSuccessExecution": "all",
                "saveManualExecutions": True,
                "callerPolicy": "workflowsFromSameOwner"
            },
            "staticData": None,
            "meta": {
                "templateCredit": "SynthNet MCP Ecosystem",
                "description": template.description,
                "domain": template.domain,
                "complexity_level": template.complexity_level,
                "semantic_requirements": template.semantic_requirements,
                "generated_at": datetime.now().isoformat()
            }
        }
        
        # Apply custom parameters
        if custom_parameters:
            self._apply_custom_parameters(workflow_json, custom_parameters)
            
        return workflow_json
        
    def _apply_custom_parameters(self, workflow_json: Dict[str, Any], custom_parameters: Dict[str, Any]):
        """Apply custom parameters to workflow JSON"""
        
        # Update variables
        if "variables" in custom_parameters:
            workflow_json["variables"].update(custom_parameters["variables"])
            
        # Update node parameters  
        if "node_parameters" in custom_parameters:
            node_params = custom_parameters["node_parameters"]
            for node in workflow_json["nodes"]:
                if node["id"] in node_params:
                    node["parameters"].update(node_params[node["id"]])
                    
        # Update workflow settings
        if "settings" in custom_parameters:
            workflow_json["settings"].update(custom_parameters["settings"])
            
    def export_all_templates(self, output_dir: str = "/data/data/com.termux/files/home/synthnet/n8n_templates"):
        """Export all templates as JSON files"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for template_id, template in self.templates.items():
            workflow_json = self.generate_workflow_json(template_id)
            
            output_file = os.path.join(output_dir, f"{template_id}.json")
            with open(output_file, 'w') as f:
                json.dump(workflow_json, f, indent=2)
                
            logger.info(f"Exported template {template_id} to {output_file}")
            
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        
        template_list = []
        for template_id, template in self.templates.items():
            template_info = {
                "template_id": template_id,
                "name": template.name,
                "description": template.description, 
                "domain": template.domain,
                "complexity_level": template.complexity_level,
                "node_count": len(template.nodes),
                "semantic_requirements": template.semantic_requirements
            }
            template_list.append(template_info)
            
        return template_list

def main():
    """Main function for workflow generation"""
    generator = N8NWorkflowGenerator()
    
    print("🌐 n8n Workflow Generator with Semantic CoT Integration")
    print("=" * 60)
    
    # List available templates
    templates = generator.list_templates()
    print(f"\n📋 Available Templates ({len(templates)}):")
    for template in templates:
        print(f"  • {template['template_id']}")
        print(f"    Name: {template['name']}")
        print(f"    Domain: {template['domain']} | Complexity: {template['complexity_level']}")
        print(f"    Nodes: {template['node_count']} | Semantic: {bool(template['semantic_requirements'])}")
        print()
    
    # Export all templates
    print("📦 Exporting all templates...")
    generator.export_all_templates()
    
    print("✅ Workflow generation complete!")
    print("🚀 Templates ready for n8n deployment")

if __name__ == "__main__":
    main()