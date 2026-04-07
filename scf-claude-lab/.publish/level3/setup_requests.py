import json
import yaml
from pathlib import Path

def main():
    print("Generating request JSONs dynamically in level3...")
    
    yaml_path = Path("level1/controls.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    first_control = data["controls"][0]
    control_id = first_control.get("control_id", "SCF-001")
    
    tests_json = Path("level3/tests.json")
    context = None
    if tests_json.exists():
        with open(tests_json, "r", encoding="utf-8") as f:
            tests_data = json.load(f)
            
        for test in tests_data.get("tests", []):
            if test.get("test_id", "").startswith(f"{control_id}-pass") or test.get("test_id", "").startswith(f"{control_id}-positive"):
                context = test.get("context")
                break
                
    if not context:
        context = {
            "actor_type": "authorized_user",
            "metadata": {"authorized": True}
        }
        
    validate_payload = {
        "control_id": control_id,
        "context": context,
        "policy_type": "python"
    }
    with open("level3/validate_request.json", "w", encoding="utf-8") as f:
        json.dump(validate_payload, f, indent=2)
        
    test_payload = {
        "control_id": control_id,
        "run_positive_tests": True,
        "run_negative_tests": True
    }
    with open("level3/test_request.json", "w", encoding="utf-8") as f:
        json.dump(test_payload, f, indent=2)
        
    print("Generated validate_request.json and test_request.json in level3/")

if __name__ == "__main__":
    main()
