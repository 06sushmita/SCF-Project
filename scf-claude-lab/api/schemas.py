"""
api/schemas.py
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL REQUEST/RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────────────────

class ControlRequest(BaseModel):
    """Request to create a new control."""
    title: str = Field(..., min_length=5, max_length=200)
    objective: str = Field(..., min_length=10)
    control_statement: str = Field(..., min_length=20)
    control_domain: str
    control_family: str
    control_type: str  # Preventive, Detective, Corrective, Administrative
    risk_addressed: str
    evidence_required: str
    metrics: str
    assumptions: str
    actor: str = "api_user"


class ControlVersionResponse(BaseModel):
    """Response: Single control version."""
    control_id: str
    version: str
    title: str
    objective: str
    control_statement: str
    control_domain: str
    control_family: str
    control_type: str
    status: str
    created_date: str
    created_by: str
    risk_addressed: str
    evidence_required: str
    metrics: str
    assumptions: str
    
    class Config:
        from_attributes = True


class ControlHistoryResponse(BaseModel):
    """Response: Full control with version history."""
    control_id: str
    versions: List[ControlVersionResponse]
    current_version: str
    search_tags: List[str]
    created_at: str


class ControlUpdateRequest(BaseModel):
    """Request to update/new version a control."""
    title: Optional[str] = None
    objective: Optional[str] = None
    control_statement: Optional[str] = None
    risk_addressed: Optional[str] = None
    evidence_required: Optional[str] = None
    metrics: Optional[str] = None
    assumptions: Optional[str] = None
    reason: str = Field(..., min_length=10)
    actor: str = "api_user"


class ControlLifecycleRequest(BaseModel):
    """Request to change control status."""
    status: str  # draft, active, deprecated
    reason: str
    actor: str = "api_user"
    approval_ticket: Optional[str] = None


class ControlSearchResponse(BaseModel):
    """Response: Search result item."""
    control_id: str
    title: str
    version: str
    status: str
    domain: str
    control_type: str
    relevance_score: float


class ControlsSearchRequest(BaseModel):
    """Request: Search controls."""
    query: Optional[str] = None
    domain: Optional[str] = None
    control_type: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(50, ge=1, le=500)


# ─────────────────────────────────────────────────────────────────────────────
# POLICY REQUEST/RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────────────────

class PolicyContext(BaseModel):
    """Input context for policy evaluation."""
    actor_type: str
    action: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PolicyValidationRequest(BaseModel):
    """Request to validate policy."""
    control_id: str
    context: PolicyContext
    policy_type: str = "python"  # python or rego


class PolicyValidationResponse(BaseModel):
    """Response from policy validation."""
    control_id: str
    policy_name: str
    result: str  # PASS, FAIL, INCONCLUSIVE
    violations: List[str]
    compliance_score: float
    evidence_collected: Dict[str, Any]
    timestamp: str


class PolicyTestsRequest(BaseModel):
    """Request to run policy tests."""
    control_id: str
    run_positive_tests: bool = True
    run_negative_tests: bool = True


class PolicyTestResult(BaseModel):
    """Result of a single policy test."""
    test_id: str
    test_name: str
    expected_result: str  # PASS, FAIL
    actual_result: str
    passed: bool
    violations: List[str]
    timestamp: str


class PolicyTestsResponse(BaseModel):
    """Response from policy tests."""
    control_id: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: List[PolicyTestResult]
    success_rate: float


# ─────────────────────────────────────────────────────────────────────────────
# GENERATION REQUEST/RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────────────────

class GenerateControlsResponse(BaseModel):
    """Response from control generation."""
    status: str  # success, error
    message: str
    controls_generated: int
    controls: List[ControlVersionResponse]
    statistics: Dict[str, Any]
    timestamp: str


class ExtractionStats(BaseModel):
    """Statistics from text extraction."""
    total_pages: Optional[int] = None
    total_sentences: int
    meaningful_clauses: int
    duplicates_removed: int


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY REQUEST/RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────────────────

class RegistryMetadataResponse(BaseModel):
    """Metadata about the control registry."""
    registry_version: str
    last_updated: str
    total_controls: int
    active_controls: int
    deprecated_controls: int
    total_versions: int
    by_domain: Dict[str, int]
    by_type: Dict[str, int]


class AuditLogEntry(BaseModel):
    """Single audit log entry."""
    event_id: str
    timestamp: str
    event_type: str
    control_id: str
    actor: str
    reason: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# COMPLIANCE REPORTING MODELS
# ─────────────────────────────────────────────────────────────────────────────

class ComplianceStatusResponse(BaseModel):
    """Compliance status for a domain."""
    domain: str
    total_controls: int
    active_controls: int
    compliant_controls: int
    non_compliant_controls: int
    compliance_percentage: float


class AuditLogQueryRequest(BaseModel):
    """Request to query audit log."""
    control_id: Optional[str] = None
    event_type: Optional[str] = None
    actor: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)


class AuditLogResponse(BaseModel):
    """Response: Audit log entries."""
    total_entries: int
    entries: List[AuditLogEntry]


# ─────────────────────────────────────────────────────────────────────────────
# ERROR RESPONSE MODEL
# ─────────────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error response."""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK MODELS
# ─────────────────────────────────────────────────────────────────────────────

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str  # healthy, degraded
    timestamp: str
    version: str
    services: Dict[str, Any]
