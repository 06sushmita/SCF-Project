"""
Level 3 - Policy-as-Code Generator
Automatically generates executable policies from control definitions.

Single Source of Truth: control.yaml (level1/controls.yaml)
Policy Generation: control_statement → policy.rego + test cases
"""

import json
import yaml
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Ensure stdout uses UTF-8 so emojis don't crash on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class PolicyArtifacts:
    """Generated policy artifacts"""
    control_id: str
    policy_rego: str
    evaluator_py: str
    positive_test: Dict[str, Any]
    negative_test: Dict[str, Any]
    metadata: Dict[str, Any]


class PolicyGenerator:
    """
    Level 3: Policy Generator
    Converts control statements to executable enforcement logic
    """
    
    def __init__(self, controls_yaml_path: str = "level1/controls.yaml"):
        """Initialize generator with control definitions"""
        self.controls_yaml_path = Path(controls_yaml_path)
        self.controls = self._load_controls()
        self.policy_dir = Path("policies")
        self.policy_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_controls(self) -> Dict[str, Any]:
        """Load controls from YAML (single source of truth)"""
        if not self.controls_yaml_path.exists():
            raise FileNotFoundError(f"Controls file not found: {self.controls_yaml_path}")
        
        with open(self.controls_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        controls_dict = {}
        for control in data.get('controls', []):
            control_id = control.get('control_id')
            controls_dict[control_id] = control
        
        print(f"📖 Loaded {len(controls_dict)} controls from {self.controls_yaml_path}")
        return controls_dict
    
    def generate_policy_for_control(self, control_id: str) -> Optional[PolicyArtifacts]:
        """Generate policy artifacts for a control"""
        if control_id not in self.controls:
            print(f"❌ Control not found: {control_id}")
            return None
        
        control = self.controls[control_id]
        print(f"\n📝 Generating policy for {control_id}...")
        
        # Generate policy artifacts
        policy_rego = self._generate_rego_policy(control)
        evaluator_py = self._generate_python_evaluator(control)
        positive_test = self._generate_positive_test(control)
        negative_test = self._generate_negative_test(control)
        
        artifacts = PolicyArtifacts(
            control_id=control_id,
            policy_rego=policy_rego,
            evaluator_py=evaluator_py,
            positive_test=positive_test,
            negative_test=negative_test,
            metadata={
                "control_statement": control.get('control_statement'),
                "objective": control.get('objective'),
                "control_type": control.get('control_type'),
                "control_domain": control.get('control_domain'),
                "generated_at": datetime.now().isoformat(),
            }
        )
        
        return artifacts
    
    def _generate_rego_policy(self, control: Dict[str, Any]) -> str:
        """Generate Rego policy from control statement"""
        control_id = control.get('control_id')
        title = control.get('title')
        control_type = control.get('control_type')
        domain = control.get('control_domain')
        control_statement = control.get('control_statement', '')
        
        # Extract key concepts from control statement
        keywords = self._extract_keywords_from_statement(control_statement)
        
        rego_policy = f'''package scf.{control_id.lower().replace('-', '_')}

# {control_id}: {title}
# Type: {control_type}
# Domain: {domain}
#
# Control Statement:
# {self._format_multiline_comment(control_statement)}

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# ─────────────────────────────────────────────────────────────────────────
# PRIMARY DECISION RULES (from control statement)
# ─────────────────────────────────────────────────────────────────────────

allow if {{
    # Validate context is properly formed
    input.context != null
    input.context.actor_type != null
    input.context.action != null
    input.data != null
    
    # Check compliance conditions derived from control statement
    is_compliant
}}

deny if {{
    not allow
}}

# ─────────────────────────────────────────────────────────────────────────
# COMPLIANCE RULES (derived from control statement)
# ─────────────────────────────────────────────────────────────────────────

is_compliant if {{
    # Requirement 1: Basic attribute presence
    input.context.actor_type != null
    input.context.action != null
    
    # Requirement 2: Check authorization
    is_authorized
    
    # Requirement 3: Check business rules
    validate_business_rules
}}

is_authorized if {{
    # Actor must have appropriate role or status
    input.context.metadata.authorized == true
}}

is_authorized if {{
    # Or actor must be in approved list
    input.context.actor_type in input.data.approved_actors
}}

validate_business_rules if {{
    # Enforce domain-specific rules
    # Requirements derived from: {self._format_multiline_comment(control_statement)}
    true
}}

# ─────────────────────────────────────────────────────────────────────────
# VIOLATION DETECTION
# ─────────────────────────────────────────────────────────────────────────

violations[msg] if {{
    input.context.actor_type == null
    msg := "VIOLATION: Missing actor type"
}}

violations[msg] if {{
    not is_authorized
    msg := "VIOLATION: Actor not authorized per control requirement"
}}

violations[msg] if {{
    not validate_business_rules
    msg := "VIOLATION: Business rules check failed"
}}

# ─────────────────────────────────────────────────────────────────────────
# COMPLIANCE SCORING
# ─────────────────────────────────────────────────────────────────────────

compliance_score := 100 if allow
compliance_score := max([0, (3 - count(violations)) * 33]) if deny

# ─────────────────────────────────────────────────────────────────────────
# POLICY DECISION OUTPUT
# ─────────────────────────────────────────────────────────────────────────

policy_decision := {{
    "control_id": "{control_id}",
    "control_type": "{control_type}",
    "control_domain": "{domain}",
    "decision": "ALLOW" if allow else "DENY",
    "result": "PASS" if allow else "FAIL",
    "compliance_score": compliance_score,
    "actor_type": input.context.actor_type,
    "action": input.context.action,
    "timestamp": input.context.metadata.timestamp,
    "violations": [msg | msg := violations[_]],
    "violation_count": count(violations),
    "reason": allow ? 
        "Control requirements met - compliant" : 
        "Control requirements not met - violations detected",
    "evidence": {{
        "actor_type": input.context.actor_type,
        "authorized": is_authorized,
        "business_rules_valid": validate_business_rules,
    }}
}}
'''
        return rego_policy
    
    def _generate_python_evaluator(self, control: Dict[str, Any]) -> str:
        """Generate Python policy validator"""
        control_id = control.get('control_id')
        title = control.get('title')
        control_type = control.get('control_type')
        domain = control.get('control_domain')
        control_statement = control.get('control_statement', '')
        
        class_name = f"{control_id.replace('-', '_')}Validator"
        
        evaluator = f'''\"\"\"
{control_id}: {title}

Control Definition:
  Type: {control_type}
  Domain: {domain}
  Statement: {control_statement}
\"\"\"

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class PolicyResult:
    control_id: str
    result: str  # PASS or FAIL
    decision: str  # ALLOW or DENY
    compliance_score: float
    violations: List[str]
    evidence: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class {class_name}:
    \"\"\"Policy validator for {control_id}\"\"\"
    
    def __init__(self):
        self.control_id = "{control_id}"
        self.control_type = "{control_type}"
        self.domain = "{domain}"
        self.requirements = [
            "Context must be properly formed",
            "Actor must be authorized",
            "Business rules must be satisfied",
        ]
    
    def evaluate(self, context: Dict[str, Any], data: Dict[str, Any]) -> PolicyResult:
        \"\"\"
        Evaluate compliance with control requirements.
        
        Control Statement:
        {self._format_multiline_comment(control_statement)}
        \"\"\"
        violations = []
        evidence = {{}}
        
        # Requirement 1: Validate context
        if not context or 'actor_type' not in context:
            violations.append("VIOLATION: Missing context or actor type")
        else:
            evidence['actor_type'] = context.get('actor_type')
        
        # Requirement 2: Check authorization
        if 'metadata' not in context or not context['metadata'].get('authorized'):
            if context.get('actor_type') not in data.get('approved_actors', []):
                violations.append("VIOLATION: Actor not authorized per control requirement")
        evidence['authorized'] = len(violations) == 0
        
        # Requirement 3: Business rules
        # [Customize based on specific control]
        evidence['business_rules_valid'] = True
        
        # Calculate compliance score
        passed_requirements = len(self.requirements) - len(violations)
        compliance_score = (passed_requirements / len(self.requirements)) * 100.0
        
        # Determine result
        result = "PASS" if not violations else "FAIL"
        decision = "ALLOW" if not violations else "DENY"
        
        return PolicyResult(
            control_id=self.control_id,
            result=result,
            decision=decision,
            compliance_score=compliance_score,
            violations=violations,
            evidence=evidence,
            timestamp=datetime.now().isoformat(),
        )


def evaluate_policy(context: Dict[str, Any], data: Dict[str, Any]) -> PolicyResult:
    \"\"\"Evaluate policy against context\"\"\"
    validator = {class_name}()
    return validator.evaluate(context, data)
'''
        return evaluator
    
    def _generate_positive_test(self, control: Dict[str, Any]) -> Dict[str, Any]:
        """Generate positive test case (should PASS)"""
        control_id = control.get('control_id')
        
        return {{
            "test_id": f"{control_id}-positive-001",
            "test_name": f"Compliant scenario: {control.get('title')}",
            "control_id": control_id,
            "description": f"Positive test: All control requirements satisfied",
            "context": {{
                "actor_type": "authorized_user",
                "action": "access_resource",
                "metadata": {{
                    "timestamp": datetime.now().isoformat(),
                    "authorized": True,
                }}
            }},
            "data": {{
                "approved_actors": ["authorized_user", "admin"],
            }},
            "expected_result": "PASS",
            "expected_decision": "ALLOW",
            "expected_compliance_score": 100.0,
            "expected_violations": [],
            "notes": f"All requirements met for control: {control_id}",
        }}
    
    def _generate_negative_test(self, control: Dict[str, Any]) -> Dict[str, Any]:
        """Generate negative test case (should FAIL)"""
        control_id = control.get('control_id')
        
        return {{
            "test_id": f"{control_id}-negative-001",
            "test_name": f"Violation scenario: {control.get('title')}",
            "control_id": control_id,
            "description": f"Negative test: Authorization requirement violated",
            "context": {{
                "actor_type": "unauthorized_user",
                "action": "access_resource",
                "metadata": {{
                    "timestamp": datetime.now().isoformat(),
                    "authorized": False,
                }}
            }},
            "data": {{
                "approved_actors": ["authorized_user", "admin"],
            }},
            "expected_result": "FAIL",
            "expected_decision": "DENY",
            "expected_compliance_score": 66.67,
            "expected_violations": ["VIOLATION: Actor not authorized per control requirement"],
            "notes": f"Authorization check failed for control: {control_id}",
        }}
    
    def _extract_keywords_from_statement(self, statement: str) -> List[str]:
        """Extract key policy concepts from control statement"""
        # Simple keyword extraction
        keywords = []
        
        requirement_words = [
            'must', 'shall', 'should', 'required',
            'authorized', 'registered', 'approved',
            'verified', 'assigned', 'valid'
        ]
        
        statement_lower = statement.lower()
        for word in requirement_words:
            if word in statement_lower:
                keywords.append(word)
        
        return list(set(keywords))
    
    def _format_multiline_comment(self, text: str, width: int = 75) -> str:
        """Format text for multiline comments"""
        lines = []
        for line in text.split('\n'):
            if len(line) > width:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= width:
                        current_line += word + " "
                    else:
                        if current_line:
                            lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    lines.append(current_line.strip())
            else:
                lines.append(line)
        
        return "\n# ".join(lines)
    
    def save_policy_artifacts(self, artifacts: PolicyArtifacts) -> Path:
        """Save policy artifacts to disk"""
        policy_version = "v1-0"
        output_dir = self.policy_dir / f"{artifacts.control_id}-{policy_version}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Rego policy
        rego_file = output_dir / "policy.rego"
        rego_file.write_text(artifacts.policy_rego, encoding='utf-8')
        print(f"  ✓ Saved {rego_file}")
        
        # Save Python evaluator
        py_file = output_dir / "evaluator.py"
        py_file.write_text(artifacts.evaluator_py, encoding='utf-8')
        print(f"  ✓ Saved {py_file}")
        
        # Save positive test
        pos_test_file = output_dir / "positive_test.json"
        pos_test_file.write_text(json.dumps(artifacts.positive_test, indent=2), encoding='utf-8')
        print(f"  ✓ Saved {pos_test_file}")
        
        # Save negative test
        neg_test_file = output_dir / "negative_test.json"
        neg_test_file.write_text(json.dumps(artifacts.negative_test, indent=2), encoding='utf-8')
        print(f"  ✓ Saved {neg_test_file}")
        
        # Save metadata
        meta_file = output_dir / "metadata.json"
        meta_file.write_text(json.dumps(artifacts.metadata, indent=2), encoding='utf-8')
        print(f"  ✓ Saved {meta_file}")
        
        return output_dir
    
    def generate_all_policies(self) -> Dict[str, Path]:
        """Generate policies for all controls"""
        print("\n" + "=" * 80)
        print("🔧 GENERATING POLICIES FOR ALL CONTROLS")
        print("=" * 80)
        
        results = {}
        for control_id in sorted(self.controls.keys()):
            artifacts = self.generate_policy_for_control(control_id)
            if artifacts:
                output_dir = self.save_policy_artifacts(artifacts)
                results[control_id] = output_dir
        
        print(f"\n✅ Generated {len(results)} policy packages")
        return results
    
    def generate_specific_policies(self, control_ids: List[str]) -> Dict[str, Path]:
        """Generate policies for specific controls"""
        results = {}
        for control_id in control_ids:
            artifacts = self.generate_policy_for_control(control_id)
            if artifacts:
                output_dir = self.save_policy_artifacts(artifacts)
                results[control_id] = output_dir
        
        return results


def main():
    """Demo: Generate policies from control definitions"""
    try:
        generator = PolicyGenerator("level1/controls.yaml")
        
        # Generate policies for first 3 controls
        demo_controls = ["SCF-001", "SCF-002", "SCF-003"]
        results = generator.generate_specific_policies(demo_controls)
        
        print("\n" + "=" * 80)
        print("✅ POLICY GENERATION COMPLETE")
        print("=" * 80)
        for control_id, output_dir in results.items():
            print(f"  • {control_id}: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
