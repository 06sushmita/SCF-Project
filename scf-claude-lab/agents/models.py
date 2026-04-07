"""
agents/models.py
Core data structures shared across all agents.
Immutable, audit-friendly design for compliance systems.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import json


# ─────────────────────────────────────────────────────────────────────────────
# ENUMERATIONS
# ─────────────────────────────────────────────────────────────────────────────

class ControlDomain(str, Enum):
    """Standard control domains per COSO framework."""
    ACCESS_CONTROL = "Access Control"
    DATA_GOVERNANCE = "Data Governance"
    MONITORING_AUDITING = "Monitoring and Auditing"
    INFORMATION_SECURITY = "Information Security Awareness"
    REGULATORY_COMPLIANCE = "Regulatory Compliance"
    FINANCIAL_COMPLIANCE = "Financial Compliance"
    GOVERNANCE_COMPLIANCE = "Governance and Compliance"


class ControlType(str, Enum):
    """Three-line-of-defense control types."""
    PREVENTIVE = "Preventive"
    DETECTIVE = "Detective"
    CORRECTIVE = "Corrective"
    ADMINISTRATIVE = "Administrative"


class ControlStatus(str, Enum):
    """Lifecycle states for controls."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class PolicyResult(str, Enum):
    """Policy evaluation outcomes."""
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES (immutable, JSON-serializable)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AuditRecord:
    """Single change event in a control's history."""
    timestamp: str  # ISO 8601
    actor: str  # User email or "system"
    action: str  # "created", "updated", "activated", "deprecated"
    reason: Optional[str] = None
    changes: Dict[str, Any] = field(default_factory=dict)
    approval_ticket: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ControlVersion:
    """Single immutable version of a control."""
    version: str  # "1.0", "1.1", "2.0"
    control_id: str  # "SCF-001"
    created_date: str  # ISO 8601
    created_by: str  # User email or "system"
    status: ControlStatus
    
    # Core control fields (immutable once version created)
    title: str
    objective: str
    control_statement: str
    control_domain: ControlDomain
    control_family: str
    control_type: ControlType
    
    # Metadata
    risk_addressed: str
    evidence_required: str
    metrics: str
    assumptions: str
    
    # Version history
    amended_from_version: Optional[str] = None  # Parent version if update
    amendment_reason: Optional[str] = None
    audit_trail: List[AuditRecord] = field(default_factory=list)
    
    # Optional policy reference
    policy_id: Optional[str] = None
    test_results_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            "version": self.version,
            "control_id": self.control_id,
            "created_date": self.created_date,
            "created_by": self.created_by,
            "status": self.status.value,
            "title": self.title,
            "objective": self.objective,
            "control_statement": self.control_statement,
            "control_domain": self.control_domain.value,
            "control_family": self.control_family,
            "control_type": self.control_type.value,
            "risk_addressed": self.risk_addressed,
            "evidence_required": self.evidence_required,
            "metrics": self.metrics,
            "assumptions": self.assumptions,
            "amended_from_version": self.amended_from_version,
            "amendment_reason": self.amendment_reason,
            "audit_trail": [r.to_dict() for r in self.audit_trail],
            "policy_id": self.policy_id,
            "test_results_id": self.test_results_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ControlVersion':
        """Deserialize from JSON dict."""
        data_copy = data.copy()
        # Convert enum strings back to enum values
        data_copy['status'] = ControlStatus(data_copy['status'])
        data_copy['control_domain'] = ControlDomain(data_copy['control_domain'])
        data_copy['control_type'] = ControlType(data_copy['control_type'])
        # Reconstruct audit trail
        data_copy['audit_trail'] = [
            AuditRecord(**record) for record in data_copy.get('audit_trail', [])
        ]
        return cls(**data_copy)


@dataclass
class Control:
    """
    Control (top-level container for all versions).
    Represents a single control with full version history.
    """
    control_id: str  # "SCF-001"
    versions: List[ControlVersion] = field(default_factory=list)  # Ordered by version date
    current_version: str = "1.0"  # Pointer to active version number
    search_tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_active_version(self) -> Optional[ControlVersion]:
        """Return the currently active version."""
        for v in self.versions:
            if v.status == ControlStatus.ACTIVE:
                return v
        return None
    
    def get_version(self, version_str: str) -> Optional[ControlVersion]:
        """Get specific version by version number."""
        for v in self.versions:
            if v.version == version_str:
                return v
        return None
    
    def add_version(self, version: ControlVersion) -> None:
        """Add a new version to this control (immutable append)."""
        # Ensure version is not duplicate
        if self.get_version(version.version):
            raise ValueError(f"Version {version.version} already exists for {self.control_id}")
        self.versions.append(version)
        self.current_version = version.version
    
    def to_dict(self) -> Dict:
        return {
            "control_id": self.control_id,
            "versions": [v.to_dict() for v in self.versions],
            "current_version": self.current_version,
            "search_tags": self.search_tags,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Control':
        """Deserialize from JSON dict."""
        return cls(
            control_id=data['control_id'],
            versions=[ControlVersion.from_dict(v) for v in data['versions']],
            current_version=data['current_version'],
            search_tags=data.get('search_tags', []),
            created_at=data.get('created_at', datetime.now().isoformat()),
        )


# ─────────────────────────────────────────────────────────────────────────────
# POLICY CONTEXT & RESULTS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PolicyContext:
    """Input context for policy evaluation."""
    actor_type: str  # "broker", "investor", "employee", etc.
    action: str  # "submit_claim", "register_nomination", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PolicyTestResult:
    """Result of a single policy test run."""
    test_id: str
    control_id: str
    test_name: str
    context: Dict[str, Any]
    result: PolicyResult  # PASS, FAIL, INCONCLUSIVE
    violations: List[str] = field(default_factory=list)
    matched_rules: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "control_id": self.control_id,
            "test_name": self.test_name,
            "context": self.context,
            "result": self.result.value,
            "violations": self.violations,
            "matched_rules": self.matched_rules,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class PolicyEvaluationResult:
    """Overall result from validating a control policy against context."""
    control_id: str
    policy_name: str
    result: PolicyResult  # PASS, FAIL, INCONCLUSIVE
    violations: List[str] = field(default_factory=list)
    compliance_score: float = 0.0  # 0.0 to 1.0
    evidence_collected: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "control_id": self.control_id,
            "policy_name": self.policy_name,
            "result": self.result.value,
            "violations": self.violations,
            "compliance_score": self.compliance_score,
            "evidence_collected": self.evidence_collected,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY SNAPSHOT (for search indexing)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ControlSearchResult:
    """Lightweight result for search queries."""
    control_id: str
    title: str
    version: str
    status: str
    domain: str
    control_type: str
    relevance_score: float = 1.0  # For ranking search results
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY METADATA
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RegistryMetadata:
    """Metadata about the entire registry."""
    registry_version: str = "1.0"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    total_controls: int = 0
    active_controls: int = 0
    deprecated_controls: int = 0
    total_versions: int = 0
    by_domain: Dict[str, int] = field(default_factory=dict)
    by_type: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
