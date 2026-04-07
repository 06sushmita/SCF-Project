"""
LEVEL 3 - Policy-as-Code Generator
Converts controls to executable policies
Single source of truth: level1/controls.yaml
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class PolicyGenerator:
    """Level 3: Generate policies from control.yaml"""
    
    def __init__(self, yaml_path: str = None):
        if yaml_path is None:
            # Construct path relative to script location
            script_dir = Path(__file__).parent.parent  # Go to scf-claude-lab
            yaml_path = script_dir / "level1" / "controls.yaml"
        self.yaml_path = Path(yaml_path)
        self.controls = self._load_controls()
        # Output to level3 directory (at project root)
        script_dir = Path(__file__).parent.parent
        self.output_dir = script_dir / "level3"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tests_dir = self.output_dir / "tests"
        self.tests_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_controls(self) -> Dict[str, Any]:
        """Load controls from control.yaml"""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"control.yaml not found: {self.yaml_path}")
        
        with open(self.yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        controls_dict = {}
        for control in data.get('controls', []):
            control_id = control.get('control_id')
            controls_dict[control_id] = control
        
        return controls_dict
    
    
    def generate_test_cases(self, control: Dict[str, Any]) -> tuple:
        """Generate positive and negative test cases"""
        control_id = control.get('control_id')
        statement = control.get('control_statement', '')
        
        positive = {
            "test_id": f"{control_id}-pass",
            "test_name": f"Compliant: {control.get('title')}",
            "context": {
                "actor_type": "authorized_user",
                "metadata": {"authorized": True}
            },
            "expected": "PASS",
            "statement_verified": statement[:80]
        }
        
        negative = {
            "test_id": f"{control_id}-fail",
            "test_name": f"Violation: {control.get('title')}",
            "context": {
                "actor_type": "unauthorized_user",
                "metadata": {"authorized": False}
            },
            "expected": "FAIL",
            "statement_verified": statement[:80]
        }
        
        return positive, negative
    
    def generate_consolidated_rego(self) -> Path:
        """Generate single consolidated policy.rego with all policies"""
        rego_content = '''# ============================================================================
# SCF - Secure Control Framework
# Consolidated Policies
# Generated: {generated_at}
# ============================================================================

package scf

import future.keywords

# ============================================================================
# CONTROL DEFINITIONS
# ============================================================================

'''.format(generated_at=datetime.now().isoformat())
        
        # Add all control policies with proper package separation
        control_repos = []
        for control_id in sorted(self.controls.keys()):
            control = self.controls[control_id]
            control_repos.append(f"\n# {control_id}: {control.get('title', '')}\n")
            control_repos.append(self._generate_control_rule(control))
        
        rego_content += "\n".join(control_repos)
        
        # Write consolidated policy file
        policy_file = self.output_dir / "policy.rego"
        policy_file.write_text(rego_content, encoding='utf-8')
        
        return policy_file
    
    def _generate_control_rule(self, control: Dict[str, Any]) -> str:
        """Generate a single control rule for consolidated policy"""
        control_id = control.get('control_id')
        title = control.get('title', '')
        control_type = control.get('control_type', '')
        domain = control.get('control_domain', '')
        statement = control.get('control_statement', '')
        
        rule = f'''
{control_id}_allow if {{
    input.context != null
    input.context.actor_type != null
    {control_id}_is_authorized
}}

{control_id}_deny if {{
    not {control_id}_allow
}}

{control_id}_is_authorized if {{
    input.context.metadata.authorized == true
}}

{control_id}_decision := {{
    "control_id": "{control_id}",
    "title": "{title}",
    "type": "{control_type}",
    "domain": "{domain}",
    "decision": {control_id}_allow ? "ALLOW" : "DENY",
    "result": {control_id}_allow ? "PASS" : "FAIL",
    "compliance_score": {control_id}_allow ? 100 : 0,
}}
'''
        return rule.strip()
    
    def generate_consolidated_tests(self) -> Path:
        """Generate single consolidated test file with all test cases"""
        all_tests = []
        
        for control_id in sorted(self.controls.keys()):
            control = self.controls[control_id]
            pos_test, neg_test = self.generate_test_cases(control)
            
            # Add both positive and negative tests
            all_tests.append(pos_test)
            all_tests.append(neg_test)
        
        # Create consolidated test structure
        test_data = {
            "test_suite": "SCF Control Compliance Tests",
            "description": "Consolidated test cases for all SCF controls",
            "total_tests": len(all_tests),
            "generated_at": datetime.now().isoformat(),
            "tests": all_tests
        }
        
        # Write consolidated test file
        test_file = self.output_dir / "tests.json"
        test_file.write_text(json.dumps(test_data, indent=2), encoding='utf-8')
        
        return test_file
    
    def generate_test_file(self, control_id: str) -> Path:
        """Generate test file with positive and negative test cases (deprecated - use consolidated)"""
        if control_id not in self.controls:
            raise ValueError(f"Control not found: {control_id}")
        
        control = self.controls[control_id]
        pos_test, neg_test = self.generate_test_cases(control)
        
        tests = {
            "control_id": control_id,
            "title": control.get('title'),
            "tests": [pos_test, neg_test]
        }
        
        test_file = self.tests_dir / f"{control_id}_tests.json"
        test_file.write_text(json.dumps(tests, indent=2), encoding='utf-8')
        
        return test_file
    
    def generate_api_requests(self) -> tuple:
        """Generate validate_request.json and test_request.json for the API"""
        if not self.controls:
            raise ValueError("No controls available to generate requests from.")
            
        # Get the first control
        first_control_id = sorted(self.controls.keys())[0]
        control = self.controls[first_control_id]
        
        # Get positive context for test
        pos_test, _ = self.generate_test_cases(control)
        
        validate_payload = {
            "control_id": first_control_id,
            "context": pos_test["context"],
            "policy_type": "python"
        }
        test_payload = {
            "control_id": first_control_id,
            "run_positive_tests": True,
            "run_negative_tests": True
        }
        
        validate_file = self.output_dir / "validate_request.json"
        validate_file.write_text(json.dumps(validate_payload, indent=2), encoding="utf-8")
        
        test_file = self.output_dir / "test_request.json"
        test_file.write_text(json.dumps(test_payload, indent=2), encoding="utf-8")
        
        return validate_file, test_file
        
    def generate_all(self) -> Dict[str, Path]:
        """Generate consolidated policy.rego and tests.json for all controls"""
        print(f"\n🔧 LEVEL 3: GENERATING CONSOLIDATED POLICIES FROM {self.yaml_path}")
        print("=" * 80)
        
        results = {}
        
        # Generate consolidated policy.rego
        try:
            policy_file = self.generate_consolidated_rego()
            results['policy.rego'] = policy_file
            print(f"✓ Consolidated policy.rego generated: {policy_file}")
        except Exception as e:
            print(f"❌ Error generating policy.rego: {e}")
        
        # Generate consolidated tests.json
        try:
            test_file = self.generate_consolidated_tests()
            results['tests.json'] = test_file
            print(f"✓ Consolidated tests.json generated: {test_file}")
        except Exception as e:
            print(f"❌ Error generating tests.json: {e}")
            
        # Generate API request bindings
        try:
            val_req, test_req = self.generate_api_requests()
            results['validate_request.json'] = val_req
            results['test_request.json'] = test_req
            print(f"✓ API Request templates generated: {val_req.name}, {test_req.name}")
        except Exception as e:
            print(f"❌ Error generating API requests: {e}")
        
        return results


def main():
    try:
        generator = PolicyGenerator()  # Use smart path resolution
        results = generator.generate_all()
        
        print(f"\n✅ Generated consolidated policies and tests")
        print(f"Policy: level3/policy.rego")
        print(f"Tests: level3/tests.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
