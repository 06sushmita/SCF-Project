"""
api/main.py
FastAPI application for SCF platform.
RESTful API for control generation, management, policy validation, and reporting.
"""

import io
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from agents import (
    RegistryAgent, ControlAgent, PolicyAgent,
    ExtractAgent, ControlVersion, ControlStatus, ControlDomain, ControlType
)
from . import schemas

# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION SETUP
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SCF Platform API",
    description="Secure Control Framework - Regulatory Controls as Code",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

# Enable CORS for browser-based testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZE AGENTS
# ─────────────────────────────────────────────────────────────────────────────

registry = RegistryAgent(registry_path="controls/controls_registry.json")
extract_agent = ExtractAgent()
control_agent = ControlAgent()
policy_agent = PolicyAgent(policies_dir="policies")


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH & INFO ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check() -> schemas.HealthCheckResponse:
    """Check API health and service status."""
    metadata = registry.get_metadata()
    return schemas.HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        services={
            "registry": "operational",
            "extraction": "operational",
            "control_generation": "operational",
            "policy_engine": "operational",
        }
    )


@app.get("/api/v1/info", tags=["System"])
async def info() -> dict:
    """Get system information and statistics."""
    metadata = registry.get_metadata()
    return {
        "platform": "Secure Control Framework",
        "version": "2.0.0",
        "registry": metadata.to_dict(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL GENERATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/controls/generate", tags=["Control Generation"],
          response_model=schemas.GenerateControlsResponse)
async def generate_controls(file: UploadFile = File(...)) -> schemas.GenerateControlsResponse:
    """
    Extract regulatory clauses from PDF and generate controls.
    
    - Upload PDF file
    - System extracts clauses, filters duplicates
    - Generates structured controls with domains, types, objectives
    - All controls created in 'draft' status
    
    Returns: Generated controls (v1.0, draft status)
    """
    try:
        # Read PDF into memory
        contents = await file.read()
        pdf_buffer = io.BytesIO(contents)
        pdf_buffer.name = file.filename
        
        # Save temporarily to extract
        temp_pdf = Path("temp_upload.pdf")
        temp_pdf.write_bytes(contents)
        
        # Extract clauses
        try:
            clauses = extract_agent.extract_from_pdf(str(temp_pdf))
            stats = extract_agent.get_extraction_stats(str(temp_pdf))
        finally:
            if temp_pdf.exists():
                temp_pdf.unlink()
        
        if not clauses:
            raise ValueError("No meaningful clauses extracted from PDF")
        
        # Generate controls
        controls_dict = control_agent.generate_controls(clauses)
        
        # Create control versions and register
        created_controls = []
        for ctrl_dict in controls_dict:
            # Create version object
            version = control_agent.clause_to_control_version(ctrl_dict, actor="pdf_generation")
            
            # Register
            control = registry.create_control(
                version,
                actor="pdf_generation",
                reason=f"Generated from {file.filename}"
            )
            
            created_controls.append(version.to_dict())
        
        return schemas.GenerateControlsResponse(
            status="success",
            message=f"{len(controls_dict)} controls extracted and registered",
            controls_generated=len(controls_dict),
            controls=[
                schemas.ControlVersionResponse(**c) for c in created_controls
            ],
            statistics={
                "source_file": file.filename,
                "extraction_stats": stats,
            },
            timestamp=datetime.now().isoformat(),
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Generation failed: {str(e)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL RETRIEVAL & SEARCH
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/controls", tags=["Controls"],
         response_model=list[schemas.ControlSearchResponse])
async def search_controls(
    query: Optional[str] = None,
    domain: Optional[str] = None,
    control_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> list[schemas.ControlSearchResponse]:
    """
    Search controls with filters.
    
    Query Parameters:
    - query: Search term (matches title, objective, tags)
    - domain: Filter by control domain
    - control_type: Filter by type (Preventive/Detective/Corrective)
    - status: Filter by status (draft/active/deprecated)
    - limit: Max results (1-500)
    """
    results = registry.search(
        query=query or "",
        domain=domain,
        control_type=control_type,
        status=status,
    )
    
    # Convert and limit
    search_results = [
        schemas.ControlSearchResponse(**r.to_dict())
        for r in results[:limit]
    ]
    
    return search_results


@app.get("/api/v1/controls/{control_id}", tags=["Controls"],
         response_model=schemas.ControlVersionResponse)
async def get_control(
    control_id: str,
    version: str = "active",
) -> schemas.ControlVersionResponse:
    """
    Retrieve a specific control version.
    
    Path Parameters:
    - control_id: Control ID (e.g., SCF-001)
    
    Query Parameters:
    - version: Version number ("1.0", "1.1") or "active", "latest"
    """
    control_version = registry.get_control_version(control_id, version=version)
    if not control_version:
        raise HTTPException(
            status_code=404,
            detail=f"Control {control_id} version {version} not found"
        )
    
    return schemas.ControlVersionResponse(**control_version.to_dict())


@app.get("/api/v1/controls/{control_id}/history", tags=["Controls"],
         response_model=schemas.ControlHistoryResponse)
async def get_control_history(control_id: str) -> schemas.ControlHistoryResponse:
    """Get full version history for a control."""
    control = registry.get_control(control_id)
    if not control:
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")
    
    return schemas.ControlHistoryResponse(**control.to_dict())


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL MANAGEMENT (CRUD)
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/controls", tags=["Control Management"],
          response_model=schemas.ControlVersionResponse)
async def create_control(req: schemas.ControlRequest) -> schemas.ControlVersionResponse:
    """Create a new control (draft status)."""
    try:
        version = ControlVersion(
            version="1.0",
            control_id=f"SCF-{len(registry.controls) + 1:03d}",
            created_date=datetime.now().isoformat(),
            created_by=req.actor,
            status=ControlStatus.DRAFT,
            title=req.title,
            objective=req.objective,
            control_statement=req.control_statement,
            control_domain=ControlDomain(req.control_domain),
            control_family=req.control_family,
            control_type=ControlType(req.control_type),
            risk_addressed=req.risk_addressed,
            evidence_required=req.evidence_required,
            metrics=req.metrics,
            assumptions=req.assumptions,
        )
        
        control = registry.create_control(version, actor=req.actor)
        return schemas.ControlVersionResponse(**version.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/api/v1/controls/{control_id}", tags=["Control Management"],
           response_model=schemas.ControlVersionResponse)
async def update_control(
    control_id: str,
    req: schemas.ControlUpdateRequest,
) -> schemas.ControlVersionResponse:
    """
    Create new minor version of control with specified changes.
    Original version remains immutable.
    """
    try:
        changes = {}
        if req.title:
            changes['title'] = req.title
        if req.objective:
            changes['objective'] = req.objective
        if req.control_statement:
            changes['control_statement'] = req.control_statement
        if req.risk_addressed:
            changes['risk_addressed'] = req.risk_addressed
        if req.evidence_required:
            changes['evidence_required'] = req.evidence_required
        if req.metrics:
            changes['metrics'] = req.metrics
        if req.assumptions:
            changes['assumptions'] = req.assumptions
        
        new_version = registry.update_control(
            control_id,
            changes=changes,
            actor=req.actor,
            reason=req.reason,
        )
        
        return schemas.ControlVersionResponse(**new_version.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/controls/{control_id}/activate", tags=["Control Management"],
          response_model=schemas.ControlVersionResponse)
async def activate_control(
    control_id: str,
    req: schemas.ControlLifecycleRequest,
) -> schemas.ControlVersionResponse:
    """Activate a control version (transition to 'active' status)."""
    try:
        if req.status != "active":
            raise ValueError("Only 'active' status transitions are supported via this endpoint")
        
        version = registry.activate_control(
            control_id,
            version=None,  # Activates latest draft
            actor=req.actor,
            reason=req.reason,
        )
        
        return schemas.ControlVersionResponse(**version.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/controls/{control_id}/deprecate", tags=["Control Management"])
async def deprecate_control(
    control_id: str,
    req: schemas.ControlLifecycleRequest,
) -> dict:
    """Deprecate a control (mark as no longer in use)."""
    try:
        success = registry.deprecate_control(
            control_id,
            actor=req.actor,
            reason=req.reason,
        )
        if not success:
            raise ValueError(f"Control {control_id} not found")
        
        return {
            "status": "success",
            "message": f"Control {control_id} deprecated",
            "timestamp": datetime.now().isoformat(),
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# POLICY VALIDATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/policies/validate", tags=["Policies"],
          response_model=schemas.PolicyValidationResponse)
async def validate_policy(req: schemas.PolicyValidationRequest) -> schemas.PolicyValidationResponse:
    """
    Validate a policy against given context.
    
    Evaluates control compliance based on provided actor context.
    Returns PASS/FAIL with compliance score and violations.
    """
    try:
        # Evaluate policy
        result = policy_agent.evaluate_policy(
            control_id=req.control_id,
            context=req.context.dict(),
            policy_type=req.policy_type,
        )
        
        return schemas.PolicyValidationResponse(**result.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/policies/run-tests", tags=["Policies"],
          response_model=schemas.PolicyTestsResponse)
async def run_policy_tests(req: schemas.PolicyTestsRequest) -> schemas.PolicyTestsResponse:
    """
    Run positive and negative test cases from level3/tests.json.
    """
    try:
        tests_file = Path("level3/tests.json")
        if not tests_file.exists():
            raise FileNotFoundError("Tests file not found in level3/")
            
        with open(tests_file, "r", encoding="utf-8") as f:
            all_tests = json.load(f)
            
        passed = 0
        failed = 0
        results = []
        
        # Filter tests for this control
        control_tests = [t for t in all_tests.get("tests", []) if t["test_id"].startswith(req.control_id)]
        
        for test_case in control_tests:
            is_positive = test_case.get("expected") == "PASS"
            if is_positive and not req.run_positive_tests: continue
            if not is_positive and not req.run_negative_tests: continue
            
            result = policy_agent.evaluate_policy(
                req.control_id,
                context=test_case.get('context', {}),
            )
            
            test_passed = result.result.value == test_case.get('expected', 'PASS')
            if test_passed: passed += 1
            else: failed += 1
                
            results.append(schemas.PolicyTestResult(
                test_id=test_case.get('test_id', 'unknown'),
                test_name=test_case.get('test_name', 'Test'),
                expected_result=test_case.get('expected', 'PASS'),
                actual_result=result.result.value,
                passed=test_passed,
                violations=result.violations,
                timestamp=datetime.now().isoformat(),
            ))
            
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0.0
        
        return schemas.PolicyTestsResponse(
            control_id=req.control_id,
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            results=results,
            success_rate=success_rate,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY & COMPLIANCE REPORTING
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/registry", tags=["Registry"],
         response_model=schemas.RegistryMetadataResponse)
async def get_registry_metadata() -> schemas.RegistryMetadataResponse:
    """Get registry metadata and statistics."""
    metadata = registry.get_metadata()
    return schemas.RegistryMetadataResponse(**metadata.to_dict())


@app.get("/api/v1/audit-log", tags=["Audit"],
         response_model=schemas.AuditLogResponse)
async def get_audit_log(
    control_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
) -> schemas.AuditLogResponse:
    """
    Retrieve audit log with optional filtering.
    
    Query Parameters:
    - control_id: Filter by control
    - start_date: ISO date (e.g., 2024-01-01T00:00:00Z)
    - end_date: ISO date
    - limit: Max results (1-1000)
    """
    entries = registry.get_audit_log(
        control_id=control_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    entries = entries[:limit]
    
    return schemas.AuditLogResponse(
        total_entries=len(entries),
        entries=[
            schemas.AuditLogEntry(**entry) for entry in entries
        ],
    )


@app.get("/api/v1/compliance/by-domain", tags=["Compliance"],
         response_model=list[schemas.ComplianceStatusResponse])
async def compliance_by_domain() -> list[schemas.ComplianceStatusResponse]:
    """Get compliance status by control domain."""
    results = []
    metadata = registry.get_metadata()
    
    for domain, count in metadata.by_domain.items():
        # Query controls by domain
        search_results = registry.search(domain=domain)
        
        active_count = sum(
            1 for r in search_results if r.status == "active"
        )
        
        # Simplified compliance: active = compliant
        compliant = active_count
        non_compliant = count - compliant
        
        results.append(schemas.ComplianceStatusResponse(
            domain=domain,
            total_controls=count,
            active_controls=active_count,
            compliant_controls=compliant,
            non_compliant_controls=non_compliant,
            compliance_percentage=(compliant / count * 100) if count > 0 else 0,
        ))
    
    return results


# ─────────────────────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": str(exc) if str(exc) else None,
            "timestamp": datetime.now().isoformat(),
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
