#!/usr/bin/env python3
"""
Test suite for MCP Gap Analyzer
Tests the ecosystem analysis and gap identification functionality.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from analyzers.gap_analyzer import GapAnalyzer, ServerInfo, GapOpportunity

class TestServerInfo:
    """Test ServerInfo dataclass functionality."""
    
    def test_server_info_creation(self):
        """Test basic server info creation."""
        server = ServerInfo(
            name="test-server",
            description="Test server description",
            category="api",
            capabilities=["tools", "resources"],
            language="python",
            stars=100
        )
        
        assert server.name == "test-server"
        assert server.description == "Test server description"
        assert server.category == "api"
        assert server.capabilities == ["tools", "resources"]
        assert server.language == "python"
        assert server.stars == 100
    
    def test_server_info_with_optional_fields(self):
        """Test server info with optional fields."""
        server = ServerInfo(
            name="test-server",
            description="Test description",
            category="database",
            capabilities=["tools"],
            language="typescript",
            stars=50,
            last_updated="2024-01-15",
            repository_url="https://github.com/test/test-server",
            tags=["database", "sql"]
        )
        
        assert server.last_updated == "2024-01-15"
        assert server.repository_url == "https://github.com/test/test-server"
        assert server.tags == ["database", "sql"]

class TestGapOpportunity:
    """Test GapOpportunity dataclass functionality."""
    
    def test_gap_opportunity_creation(self):
        """Test basic gap opportunity creation."""
        opportunity = GapOpportunity(
            name="healthcare-server",
            description="Healthcare integration server",
            category="healthcare",
            priority="high",
            market_size="large",
            technical_complexity="medium",
            use_cases=["patient data", "clinical records"],
            target_industries=["Healthcare", "Medical Research"],
            competition_level="low",
            estimated_effort="4-6 weeks",
            potential_impact="high"
        )
        
        assert opportunity.name == "healthcare-server"
        assert opportunity.category == "healthcare"
        assert opportunity.priority == "high"
        assert opportunity.market_size == "large"
        assert len(opportunity.use_cases) == 2
        assert len(opportunity.target_industries) == 2
    
    def test_gap_opportunity_with_suggestions(self):
        """Test gap opportunity with suggested implementations."""
        opportunity = GapOpportunity(
            name="iot-server",
            description="IoT device management",
            category="iot",
            priority="medium",
            market_size="large",
            technical_complexity="high",
            use_cases=["device control"],
            target_industries=["Smart Home"],
            competition_level="medium",
            estimated_effort="6-8 weeks",
            potential_impact="medium",
            suggested_tools=["control-device", "read-sensors"],
            suggested_resources=["device-registry"],
            required_integrations=["AWS IoT", "Google Cloud IoT"]
        )
        
        assert len(opportunity.suggested_tools) == 2
        assert len(opportunity.suggested_resources) == 1
        assert len(opportunity.required_integrations) == 2

class TestGapAnalyzer:
    """Test GapAnalyzer functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a GapAnalyzer instance for testing."""
        return GapAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer is not None
        assert analyzer.existing_servers is not None
        assert analyzer.industry_requirements is not None
        assert analyzer.technology_trends is not None
    
    def test_load_existing_servers(self, analyzer):
        """Test loading of existing server data."""
        servers = analyzer.existing_servers
        
        assert len(servers) > 0
        
        # Check for some expected servers
        server_names = [s.name for s in servers]
        assert "aws-mcp-server" in server_names
        assert "postgresql-mcp-server" in server_names
        assert "github-mcp-server" in server_names
        
        # Check server structure
        aws_server = next(s for s in servers if s.name == "aws-mcp-server")
        assert aws_server.category == "cloud"
        assert "tools" in aws_server.capabilities
        assert aws_server.language in ["python", "typescript"]
    
    def test_load_industry_requirements(self, analyzer):
        """Test loading of industry requirements."""
        industries = analyzer.industry_requirements
        
        assert "healthcare" in industries
        assert "education" in industries
        assert "legal" in industries
        assert "manufacturing" in industries
        
        # Check healthcare structure
        healthcare = industries["healthcare"]
        assert "priority" in healthcare
        assert "market_size" in healthcare
        assert "key_systems" in healthcare
        assert "use_cases" in healthcare
        assert "pain_points" in healthcare
        
        # Validate content
        assert healthcare["priority"] == "high"
        assert "FHIR" in healthcare["key_systems"]
        assert len(healthcare["use_cases"]) > 0
    
    def test_load_technology_trends(self, analyzer):
        """Test loading of technology trends."""
        trends = analyzer.technology_trends
        
        assert "blockchain" in trends
        assert "iot" in trends
        assert "ar_vr" in trends
        assert "edge_computing" in trends
        
        # Check blockchain structure
        blockchain = trends["blockchain"]
        assert "maturity" in blockchain
        assert "adoption_rate" in blockchain
        assert "key_platforms" in blockchain
        assert "use_cases" in blockchain
        
        # Validate content
        assert len(blockchain["key_platforms"]) > 0
        assert len(blockchain["use_cases"]) > 0
    
    def test_identify_opportunities(self, analyzer):
        """Test opportunity identification."""
        opportunities = analyzer.identify_opportunities()
        
        assert len(opportunities) > 0
        
        # Check that opportunities are sorted by priority
        high_priority = [o for o in opportunities if o.priority == "high"]
        assert len(high_priority) > 0
        
        # Check for expected high-priority opportunities
        opportunity_names = [o.name for o in opportunities]
        assert "healthcare-fhir-server" in opportunity_names
        assert "education-lms-server" in opportunity_names
        
        # Validate opportunity structure
        healthcare_opp = next(o for o in opportunities if o.name == "healthcare-fhir-server")
        assert healthcare_opp.category == "healthcare"
        assert healthcare_opp.priority == "high"
        assert healthcare_opp.market_size == "very_large"
        assert len(healthcare_opp.use_cases) > 0
        assert len(healthcare_opp.target_industries) > 0
    
    def test_analyze_industry_gaps(self, analyzer):
        """Test industry-specific gap analysis."""
        gaps = analyzer._analyze_industry_gaps()
        
        assert len(gaps) > 0
        
        # Check for healthcare gaps
        healthcare_gaps = [g for g in gaps if g.category == "healthcare"]
        assert len(healthcare_gaps) > 0
        
        healthcare_gap = healthcare_gaps[0]
        assert healthcare_gap.priority in ["high", "medium", "low"]
        assert healthcare_gap.market_size in ["very_large", "large", "medium", "small", "very_small"]
        assert len(healthcare_gap.use_cases) > 0
        assert len(healthcare_gap.suggested_tools) > 0
    
    def test_analyze_technology_gaps(self, analyzer):
        """Test technology-specific gap analysis."""
        gaps = analyzer._analyze_technology_gaps()
        
        assert len(gaps) > 0
        
        # Check for IoT gaps
        iot_gaps = [g for g in gaps if g.category == "iot"]
        assert len(iot_gaps) > 0
        
        iot_gap = iot_gaps[0]
        assert iot_gap.name == "iot-device-server"
        assert iot_gap.technical_complexity in ["low", "medium", "high"]
        assert len(iot_gap.required_integrations) > 0
    
    def test_analyze_integration_gaps(self, analyzer):
        """Test integration-specific gap analysis."""
        gaps = analyzer._analyze_integration_gaps()
        
        assert len(gaps) > 0
        
        # Should find social media and video conferencing gaps
        gap_categories = [g.category for g in gaps]
        assert "social_media" in gap_categories or "communication" in gap_categories
    
    def test_analyze_regional_gaps(self, analyzer):
        """Test regional/international gap analysis."""
        gaps = analyzer._analyze_regional_gaps()
        
        assert len(gaps) > 0
        
        # Should identify international e-commerce opportunities
        ecommerce_gaps = [g for g in gaps if g.category == "ecommerce"]
        assert len(ecommerce_gaps) > 0
        
        ecommerce_gap = ecommerce_gaps[0]
        assert "international" in ecommerce_gap.name.lower()
        assert len(ecommerce_gap.use_cases) > 0
    
    def test_generate_gap_report(self, analyzer):
        """Test gap analysis report generation."""
        opportunities = analyzer.identify_opportunities()
        report = analyzer.generate_gap_report(opportunities)
        
        assert isinstance(report, str)
        assert len(report) > 0
        
        # Check for essential sections
        assert "# MCP Ecosystem Gap Analysis Report" in report
        assert "## Executive Summary" in report
        assert "## Key Findings" in report
        assert "## Detailed Opportunities" in report
        assert "## Recommendations" in report
        
        # Check for content
        assert "High Priority Opportunities" in report
        assert "healthcare-fhir-server" in report
        assert "education-lms-server" in report
    
    def test_get_server_suggestions_for_industry(self, analyzer):
        """Test getting server suggestions for specific industry."""
        healthcare_servers = analyzer.get_server_suggestions_for_industry("healthcare")
        
        assert len(healthcare_servers) > 0
        
        # All suggestions should target healthcare industry
        for server in healthcare_servers:
            assert any("healthcare" in industry.lower() for industry in server.target_industries)
    
    def test_analyze_competition(self, analyzer):
        """Test competition analysis for potential servers."""
        # Test competition analysis for a server type with existing competitors
        competition = analyzer.analyze_competition("database-server")
        
        assert "direct_competitors" in competition
        assert "competitor_details" in competition
        assert "competition_level" in competition
        assert "market_opportunity" in competition
        
        assert isinstance(competition["direct_competitors"], int)
        assert competition["competition_level"] in ["low", "medium", "high"]
        assert competition["market_opportunity"] in ["low", "medium", "high"]
        
        # Test for a unique server type
        unique_competition = analyzer.analyze_competition("unique-healthcare-fhir-server")
        assert unique_competition["direct_competitors"] == 0
        assert unique_competition["competition_level"] == "low"
        assert unique_competition["market_opportunity"] == "high"

class TestReportGeneration:
    """Test report generation functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer with mock data."""
        return GapAnalyzer()
    
    def test_report_structure(self, analyzer):
        """Test that generated reports have proper structure."""
        opportunities = analyzer.identify_opportunities()[:5]  # Limit to first 5 for testing
        report = analyzer.generate_gap_report(opportunities)
        
        # Check markdown structure
        lines = report.split('\n')
        
        # Should have main title
        title_lines = [line for line in lines if line.startswith('# ')]
        assert len(title_lines) >= 1
        
        # Should have section headers
        section_headers = [line for line in lines if line.startswith('## ')]
        assert len(section_headers) >= 3
        
        # Should have opportunity details
        opportunity_headers = [line for line in lines if line.startswith('### ')]
        assert len(opportunity_headers) >= len(opportunities)
    
    def test_report_content_accuracy(self, analyzer):
        """Test that report content accurately reflects opportunities."""
        # Create specific opportunities for testing
        test_opportunities = [
            GapOpportunity(
                name="test-server-1",
                description="Test server 1",
                category="test_category",
                priority="high",
                market_size="large",
                technical_complexity="medium",
                use_cases=["test use case 1", "test use case 2"],
                target_industries=["Test Industry"],
                competition_level="low",
                estimated_effort="4 weeks",
                potential_impact="high"
            ),
            GapOpportunity(
                name="test-server-2",
                description="Test server 2",
                category="test_category",
                priority="medium",
                market_size="medium",
                technical_complexity="high",
                use_cases=["test use case 3"],
                target_industries=["Another Industry"],
                competition_level="medium",
                estimated_effort="8 weeks",
                potential_impact="medium"
            )
        ]
        
        report = analyzer.generate_gap_report(test_opportunities)
        
        # Check that all test opportunities are mentioned
        assert "test-server-1" in report
        assert "test-server-2" in report
        assert "Test server 1" in report
        assert "Test server 2" in report
        
        # Check priority distribution
        assert "High Priority Opportunities (1)" in report  # 1 high priority
        
        # Check category breakdown
        assert "test_category: 2 opportunities" in report

class TestDataValidation:
    """Test data validation and consistency."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer for validation testing."""
        return GapAnalyzer()
    
    def test_server_data_consistency(self, analyzer):
        """Test that server data is consistent and valid."""
        servers = analyzer.existing_servers
        
        for server in servers:
            # Check required fields
            assert server.name is not None and server.name != ""
            assert server.description is not None and server.description != ""
            assert server.category is not None and server.category != ""
            assert isinstance(server.capabilities, list)
            assert server.language in ["python", "typescript", "javascript", "rust", "go"]
            assert isinstance(server.stars, int) and server.stars >= 0
    
    def test_industry_data_consistency(self, analyzer):
        """Test that industry data is consistent and valid."""
        industries = analyzer.industry_requirements
        
        for industry_name, industry_data in industries.items():
            assert "priority" in industry_data
            assert industry_data["priority"] in ["high", "medium", "low"]
            
            assert "market_size" in industry_data
            assert industry_data["market_size"] in ["very_large", "large", "medium", "small", "very_small"]
            
            assert "key_systems" in industry_data
            assert isinstance(industry_data["key_systems"], list)
            assert len(industry_data["key_systems"]) > 0
            
            assert "use_cases" in industry_data
            assert isinstance(industry_data["use_cases"], list)
            assert len(industry_data["use_cases"]) > 0
    
    def test_technology_data_consistency(self, analyzer):
        """Test that technology trend data is consistent."""
        trends = analyzer.technology_trends
        
        for tech_name, tech_data in trends.items():
            assert "maturity" in tech_data
            assert tech_data["maturity"] in ["emerging", "growing", "mature", "declining"]
            
            assert "adoption_rate" in tech_data
            assert tech_data["adoption_rate"] in ["low", "medium", "high"]
            
            assert "key_platforms" in tech_data
            assert isinstance(tech_data["key_platforms"], list)
            
            assert "use_cases" in tech_data
            assert isinstance(tech_data["use_cases"], list)
    
    def test_opportunity_data_validation(self, analyzer):
        """Test that generated opportunities have valid data."""
        opportunities = analyzer.identify_opportunities()
        
        for opportunity in opportunities:
            # Check required fields
            assert opportunity.name is not None and opportunity.name != ""
            assert opportunity.description is not None and opportunity.description != ""
            assert opportunity.category is not None and opportunity.category != ""
            
            # Check enum fields
            assert opportunity.priority in ["high", "medium", "low"]
            assert opportunity.market_size in ["very_large", "large", "medium", "small", "very_small"]
            assert opportunity.technical_complexity in ["low", "medium", "high"]
            assert opportunity.competition_level in ["low", "medium", "high"]
            assert opportunity.potential_impact in ["very_high", "high", "medium", "low"]
            
            # Check list fields
            assert isinstance(opportunity.use_cases, list)
            assert len(opportunity.use_cases) > 0
            assert isinstance(opportunity.target_industries, list)
            assert len(opportunity.target_industries) > 0
            
            # Check that effort estimation follows expected format
            assert "week" in opportunity.estimated_effort.lower() or "month" in opportunity.estimated_effort.lower()

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])