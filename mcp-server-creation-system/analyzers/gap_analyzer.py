#!/usr/bin/env python3
"""
MCP Ecosystem Gap Analysis Engine
Identifies opportunities for new MCP servers based on ecosystem analysis.
"""

import json
import yaml
from typing import Dict, List, Any, Set, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging
from datetime import datetime
import requests
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ServerInfo:
    """Information about an existing MCP server."""
    name: str
    description: str
    category: str
    capabilities: List[str]
    language: str
    stars: int = 0
    last_updated: Optional[str] = None
    repository_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class GapOpportunity:
    """Represents a gap in the MCP ecosystem."""
    name: str
    description: str
    category: str
    priority: str  # 'high', 'medium', 'low'
    market_size: str
    technical_complexity: str
    use_cases: List[str]
    target_industries: List[str]
    competition_level: str
    estimated_effort: str
    potential_impact: str
    suggested_tools: List[str] = field(default_factory=list)
    suggested_resources: List[str] = field(default_factory=list)
    required_integrations: List[str] = field(default_factory=list)

class GapAnalyzer:
    """Analyzes the MCP ecosystem to identify gaps and opportunities."""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = Path(data_dir) if data_dir else self.base_dir / "analyzers" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing ecosystem data
        self.existing_servers = self.load_existing_servers()
        self.industry_requirements = self.load_industry_requirements()
        self.technology_trends = self.load_technology_trends()
    
    def load_existing_servers(self) -> List[ServerInfo]:
        """Load information about existing MCP servers."""
        # This would ideally fetch from the official MCP registry or GitHub
        # For now, we'll use a comprehensive list based on research
        return [
            # Cloud & Infrastructure
            ServerInfo("aws-mcp-server", "Amazon Web Services integration", "cloud", ["tools", "resources"], "typescript", 150),
            ServerInfo("gcp-mcp-server", "Google Cloud Platform integration", "cloud", ["tools", "resources"], "python", 120),
            ServerInfo("azure-mcp-server", "Microsoft Azure integration", "cloud", ["tools", "resources"], "python", 90),
            ServerInfo("kubernetes-mcp-server", "Kubernetes cluster management", "infrastructure", ["tools", "resources"], "python", 80),
            ServerInfo("docker-mcp-server", "Docker container management", "infrastructure", ["tools"], "python", 70),
            ServerInfo("terraform-mcp-server", "Infrastructure as Code", "infrastructure", ["tools", "resources"], "python", 60),
            
            # Databases & Data
            ServerInfo("postgresql-mcp-server", "PostgreSQL database integration", "database", ["tools", "resources"], "python", 200),
            ServerInfo("mysql-mcp-server", "MySQL database integration", "database", ["tools", "resources"], "python", 150),
            ServerInfo("mongodb-mcp-server", "MongoDB integration", "database", ["tools", "resources"], "python", 130),
            ServerInfo("redis-mcp-server", "Redis cache integration", "database", ["tools", "resources"], "python", 100),
            ServerInfo("elasticsearch-mcp-server", "Elasticsearch integration", "database", ["tools", "resources"], "python", 85),
            ServerInfo("neo4j-mcp-server", "Neo4j graph database", "database", ["tools", "resources"], "python", 70),
            ServerInfo("chroma-mcp-server", "Chroma vector database", "database", ["tools", "resources"], "python", 90),
            ServerInfo("pinecone-mcp-server", "Pinecone vector database", "database", ["tools", "resources"], "python", 85),
            
            # Development & DevOps
            ServerInfo("github-mcp-server", "GitHub integration", "development", ["tools", "resources"], "typescript", 300),
            ServerInfo("gitlab-mcp-server", "GitLab integration", "development", ["tools", "resources"], "python", 150),
            ServerInfo("circleci-mcp-server", "CircleCI integration", "development", ["tools"], "python", 80),
            ServerInfo("jenkins-mcp-server", "Jenkins CI/CD", "development", ["tools", "resources"], "python", 75),
            ServerInfo("sonarqube-mcp-server", "Code quality analysis", "development", ["tools", "resources"], "python", 60),
            ServerInfo("jira-mcp-server", "Atlassian Jira integration", "development", ["tools", "resources"], "python", 120),
            
            # AI & ML
            ServerInfo("openai-mcp-server", "OpenAI API integration", "ai", ["tools", "prompts"], "python", 250),
            ServerInfo("anthropic-mcp-server", "Anthropic Claude integration", "ai", ["tools", "prompts"], "python", 200),
            ServerInfo("huggingface-mcp-server", "Hugging Face integration", "ai", ["tools", "resources"], "python", 180),
            ServerInfo("langchain-mcp-server", "LangChain integration", "ai", ["tools", "prompts"], "python", 160),
            ServerInfo("zenml-mcp-server", "ZenML MLOps platform", "ai", ["tools", "resources"], "python", 70),
            ServerInfo("langfuse-mcp-server", "LLM observability", "ai", ["tools", "resources"], "python", 90),
            
            # Business & Productivity
            ServerInfo("notion-mcp-server", "Notion workspace integration", "productivity", ["tools", "resources"], "python", 180),
            ServerInfo("slack-mcp-server", "Slack messaging platform", "productivity", ["tools", "resources"], "python", 200),
            ServerInfo("discord-mcp-server", "Discord integration", "productivity", ["tools"], "python", 120),
            ServerInfo("taskade-mcp-server", "Taskade project management", "productivity", ["tools", "resources"], "python", 60),
            ServerInfo("trello-mcp-server", "Trello boards", "productivity", ["tools", "resources"], "python", 80),
            ServerInfo("asana-mcp-server", "Asana project management", "productivity", ["tools", "resources"], "python", 70),
            
            # Finance & Payments
            ServerInfo("stripe-mcp-server", "Stripe payments", "finance", ["tools", "resources"], "python", 140),
            ServerInfo("paypal-mcp-server", "PayPal integration", "finance", ["tools", "resources"], "python", 100),
            ServerInfo("quickbooks-mcp-server", "QuickBooks accounting", "finance", ["tools", "resources"], "python", 80),
            ServerInfo("coingecko-mcp-server", "Cryptocurrency data", "finance", ["tools", "resources"], "python", 90),
            
            # Web & Content
            ServerInfo("webscraping-ai-mcp-server", "Web scraping service", "web", ["tools"], "python", 110),
            ServerInfo("contentful-mcp-server", "Contentful CMS", "web", ["tools", "resources"], "python", 85),
            ServerInfo("wordpress-mcp-server", "WordPress integration", "web", ["tools", "resources"], "python", 95),
            ServerInfo("kagi-mcp-server", "Kagi search engine", "web", ["tools"], "python", 70),
        ]
    
    def load_industry_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load industry-specific requirements and pain points."""
        return {
            "healthcare": {
                "priority": "high",
                "market_size": "very_large",
                "compliance_requirements": ["HIPAA", "GDPR", "FDA"],
                "key_systems": ["EHR", "FHIR", "HL7", "DICOM", "Epic", "Cerner"],
                "use_cases": [
                    "Patient data integration",
                    "Clinical decision support",
                    "Medical imaging analysis",
                    "Drug interaction checking",
                    "Appointment scheduling",
                    "Insurance verification",
                    "Clinical research data"
                ],
                "pain_points": [
                    "Data silos between systems",
                    "Complex integration requirements",
                    "Strict compliance needs",
                    "Legacy system compatibility"
                ]
            },
            "education": {
                "priority": "high",
                "market_size": "large",
                "key_systems": ["LMS", "SIS", "Canvas", "Blackboard", "Moodle", "Google Classroom"],
                "use_cases": [
                    "Student information systems",
                    "Learning management integration",
                    "Grade book management",
                    "Assignment submission",
                    "Virtual classroom tools",
                    "Educational content delivery",
                    "Student performance analytics"
                ],
                "pain_points": [
                    "Fragmented educational tools",
                    "Data portability issues",
                    "Limited API standardization",
                    "Budget constraints"
                ]
            },
            "legal": {
                "priority": "high",
                "market_size": "large",
                "compliance_requirements": ["Attorney-client privilege", "Data retention"],
                "key_systems": ["Westlaw", "LexisNexis", "Thomson Reuters", "Clio", "MyCase"],
                "use_cases": [
                    "Legal research automation",
                    "Case law analysis",
                    "Contract review",
                    "Document discovery",
                    "Billing and time tracking",
                    "Client communication",
                    "Regulatory compliance monitoring"
                ],
                "pain_points": [
                    "Manual research processes",
                    "Document review inefficiency",
                    "High subscription costs",
                    "Integration complexity"
                ]
            },
            "manufacturing": {
                "priority": "medium",
                "market_size": "very_large",
                "key_systems": ["ERP", "MES", "SAP", "Oracle", "PLM", "SCADA"],
                "use_cases": [
                    "Production planning",
                    "Supply chain management",
                    "Quality control",
                    "Equipment maintenance",
                    "Inventory management",
                    "Compliance reporting",
                    "IoT device integration"
                ],
                "pain_points": [
                    "Legacy system integration",
                    "Real-time data needs",
                    "Complex workflows",
                    "Downtime costs"
                ]
            },
            "real_estate": {
                "priority": "medium",
                "market_size": "large",
                "key_systems": ["MLS", "CRM", "Zillow", "Realtor.com", "DocuSign"],
                "use_cases": [
                    "Property listing management",
                    "Market analysis",
                    "Document signing",
                    "Client relationship management",
                    "Property valuation",
                    "Transaction management",
                    "Lead generation"
                ],
                "pain_points": [
                    "Fragmented data sources",
                    "Manual data entry",
                    "Complex transaction processes",
                    "Regulatory compliance"
                ]
            },
            "retail": {
                "priority": "medium",
                "market_size": "very_large",
                "key_systems": ["POS", "E-commerce", "Inventory", "Shopify", "WooCommerce"],
                "use_cases": [
                    "Inventory management",
                    "Customer analytics",
                    "Order processing",
                    "Payment processing",
                    "Supply chain coordination",
                    "Marketing automation",
                    "Fraud detection"
                ],
                "pain_points": [
                    "Omnichannel complexity",
                    "Inventory synchronization",
                    "Customer data fragmentation",
                    "Seasonal demand fluctuation"
                ]
            }
        }
    
    def load_technology_trends(self) -> Dict[str, Dict[str, Any]]:
        """Load current technology trends and emerging technologies."""
        return {
            "blockchain": {
                "maturity": "growing",
                "adoption_rate": "medium",
                "key_platforms": ["Ethereum", "Bitcoin", "Polygon", "Solana", "Chainlink"],
                "use_cases": [
                    "DeFi protocol integration",
                    "NFT marketplace data",
                    "Smart contract interaction", 
                    "Cryptocurrency analytics",
                    "Blockchain data indexing"
                ]
            },
            "iot": {
                "maturity": "mature",
                "adoption_rate": "high",
                "key_platforms": ["AWS IoT", "Azure IoT", "Google Cloud IoT", "ThingWorx"],
                "use_cases": [
                    "Device management",
                    "Sensor data collection",
                    "Remote monitoring",
                    "Predictive maintenance",
                    "Smart home automation"
                ]
            },
            "ar_vr": {
                "maturity": "emerging",
                "adoption_rate": "low",
                "key_platforms": ["Unity", "Unreal Engine", "ARKit", "ARCore", "WebXR"],
                "use_cases": [
                    "3D content management",
                    "Virtual collaboration",
                    "Training simulations",
                    "Product visualization",
                    "Remote assistance"
                ]
            },
            "edge_computing": {
                "maturity": "growing",
                "adoption_rate": "medium",
                "key_platforms": ["AWS Greengrass", "Azure IoT Edge", "NVIDIA Jetson"],
                "use_cases": [
                    "Local data processing",
                    "Real-time analytics",
                    "Offline operation",
                    "Latency optimization",
                    "Edge AI deployment"
                ]
            }
        }
    
    def identify_opportunities(self) -> List[GapOpportunity]:
        """Identify gaps and opportunities in the MCP ecosystem."""
        opportunities = []
        
        # Analyze industry gaps
        opportunities.extend(self._analyze_industry_gaps())
        
        # Analyze technology gaps
        opportunities.extend(self._analyze_technology_gaps())
        
        # Analyze integration gaps
        opportunities.extend(self._analyze_integration_gaps())
        
        # Analyze regional/language gaps
        opportunities.extend(self._analyze_regional_gaps())
        
        # Sort by priority and potential impact
        opportunities.sort(key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}[x.priority],
            {"very_large": 5, "large": 4, "medium": 3, "small": 2, "very_small": 1}[x.market_size]
        ), reverse=True)
        
        return opportunities
    
    def _analyze_industry_gaps(self) -> List[GapOpportunity]:
        """Analyze gaps in industry-specific integrations."""
        gaps = []
        
        # Healthcare FHIR Integration
        gaps.append(GapOpportunity(
            name="healthcare-fhir-server",
            description="FHIR (Fast Healthcare Interoperability Resources) integration server for healthcare data exchange",
            category="healthcare",
            priority="high",
            market_size="very_large",
            technical_complexity="high",
            use_cases=[
                "Patient data retrieval from EHR systems",
                "Clinical decision support integration",
                "Healthcare analytics and reporting",
                "Interoperability between healthcare systems",
                "Telemedicine data exchange"
            ],
            target_industries=["Healthcare", "Medical Research", "Telemedicine"],
            competition_level="low",
            estimated_effort="6-8 weeks",
            potential_impact="very_high",
            suggested_tools=[
                "search-patients",
                "get-patient-data",
                "create-observation",
                "query-conditions",
                "fetch-medications"
            ],
            suggested_resources=[
                "patient-records",
                "clinical-guidelines",
                "medication-database"
            ],
            required_integrations=["Epic", "Cerner", "Allscripts", "SMART on FHIR"]
        ))
        
        # Educational LMS Integration
        gaps.append(GapOpportunity(
            name="education-lms-server",
            description="Learning Management System integration for educational institutions",
            category="education",
            priority="high",
            market_size="large",
            technical_complexity="medium",
            use_cases=[
                "Student enrollment management",
                "Grade synchronization",
                "Course content delivery",
                "Assignment submission tracking",
                "Learning analytics"
            ],
            target_industries=["Education", "Corporate Training", "Online Learning"],
            competition_level="low",
            estimated_effort="4-6 weeks",
            potential_impact="high",
            suggested_tools=[
                "enroll-student",
                "submit-assignment",
                "get-grades",
                "create-course",
                "track-progress"
            ],
            suggested_resources=[
                "course-catalog",
                "student-records",
                "assignment-templates"
            ],
            required_integrations=["Canvas", "Blackboard", "Moodle", "Google Classroom"]
        ))
        
        # Legal Research Server
        gaps.append(GapOpportunity(
            name="legal-research-server",
            description="Legal research and case law analysis integration",
            category="legal",
            priority="high",
            market_size="large",
            technical_complexity="high",
            use_cases=[
                "Case law research automation",
                "Legal document analysis",
                "Regulatory compliance monitoring",
                "Contract review assistance",
                "Legal precedent tracking"
            ],
            target_industries=["Law Firms", "Corporate Legal", "Government"],
            competition_level="medium",
            estimated_effort="6-10 weeks",
            potential_impact="high",
            suggested_tools=[
                "search-cases",
                "analyze-contract",
                "check-compliance",
                "find-precedents",
                "extract-clauses"
            ],
            suggested_resources=[
                "case-database",
                "legal-templates",
                "regulation-updates"
            ],
            required_integrations=["Westlaw", "LexisNexis", "Bloomberg Law", "Fastcase"]
        ))
        
        # Manufacturing ERP Server
        gaps.append(GapOpportunity(
            name="manufacturing-erp-server",
            description="Enterprise Resource Planning integration for manufacturing",
            category="manufacturing",
            priority="medium",
            market_size="very_large",
            technical_complexity="high",
            use_cases=[
                "Production planning optimization",
                "Supply chain coordination",
                "Quality control monitoring",
                "Equipment maintenance scheduling",
                "Inventory management"
            ],
            target_industries=["Manufacturing", "Automotive", "Aerospace", "Electronics"],
            competition_level="high",
            estimated_effort="8-12 weeks",
            potential_impact="very_high",
            suggested_tools=[
                "schedule-production",
                "track-inventory",
                "monitor-quality",
                "plan-maintenance",
                "optimize-supply-chain"
            ],
            suggested_resources=[
                "production-data",
                "quality-metrics",
                "maintenance-logs"
            ],
            required_integrations=["SAP", "Oracle ERP", "Microsoft Dynamics", "Infor"]
        ))
        
        return gaps
    
    def _analyze_technology_gaps(self) -> List[GapOpportunity]:
        """Analyze gaps in emerging technology integrations."""
        gaps = []
        
        # IoT Device Management Server
        gaps.append(GapOpportunity(
            name="iot-device-server",
            description="IoT device management and data integration server",
            category="iot",
            priority="high",
            market_size="very_large",
            technical_complexity="medium",
            use_cases=[
                "Smart home device control",
                "Industrial IoT monitoring",
                "Sensor data collection",
                "Device firmware updates",
                "Predictive maintenance"
            ],
            target_industries=["Smart Home", "Industrial IoT", "Agriculture", "Healthcare"],
            competition_level="medium",
            estimated_effort="5-7 weeks",
            potential_impact="high",
            suggested_tools=[
                "control-device",
                "read-sensors",
                "update-firmware",
                "monitor-health",
                "configure-device"
            ],
            suggested_resources=[
                "device-registry",
                "sensor-data",
                "firmware-repository"
            ],
            required_integrations=["AWS IoT", "Azure IoT Hub", "Google Cloud IoT", "ThingWorx"]
        ))
        
        # Blockchain Analytics Server
        gaps.append(GapOpportunity(
            name="blockchain-analytics-server",
            description="Blockchain data analysis and DeFi integration server",
            category="blockchain",
            priority="medium",
            market_size="large",
            technical_complexity="high",
            use_cases=[
                "DeFi protocol analysis",
                "NFT marketplace data",
                "Cryptocurrency tracking",
                "Smart contract interaction",
                "Blockchain forensics"
            ],
            target_industries=["Financial Services", "Crypto Trading", "Compliance"],
            competition_level="medium",
            estimated_effort="6-8 weeks",
            potential_impact="medium",
            suggested_tools=[
                "analyze-defi-protocol",
                "track-transactions",
                "query-smart-contract",
                "monitor-nft-sales",
                "detect-fraud"
            ],
            suggested_resources=[
                "blockchain-data",
                "defi-protocols",
                "nft-collections"
            ],
            required_integrations=["Etherscan", "The Graph", "Chainlink", "Alchemy"]
        ))
        
        # AR/VR Content Server
        gaps.append(GapOpportunity(
            name="ar-vr-content-server",
            description="Augmented and Virtual Reality content management server",
            category="ar_vr",
            priority="low",
            market_size="small",
            technical_complexity="high",
            use_cases=[
                "3D model management",
                "Virtual training content",
                "AR experience deployment",
                "Spatial computing data",
                "Mixed reality collaboration"
            ],
            target_industries=["Entertainment", "Training", "Architecture", "Retail"],
            competition_level="low",
            estimated_effort="8-10 weeks",
            potential_impact="medium",
            suggested_tools=[
                "upload-3d-model",
                "create-ar-experience",
                "manage-vr-content",
                "deploy-experience",
                "track-interactions"
            ],
            suggested_resources=[
                "3d-models",
                "ar-templates",
                "vr-environments"
            ],
            required_integrations=["Unity", "Unreal Engine", "ARKit", "ARCore"]
        ))
        
        return gaps
    
    def _analyze_integration_gaps(self) -> List[GapOpportunity]:
        """Analyze gaps in popular service integrations."""
        gaps = []
        
        # Social Media Management Server
        gaps.append(GapOpportunity(
            name="social-media-server",
            description="Social media platform integration and management server",
            category="social_media",
            priority="medium",
            market_size="large",
            technical_complexity="medium",
            use_cases=[
                "Cross-platform posting",
                "Social media analytics",
                "Content scheduling",
                "Audience engagement tracking",
                "Influencer collaboration"
            ],
            target_industries=["Marketing", "E-commerce", "Media", "Agencies"],
            competition_level="high",
            estimated_effort="4-6 weeks",
            potential_impact="medium",
            suggested_tools=[
                "post-content",
                "schedule-posts",
                "analyze-engagement",
                "monitor-mentions",
                "track-hashtags"
            ],
            suggested_resources=[
                "social-analytics",
                "content-calendar",
                "audience-insights"
            ],
            required_integrations=["Twitter API", "Facebook Graph API", "Instagram API", "LinkedIn API"]
        ))
        
        # Video Conferencing Server
        gaps.append(GapOpportunity(
            name="video-conferencing-server",
            description="Video conferencing platform integration server",
            category="communication",
            priority="medium",
            market_size="large",
            technical_complexity="medium",
            use_cases=[
                "Meeting scheduling automation",
                "Recording management",
                "Participant analytics",
                "Integration with calendars",
                "Transcription services"
            ],
            target_industries=["Business", "Education", "Healthcare", "Remote Work"],
            competition_level="medium",
            estimated_effort="4-5 weeks",
            potential_impact="medium",
            suggested_tools=[
                "schedule-meeting",
                "start-recording",
                "manage-participants",
                "get-transcription",
                "analyze-usage"
            ],
            suggested_resources=[
                "meeting-recordings",
                "transcripts",
                "usage-analytics"
            ],
            required_integrations=["Zoom API", "Microsoft Teams", "Google Meet", "WebEx"]
        ))
        
        return gaps
    
    def _analyze_regional_gaps(self) -> List[GapOpportunity]:
        """Analyze gaps in regional/international service integrations."""
        gaps = []
        
        # International E-commerce Server
        gaps.append(GapOpportunity(
            name="international-ecommerce-server",
            description="International e-commerce platform integration server",
            category="ecommerce",
            priority="medium",
            market_size="very_large",
            technical_complexity="medium",
            use_cases=[
                "Multi-currency handling",
                "International shipping",
                "Tax calculation",
                "Localization support",
                "Cross-border compliance"
            ],
            target_industries=["E-commerce", "Retail", "Import/Export"],
            competition_level="medium",
            estimated_effort="6-8 weeks",
            potential_impact="high",
            suggested_tools=[
                "calculate-shipping",
                "convert-currency",
                "check-tax-rates",
                "validate-address",
                "track-shipment"
            ],
            suggested_resources=[
                "shipping-rates",
                "tax-tables",
                "exchange-rates"
            ],
            required_integrations=["Amazon Global", "AliExpress", "eBay International", "Shopify Markets"]
        ))
        
        return gaps
    
    def generate_gap_report(self, opportunities: List[GapOpportunity]) -> str:
        """Generate a comprehensive gap analysis report."""
        report = f"""# MCP Ecosystem Gap Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report identifies {len(opportunities)} significant opportunities for new MCP servers based on comprehensive ecosystem analysis.

### Key Findings

#### High Priority Opportunities ({len([o for o in opportunities if o.priority == 'high'])})
"""
        
        high_priority = [o for o in opportunities if o.priority == 'high']
        for opp in high_priority[:5]:  # Top 5
            report += f"- **{opp.name}**: {opp.description} ({opp.category})\n"
        
        report += f"""
#### Market Size Distribution
- Very Large: {len([o for o in opportunities if o.market_size == 'very_large'])} opportunities
- Large: {len([o for o in opportunities if o.market_size == 'large'])} opportunities
- Medium: {len([o for o in opportunities if o.market_size == 'medium'])} opportunities
- Small: {len([o for o in opportunities if o.market_size == 'small'])} opportunities

#### Category Breakdown
"""
        
        categories = defaultdict(int)
        for opp in opportunities:
            categories[opp.category] += 1
        
        for category, count in sorted(categories.items()):
            report += f"- {category.title()}: {count} opportunities\n"
        
        report += "\n## Detailed Opportunities\n\n"
        
        for i, opp in enumerate(opportunities, 1):
            report += f"""### {i}. {opp.name}

**Category**: {opp.category}
**Priority**: {opp.priority}
**Market Size**: {opp.market_size}
**Technical Complexity**: {opp.technical_complexity}
**Estimated Effort**: {opp.estimated_effort}
**Potential Impact**: {opp.potential_impact}

**Description**: {opp.description}

**Target Industries**: {', '.join(opp.target_industries)}

**Key Use Cases**:
{chr(10).join(f'- {use_case}' for use_case in opp.use_cases)}

**Suggested Tools**: {', '.join(opp.suggested_tools)}
**Suggested Resources**: {', '.join(opp.suggested_resources)}
**Required Integrations**: {', '.join(opp.required_integrations)}

---

"""
        
        report += """## Recommendations

### Immediate Actions (Next 3 months)
1. Focus on high-priority, large market opportunities
2. Start with healthcare and education sectors
3. Develop foundational infrastructure for industry-specific servers

### Medium-term Goals (3-12 months)
1. Expand into emerging technologies (IoT, blockchain)
2. Build partnerships with key platform providers
3. Establish community contribution guidelines

### Long-term Vision (12+ months)
1. Create comprehensive industry-specific server suites
2. Develop automated server generation tools
3. Build ecosystem marketplace and discovery platform

### Success Metrics
- Number of new servers developed
- Adoption rates by target industries
- Developer community growth
- Integration success rates
"""
        
        return report
    
    def get_server_suggestions_for_industry(self, industry: str) -> List[GapOpportunity]:
        """Get server suggestions for a specific industry."""
        opportunities = self.identify_opportunities()
        return [opp for opp in opportunities if industry.lower() in [ind.lower() for ind in opp.target_industries]]
    
    def analyze_competition(self, server_name: str) -> Dict[str, Any]:
        """Analyze competition for a potential server."""
        existing_servers = [s for s in self.existing_servers if server_name.lower() in s.name.lower() or any(tag.lower() in server_name.lower() for tag in s.tags)]
        
        return {
            "direct_competitors": len(existing_servers),
            "competitor_details": [{"name": s.name, "stars": s.stars, "language": s.language} for s in existing_servers],
            "competition_level": "high" if len(existing_servers) > 5 else "medium" if len(existing_servers) > 2 else "low",
            "market_opportunity": "low" if len(existing_servers) > 5 else "medium" if len(existing_servers) > 2 else "high"
        }

if __name__ == "__main__":
    analyzer = GapAnalyzer()
    opportunities = analyzer.identify_opportunities()
    
    print(f"Found {len(opportunities)} opportunities:")
    for opp in opportunities[:10]:  # Show top 10
        print(f"- {opp.name} ({opp.category}) - Priority: {opp.priority}")
    
    # Generate full report
    report = analyzer.generate_gap_report(opportunities)
    output_path = Path(__file__).parent / "gap_analysis_report.md"
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nFull report saved to: {output_path}")