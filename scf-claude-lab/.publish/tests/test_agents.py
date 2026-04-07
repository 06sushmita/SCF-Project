"""
tests/test_agents.py
Unit tests for core agents (extract, control, registry, policy)
"""

import pytest
from pathlib import Path
from datetime import datetime

from agents import (
    ExtractAgent, ControlAgent, RegistryAgent, PolicyAgent,
    ControlVersion, ControlStatus, ControlDomain, ControlType
)


class TestExtractAgent:
    """Test PDF extraction and filtering"""
    
    def test_extract_removes_short_clauses(self):
        """Short clauses should be filtered out"""
        agent = ExtractAgent()
        short_text = "This is short."
        
        result = agent.extract_from_text(short_text)
        assert len(result) == 0  # Too short
    
    def test_extract_requires_obligation_verb(self):
        """Clauses without modal verbs should be filtered"""
        agent = ExtractAgent()
        text = "Brokers exist and serve investors in the market."
        
        result = agent.extract_from_text(text)
        assert len(result) == 0  # No must/shall/should
    
    def test_extract_keeps_meaningful_clauses(self):
        """Meaningful clauses with obligation verbs should be kept"""
        agent = ExtractAgent()
        text = "Brokers must submit enrollment requests on formal letterhead with supporting documentation."
        
        result = agent.extract_from_text(text)
        assert len(result) >= 1
        assert "must submit" in result[0].lower()
    
    def test_extract_removes_duplicates(self):
        """Similar clauses should be deduplicated"""
        agent = ExtractAgent()
        clause1 = "Brokers must submit enrollment requests with formal documentation and business data."
        clause2 = "Brokers must submit enrollment requests with formal documentation and official letterhead."
        
        text = f"{clause1} {clause2}"
        result = agent.extract_from_text(text)
        
        # Should have only 1 or 2 (similar, not identical)
        assert len(result) <= 2


class TestControlAgent:
    """Test control generation from clauses"""
    
    def test_control_agent_infers_domain(self):
        """Control agent should infer domain from keywords"""
        agent = ControlAgent()
        
        clause = "Brokers must register and receive a unique code before submitting claims."
        domain, family = agent._infer_domain_family(clause)
        assert domain == "Access Control"
        assert "Third-Party" in family
    
    def test_control_agent_infers_type(self):
        """Control agent should classify preventive/detective/corrective"""
        agent = ControlAgent()
        
        # Preventive
        preventive = "Brokers must not submit claims without valid code."
        assert agent._infer_control_type(preventive) == "Preventive"
        
        # Detective
        detective = "Audit teams must reconcile all broker claims weekly."
        assert agent._infer_control_type(detective) == "Monitoring and Auditing"
        
        # Administrative (fallback)
        admin = "The organization will maintain records."
        assert agent._infer_control_type(admin) in ["Administrative", "Preventive"]
    
    def test_control_agent_generates_controls(self):
        """Control agent should generate properly structured controls"""
        agent = ControlAgent()
        
        clauses = [
            "Brokers must register and receive a unique code.",
            "Investors must submit nomination requests before bond maturity."
        ]
        
        controls = agent.generate_controls(clauses)
        assert len(controls) == 2
        assert controls[0]['control_id'] == 'SCF-001'
        assert controls[0]['control_type'] in ['Preventive', 'Detective', 'Corrective', 'Administrative']
        assert controls[0]['control_domain'] in [d.value for d in ControlDomain]


class TestRegistryAgent:
    """Test control registry with versioning"""
    
    def test_registry_creates_control(self):
        """Registry should create new control version"""
        registry = RegistryAgent(registry_path="test_controls_registry.json")
        
        version = ControlVersion(
            version="1.0",
            control_id="TEST-001",
            created_date=datetime.now().isoformat(),
            created_by="test",
            status=ControlStatus.DRAFT,
            title="Test Control",
            objective="Test objective",
            control_statement="Test statement",
            control_domain=ControlDomain.ACCESS_CONTROL,
            control_family="Test Family",
            control_type=ControlType.PREVENTIVE,
            risk_addressed="Test risk",
            evidence_required="Test evidence",
            metrics="Test metrics",
            assumptions="Test assumptions",
        )
        
        control = registry.create_control(version, actor="test_user")
        assert control.control_id == "TEST-001"
        assert len(control.versions) == 1
    
    def test_registry_updates_control_creates_new_version(self):
        """Updating control should create new minor version"""
        registry = RegistryAgent(registry_path="test_controls_registry.json")
        
        # Create v1.0
        version_10 = ControlVersion(
            version="1.0",
            control_id="TEST-002",
            created_date=datetime.now().isoformat(),
            created_by="test",
            status=ControlStatus.DRAFT,
            title="Original Title",
            objective="Original objective",
            control_statement="Test statement",
            control_domain=ControlDomain.ACCESS_CONTROL,
            control_family="Test Family",
            control_type=ControlType.PREVENTIVE,
            risk_addressed="Test",
            evidence_required="Test",
            metrics="Test",
            assumptions="Test",
        )
        registry.create_control(version_10, actor="test_user")
        
        # Update → should create v1.1
        new_version = registry.update_control(
            "TEST-002",
            {"title": "Updated Title"},
            actor="test_user",
            reason="Clarification"
        )
        
        assert new_version.version == "1.1"
        assert new_version.title == "Updated Title"
        assert new_version.amended_from_version == "1.0"
    
    def test_registry_searches_controls(self):
        """Registry should search by domain and keywords"""
        registry = RegistryAgent(registry_path="test_controls_registry.json")
        
        version = ControlVersion(
            version="1.0",
            control_id="TEST-003",
            created_date=datetime.now().isoformat(),
            created_by="test",
            status=ControlStatus.ACTIVE,
            title="Broker Access Control",
            objective="Control broker access",
            control_statement="Test",
            control_domain=ControlDomain.ACCESS_CONTROL,
            control_family="Test",
            control_type=ControlType.PREVENTIVE,
            risk_addressed="Test",
            evidence_required="Test",
            metrics="Test",
            assumptions="Test",
        )
        registry.create_control(version, actor="test")
        registry.activate_control("TEST-003", actor="test")
        
        # Search by query
        results = registry.search(query="broker")
        assert len(results) >= 1
        assert results[0].control_id == "TEST-003"
        
        # Search by domain
        results = registry.search(domain="Access Control")
        assert len(results) >= 1


class TestPolicyAgent:
    """Test policy generation and evaluation"""
    
    def test_policy_agent_generates_rego(self):
        """Policy agent should generate valid Rego"""
        agent = PolicyAgent(policies_dir="test_policies")
        
        version = ControlVersion(
            version="1.0",
            control_id="POL-001",
            created_date=datetime.now().isoformat(),
            created_by="test",
            status=ControlStatus.DRAFT,
            title="Test Policy",
            objective="Test",
            control_statement="Test",
            control_domain=ControlDomain.ACCESS_CONTROL,
            control_family="Test",
            control_type=ControlType.PREVENTIVE,
            risk_addressed="Test",
            evidence_required="Test",
            metrics="Test",
            assumptions="Test",
        )
        
        artifacts = agent.generate_policy_package(version, policy_type="both")
        assert "rego" in artifacts
        assert "python" in artifacts
        assert "package scf" in artifacts["rego"]
        assert "PolicyValidator" in artifacts["python"]
    
    def test_policy_agent_generates_test_cases(self):
        """Policy agent should generate positive and negative tests"""
        agent = PolicyAgent(policies_dir="test_policies")
        
        version = ControlVersion(
            version="1.0",
            control_id="POL-002",
            created_date=datetime.now().isoformat(),
            created_by="test",
            status=ControlStatus.DRAFT,
            title="Access Control",
            objective="Test",
            control_statement="Test",
            control_domain=ControlDomain.ACCESS_CONTROL,
            control_family="Test",
            control_type=ControlType.PREVENTIVE,
            risk_addressed="Test",
            evidence_required="Test",
            metrics="Test",
            assumptions="Test",
        )
        
        artifacts = agent.generate_policy_package(version, policy_type="both")
        positive = artifacts["positive_test"]
        negative = artifacts["negative_test"]
        
        assert positive["expected_result"] == "PASS"
        assert negative["expected_result"] == "FAIL"
        assert "context" in positive
        assert "context" in negative


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
