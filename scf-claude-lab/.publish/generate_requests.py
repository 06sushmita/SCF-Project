import json
import yaml
from pathlib import Path

def main():
    print("Generating request JSONs dynamically...")
    
    # 1. Read controls.yaml
    yaml_path = Path("level1/controls.yaml")
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found")
        return
        
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if not data or "controls" not in data or len(data["controls"]) == 0:
        print("Error: No controls found in level1/controls.yaml")
        return
        
    first_control = data["controls"][0]
    control_id = first_control.get("control_id", "SCF-001")
    
    # 2. Read level3/tests.json
    tests_json = Path("level3/tests.json")
    context = None
    if tests_json.exists():
        with open(tests_json, "r", encoding="utf-8") as f:
            tests_data = json.load(f)
            
        # Find context for this control
        for test in tests_data.get("tests", []):
            if test.get("test_id", "").startswith(f"{control_id}-pass") or test.get("test_id", "").startswith(f"{control_id}-positive"):
                context = test.get("context")
                break
                
    if not context:
        print(f"Warning: No positive test context found for {control_id} in {tests_json}, using fallback.")
        context = {
            "actor_type": "authorized_user",
            "action": "execute",
            "metadata": {"authorized": True}
        }
        
    # Create validate_request.json
    validate_payload = {
        "control_id": control_id,
        "context": context,
        "policy_type": "python"
    }
    with open("validate_request.json", "w", encoding="utf-8") as f:
        json.dump(validate_payload, f, indent=2)
    print("✓ Created validate_request.json from level1/controls.yaml and level3/tests.json")
        
    # Create test_request.json
    test_payload = {
        "control_id": control_id,
        "run_positive_tests": True,
        "run_negative_tests": True
    }
    with open("test_request.json", "w", encoding="utf-8") as f:
        json.dump(test_payload, f, indent=2)
    print("✓ Created test_request.json mapped to the derived control.")

if __name__ == "__main__":
    main()
