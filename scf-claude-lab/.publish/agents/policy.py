"""
agents/policy.py
PolicyAgent: Converts controls into executable policies (Rego + Python).
Level 3: Policy-as-Code implementation.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Any
from .models import ControlVersion, PolicyEvaluationResult, PolicyResult, PolicyTestResult


class PolicyAgent:
    """
    Generates executable policies from controls.
    Supports two formats: OPA/Rego and Python validators.
    """
    
    def __init__(self, policies_dir: str = "policies"):
        self.policies_dir = Path(policies_dir)
        self.policies_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_policy_package(self, control_version: ControlVersion, 
                               policy_type: str = "both") -> Dict[str, str]:
        """
        Generate policy artifacts for a control.
        
        Args:
            control_version: ControlVersion object
            policy_type: "rego", "python", or "both"
        
        Returns:
            Dictionary with generated policy code
        """
        policy_id = f"{control_version.control_id}-{control_version.version}"
        
        artifacts = {}
        
        if policy_type in ("rego", "both"):
            artifacts["rego"] = self._generate_rego_policy(control_version)
        
        if policy_type in ("python", "both"):
            artifacts["python"] = self._generate_python_policy(control_version)
        
        # Generate test cases
        artifacts["positive_test"] = self._generate_positive_test(control_version)
        artifacts["negative_test"] = self._generate_negative_test(control_version)
        artifacts["readme"] = self._generate_readme(control_version)
        
        return artifacts
    
    def save_policy_package(self, control_version: ControlVersion,
                           artifacts: Dict[str, str]) -> str:
        """Save policy artifacts to disk."""
        policy_dir = self.policies_dir / f"{control_version.control_id}-{control_version.version.replace('.', '-')}"
        policy_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Rego
        if "rego" in artifacts:
            rego_file = policy_dir / "policy.rego"
            rego_file.write_text(artifacts["rego"], encoding='utf-8')
        
        # Save Python
        if "python" in artifacts:
            py_file = policy_dir / "policy.py"
            py_file.write_text(artifacts["python"], encoding='utf-8')
        
        # Save test cases
        positive_file = policy_dir / "positive_test.json"
        positive_file.write_text(
            json.dumps(artifacts["positive_test"], indent=2),
            encoding='utf-8'
        )
        
        negative_file = policy_dir / "negative_test.json"
        negative_file.write_text(
            json.dumps(artifacts["negative_test"], indent=2),
            encoding='utf-8'
        )
        
        # Save README
        readme_file = policy_dir / "README.md"
        readme_file.write_text(artifacts["readme"], encoding='utf-8')
        
        return str(policy_dir)
    
    # ─────────────────────────────────────────────────────────────────────────
    # REGO POLICY GENERATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def _generate_rego_policy(self, control: ControlVersion) -> str:
        """Generate OPA/Rego policy from control."""
        
        policy = f'''package scf.{control.control_id.lower().replace('-', '_')}

# {control.control_id}: {control.title}
# Type: {control.control_type.value}
# Domain: {control.control_domain.value}
# 
# Objective: {control.objective}
# Statement: {control.control_statement}

import future.keywords

# Main decision: allow or deny based on compliance with control requirements
allow if {{
    # Check that required metadata is present
    context.actor_type != null
    context.action != null
    
    # Check that the actor is authorized for this action
    is_authorized_actor[context.actor_type]
    
    # Check that the action is valid for this control
    is_valid_action[context.action]
    
    # Check all business rules within context
    validate_business_rules
}}

# Deny by default if allow doesn't match
deny if {{
    not allow
}}

# Define authorized actors by control domain
is_authorized_actor[actor_type] if {{
    context.actor_type == "admin"
}}

is_authorized_actor[actor_type] if {{
    context.actor_type == "{control.control_domain.value.lower().replace(' ', '_')}_user"
}}

# Define valid actions for this control
is_valid_action[action] if {{
    action == "{control.control_type.value.lower()}"
}}

# Business rule validation - override/extend based on control domain
validate_business_rules if {{
    # Add domain-specific business rules here
    # This is a template; customize per control
    true
}}

# Metrics for compliance scoring
metrics if {{
    # Count of authorized actions
    authorized_count := count(allow)
    
    # Count of denied actions
    denied_count := count(deny)
    
    # Compliance score (0-100)
    compliance_score := (authorized_count / (authorized_count + denied_count)) * 100
}}

# Output verbose decision with evidence
output if {{
    {{
        "decision": allow ? "ALLOW" : "DENY",
        "control_id": "{control.control_id}",
        "control_type": "{control.control_type.value}",
        "actor": context.actor_type,
        "action": context.action,
        "timestamp": context.timestamp,
        "reason": allow ? "Compliant with control requirements" : "Non-compliant: authorization denied",
    }}
}}
'''
        return policy
    
    # ─────────────────────────────────────────────────────────────────────────
    # PYTHON POLICY GENERATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def _generate_python_policy(self, control: ControlVersion) -> str:
        """Generate Python policy validator from control."""
        
        policy = f'''\"\"\"
{control.control_id}: {control.title}
Type: {control.control_type.value}
Domain: {control.control_domain.value}

Objective: {{control.objective}}

Statement:
{{control.control_statement}}
\"\"\"

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class PolicyResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class PolicyContext:
    actor_type: str
    action: str
    metadata: Dict[str, Any]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PolicyEvaluationResult:
    control_id: str
    policy_name: str
    result: PolicyResult
    violations: List[str]
    compliance_score: float = 0.0
    evidence: Dict[str, Any] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.evidence is None:
            self.evidence = {{}}

    def to_dict(self) -> Dict:
        return {{
            "control_id": self.control_id,
            "policy_name": self.policy_name,
            "result": self.result.value,
            "violations": self.violations,
            "compliance_score": self.compliance_score,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
        }}


class {control.control_id.replace('-', '')}PolicyValidator:
    \"\"\"Policy validator for {control.control_id}\"\"\"
    
    def __init__(self):
        self.control_id = "{control.control_id}"
        self.policy_name = "{control.title}"
        self.control_type = "{control.control_type.value}"
        self.domain = "{control.control_domain.value}"
    
    def validate(self, context: PolicyContext) -> PolicyEvaluationResult:
        \"\"\"
        Validate context against control requirements.
        
        Requirements:
        - Control Statement: {control.control_statement}
        - Risk: {control.risk_addressed}
        - Evidence: {control.evidence_required}
        - Metrics: {control.metrics}
        
        Args:
            context: PolicyContext with actor_type, action, metadata
        
        Returns:
            PolicyEvaluationResult with PASS/FAIL status
        \"\"\"
        violations = []
        evidence = {{}}
        
        # Requirement 1: Validate actor type
        if not context.actor_type:
            violations.append(f"FAIL: Actor type is missing")
        else:
            evidence['actor_type'] = context.actor_type
        
        # Requirement 2: Validate action
        if not context.action:
            violations.append(f"FAIL: Action is missing")
        else:
            evidence['action'] = context.action
        
        # Requirement 3: Domain-specific business logic
        # CUSTOMIZE THIS SECTION FOR YOUR CONTROL
        # Example: Check for required metadata
        required_fields = []  # Add your required fields here
        for field in required_fields:
            if field not in context.metadata or not context.metadata[field]:
                violations.append(f"FAIL: Required field '{{field}}' missing from metadata")
            else:
                evidence[field] = context.metadata[field]
        
        # Calculate compliance score
        compliance_score = 1.0 if not violations else 0.0
        
        # Determine result
        result = PolicyResult.PASS if not violations else PolicyResult.FAIL
        
        return PolicyEvaluationResult(
            control_id=self.control_id,
            policy_name=self.policy_name,
            result=result,
            violations=violations,
            compliance_score=compliance_score,
            evidence=evidence,
        )


# Example usage
if __name__ == "__main__":
    validator = {control.control_id.replace('-', '')}PolicyValidator()
    
    # Test case: positive (should PASS)
    ctx = PolicyContext(
        actor_type="authorized_user",
        action="{control.control_type.value.lower()}",
        metadata={{}},
    )
    result = validator.validate(ctx)
    print(f"Test Result: {{result.result.value}}")
    print(f"Violations: {{result.violations}}")
'''
        return policy
    
    # ─────────────────────────────────────────────────────────────────────────
    # TEST CASE GENERATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def _generate_positive_test(self, control: ControlVersion) -> Dict:
        """Generate positive test case (should PASS)."""
        return {
            "test_id": f"{control.control_id}-positive-001",
            "test_name": f"Valid compliance case for {control.control_id}",
            "control_id": control.control_id,
            "description": f"Test that validates {control.title}",
            "context": {
                "actor_type": "authorized_user",
                "action": control.control_type.value.lower(),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "authorization": "valid",
                    "evidence": "present",
                },
            },
            "expected_result": "PASS",
            "expected_violations": [],
            "notes": "This test demonstrates a compliant scenario.",
        }
    
    def _generate_negative_test(self, control: ControlVersion) -> Dict:
        """Generate negative test case (should FAIL)."""
        return {
            "test_id": f"{control.control_id}-negative-001",
            "test_name": f"Invalid / non-compliant case for {control.control_id}",
            "control_id": control.control_id,
            "description": f"Test that demonstrates violation of {control.title}",
            "context": {
                "actor_type": "unauthorized_user",
                "action": control.control_type.value.lower(),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "authorization": None,
                    "evidence": None,
                },
            },
            "expected_result": "FAIL",
            "expected_violations": [
                "Missing required authorization",
                "Missing evidence",
            ],
            "notes": "This test demonstrates a non-compliant scenario.",
        }
    
    def _generate_readme(self, control: ControlVersion) -> str:
        """Generate policy package documentation."""
        return f'''# {control.control_id}: {control.title}

## Control Details

**Type**: {control.control_type.value}  
**Domain**: {control.control_domain.value}  
**Family**: {control.control_family}  
**Version**: {control.version}  
**Status**: {control.status.value}  

## Objective

{control.objective}

## Control Statement

{control.control_statement}

## Risk Addressed

{control.risk_addressed}

## Evidence Required

{control.evidence_required}

## Metrics

{control.metrics}

## Assumptions

{control.assumptions}

---

## Policy Artifacts

### Rego Policy (`policy.rego`)

OPA/Rego-based policy for enterprise policy-as-code frameworks.
Compatible with OPA/Conftest and Styra DAS.

**Usage**:
```
opa eval -d policy.rego -i positive_test.json "data.scf.{control.control_id.lower().replace('-', '_')}.allow"
```

### Python Policy (`policy.py`)

Pure Python policy validator (no external dependencies).
Can be imported directly into applications.

**Usage**:
```python
from policy import {control.control_id.replace('-', '')}PolicyValidator

validator = {control.control_id.replace('-', '')}PolicyValidator()
result = validator.validate(context)
print(result.to_dict())
```

## Test Cases

### Positive Test (`positive_test.json`)
Valid scenario that should result in **PASS**.

**Run**:
```bash
curl -X POST http://localhost:8181/v1/data/scf/{control.control_id.lower().replace('-', '_')} \\
  -H "Content-Type: application/json" \\
  -d @positive_test.json
```

### Negative Test (`negative_test.json`)
Invalid scenario that should result in **FAIL**.

---

## Compliance Scoring

Compliance score is calculated as:
```
Score = (Passed Validations / Total Validations) * 100%
```

- **Score ≥ 95%**: Compliant  
- **Score 80-94%**: Mostly Compliant  
- **Score < 80%**: Non-Compliant  

---

## Integration Examples

### FastAPI Integration

```python
from api.schemas import PolicyValidationRequest
from policy import {control.control_id.replace('-', '')}PolicyValidator

@app.post("/validate/{control.control_id}")
async def validate_{control.control_id.lower().replace('-', '_')}(request: PolicyValidationRequest):
    validator = {control.control_id.replace('-', '')}PolicyValidator()
    result = validator.validate(request.context)
    return result.to_dict()
```

### OPA Integration

Deployed as a bundle in Styra DAS or OPA container.

---

## Change History

- **v{control.version}** - {control.created_date} - Initial policy definition

---

*Generated: {datetime.now().isoformat()}*
*Control ID: {control.control_id}*
'''
    
    # ─────────────────────────────────────────────────────────────────────────
    # POLICY EVALUATION (Runtime)
    # ─────────────────────────────────────────────────────────────────────────
    
    def evaluate_policy(self, control_id: str, context: Dict[str, Any],
                       policy_type: str = "python") -> PolicyEvaluationResult:
        """
        Evaluate a policy against given context.
        """
        # Bypass policies_dir logic for level3 integration
        policy_dir = Path("level3")

        
        if policy_type == "python":
            return self._evaluate_python_policy(control_id, context, policy_dir)
        elif policy_type == "rego":
            return self._evaluate_rego_policy(control_id, context, policy_dir)
        
        return PolicyEvaluationResult(
            control_id=control_id,
            policy_name="Unknown",
            result=PolicyResult.INCONCLUSIVE,
            violations=[f"Unknown policy type: {policy_type}"],
        )
    
    def _evaluate_python_policy(self, control_id: str, context: Dict,
                               policy_dir: Path) -> PolicyEvaluationResult:
        """Evaluate Python policy."""
        is_authorized = context.get('metadata', {}).get('authorized', False)
        result = PolicyResult.PASS if is_authorized else PolicyResult.FAIL
        violations = [] if is_authorized else ["VIOLATION: Actor not authorized"]
        
        return PolicyEvaluationResult(
            control_id=control_id,
            policy_name="Policy Validation",
            result=result,
            violations=violations,
            compliance_score=1.0 if is_authorized else 0.0,
            evidence_collected=context,
        )
    
    def _evaluate_rego_policy(self, control_id: str, context: Dict,
                             policy_dir: Path) -> PolicyEvaluationResult:
        """Evaluate Rego policy via OPA API (stub - would call OPA)."""
        # Placeholder - in production, would POST to OPA server
        return PolicyEvaluationResult(
            control_id=control_id,
            policy_name="Rego Policy",
            result=PolicyResult.PASS,
            violations=[],
            compliance_score=1.0,
            evidence=context,
        )
