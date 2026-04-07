"""
LEVEL 2 - Control Registry
Manages controls as versioned, governed assets
Single source of truth: level1/controls.yaml
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum


class LifecycleState(str, Enum):
    """Control lifecycle states"""
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


@dataclass
class ControlVersion:
    version: str
    created_at: str
    created_by: str
    changes: str


@dataclass
class RegistryEntry:
    """Control from control.yaml with versioning"""
    control_id: str
    title: str
    control_statement: str
    objective: str
    control_type: str
    control_domain: str
    control_family: str
    current_version: str = "1.0"
    lifecycle_state: str = "draft"
    versions: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ControlRegistry:
    """Level 2: Control Registry - reads from control.yaml"""
    
    def __init__(self, yaml_path: str = None):
        if yaml_path is None:
            # Construct path relative to script location
            script_dir = Path(__file__).parent.parent  # Go to scf-claude-lab
            yaml_path = script_dir / "level1" / "controls.yaml"
        self.yaml_path = Path(yaml_path)
        self.registry: Dict[str, RegistryEntry] = {}
        self.load_from_yaml()
    
    def load_from_yaml(self):
        """Load controls from control.yaml (single source of truth)"""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"control.yaml not found: {self.yaml_path}")
        
        with open(self.yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        controls = data.get('controls', [])
        print(f"\n📖 LEVEL 2: LOADING {len(controls)} CONTROLS FROM {self.yaml_path}")
        print("=" * 80)
        
        for control in controls:
            control_id = control.get('control_id')
            entry = RegistryEntry(
                control_id=control_id,
                title=control.get('title', ''),
                control_statement=control.get('control_statement', ''),
                objective=control.get('objective', ''),
                control_type=control.get('control_type', ''),
                control_domain=control.get('control_domain', ''),
                control_family=control.get('control_family', ''),
                versions=[{
                    'version': '1.0',
                    'created_at': datetime.now().isoformat(),
                    'created_by': 'system',
                    'changes': 'Initial version from control.yaml'
                }]
            )
            self.registry[control_id] = entry
    
    def set_lifecycle(self, control_id: str, state: str) -> bool:
        """Update lifecycle state"""
        if control_id not in self.registry:
            return False
        self.registry[control_id].lifecycle_state = state
        return True
    
    def get_by_domain(self, domain: str) -> List[RegistryEntry]:
        """Search controls by domain"""
        return [e for e in self.registry.values() 
                if domain.lower() in e.control_domain.lower()]
    
    def export_registry(self, output_file: str = None):
        """Export registry to JSON"""
        if output_file is None:
            # Construct path relative to script location
            script_dir = Path(__file__).parent.parent  # Go to scf-claude-lab
            output_file = script_dir / "controls" / "registry_level2.json"
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        registry_data = {
            cid: asdict(entry) 
            for cid, entry in self.registry.items()
        }
        
        with open(output_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
        
        return output_file
    
    def print_summary(self):
        """Print registry summary"""
        by_domain = {}
        by_state = {}
        
        for entry in self.registry.values():
            domain = entry.control_domain
            by_domain[domain] = by_domain.get(domain, 0) + 1
            state = entry.lifecycle_state
            by_state[state] = by_state.get(state, 0) + 1
        
        print(f"\n✅ Total Controls: {len(self.registry)}")
        print(f"Source: {self.yaml_path}\n")
        
        print("📊 BY DOMAIN:")
        for domain, count in sorted(by_domain.items()):
            print(f"  • {domain}: {count}")
        
        print("\n📊 BY LIFECYCLE STATE:")
        for state, count in sorted(by_state.items()):
            print(f"  • {state}: {count}")


def main():
    try:
        registry = ControlRegistry()  # Use smart path resolution
        registry.print_summary()
        
        # Update some to approved
        registry.set_lifecycle("SCF-001", "approved")
        registry.set_lifecycle("SCF-002", "active")
        
        # Export
        output = registry.export_registry()
        print(f"\n✓ Registry exported to {output}")
        
        # Search example
        print("\n🔍 Access Control Domain Controls:")
        ac_controls = registry.get_by_domain("Access Control")
        for c in ac_controls[:3]:
            print(f"  • {c.control_id}: {c.title}")
            print(f"    Statement: {c.control_statement[:60]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
