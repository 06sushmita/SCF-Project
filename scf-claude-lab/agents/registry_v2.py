"""
Level 2 - Control Registry
Manages controls as versioned, governed assets with lifecycle tracking.

Single Source of Truth: control.yaml (level1/controls.yaml)
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
    RETIRED = "retired"


@dataclass
class ControlVersion:
    """Single version of a control"""
    version: str
    created_at: str
    created_by: str
    changes: str
    active: bool = True


@dataclass
class RegistryEntry:
    """Control registry entry with full metadata and version history"""
    control_id: str
    title: str
    description: str
    domain: str
    control_family: str
    owner: str
    control_type: str  # Preventive, Detective, Corrective
    current_version: str
    lifecycle_state: LifecycleState
    versions: List[ControlVersion] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    control_statement: str = ""
    objective: str = ""
    risk_addressed: str = ""
    evidence_required: str = ""
    metrics: str = ""
    assumptions: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['lifecycle_state'] = self.lifecycle_state.value
        data['versions'] = [asdict(v) for v in self.versions]
        return data


class ControlRegistry:
    """
    Level 2: Control Registry
    Manages controls as versioned, governed assets
    """
    
    def __init__(self, controls_yaml_path: str = "level1/controls.yaml"):
        """Initialize registry and load controls from YAML"""
        self.controls_yaml_path = Path(controls_yaml_path)
        self.registry: Dict[str, RegistryEntry] = {}
        self.version_history: Dict[str, List[ControlVersion]] = {}
        self.lifecycle_db_path = Path("controls/registry_state.json")
        
        # Load controls from YAML
        self.load_controls_from_yaml()
        
        # Load lifecycle state from persistent storage if exists
        self.load_lifecycle_state()
    
    def load_controls_from_yaml(self):
        """Load controls from control.yaml (single source of truth)"""
        if not self.controls_yaml_path.exists():
            raise FileNotFoundError(f"Controls file not found: {self.controls_yaml_path}")
        
        with open(self.controls_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        controls = data.get('controls', [])
        print(f"📖 Loading {len(controls)} controls from {self.controls_yaml_path}")
        
        for control_data in controls:
            self._register_control_from_yaml(control_data)
    
    def _register_control_from_yaml(self, control_data: Dict[str, Any]):
        """Register a single control from YAML data"""
        control_id = control_data.get('control_id')
        
        # Create initial version
        initial_version = ControlVersion(
            version="1.0",
            created_at=datetime.now().isoformat(),
            created_by="system",
            changes="Initial version from control.yaml",
            active=True
        )
        
        # Create registry entry
        entry = RegistryEntry(
            control_id=control_id,
            title=control_data.get('title', ''),
            description=control_data.get('title', ''),  # Use title as description initially
            domain=control_data.get('control_domain', ''),
            control_family=control_data.get('control_family', ''),
            owner=control_data.get('owner', 'Unassigned'),
            control_type=control_data.get('control_type', ''),
            current_version="1.0",
            lifecycle_state=LifecycleState.DRAFT,  # Default to draft
            versions=[initial_version],
            control_statement=control_data.get('control_statement', ''),
            objective=control_data.get('objective', ''),
            risk_addressed=control_data.get('risk_addressed', ''),
            evidence_required=control_data.get('evidence_required', ''),
            metrics=control_data.get('metrics', ''),
            assumptions=control_data.get('assumptions', ''),
        )
        
        self.registry[control_id] = entry
        self.version_history[control_id] = [initial_version]
    
    def load_lifecycle_state(self):
        """Load lifecycle states from persistent storage"""
        if self.lifecycle_db_path.exists():
            with open(self.lifecycle_db_path, 'r') as f:
                data = json.load(f)
            
            for control_id, state in data.items():
                if control_id in self.registry:
                    self.registry[control_id].lifecycle_state = LifecycleState(state)
    
    def save_lifecycle_state(self):
        """Save lifecycle states to persistent storage"""
        self.lifecycle_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        lifecycle_data = {
            control_id: entry.lifecycle_state.value
            for control_id, entry in self.registry.items()
        }
        
        with open(self.lifecycle_db_path, 'w') as f:
            json.dump(lifecycle_data, f, indent=2)
    
    def get_control(self, control_id: str) -> Optional[RegistryEntry]:
        """Retrieve control by ID"""
        return self.registry.get(control_id)
    
    def get_controls_by_domain(self, domain: str) -> List[RegistryEntry]:
        """Search controls by domain (case-insensitive)"""
        domain_lower = domain.lower()
        return [
            entry for entry in self.registry.values()
            if domain_lower in entry.domain.lower()
        ]
    
    def get_controls_by_lifecycle_state(self, state: LifecycleState) -> List[RegistryEntry]:
        """Get all controls with a specific lifecycle state"""
        return [
            entry for entry in self.registry.values()
            if entry.lifecycle_state == state
        ]
    
    def set_lifecycle_state(self, control_id: str, new_state: LifecycleState) -> bool:
        """Update lifecycle state of a control"""
        if control_id not in self.registry:
            return False
        
        entry = self.registry[control_id]
        old_state = entry.lifecycle_state
        entry.lifecycle_state = new_state
        entry.updated_at = datetime.now().isoformat()
        
        print(f"✓ {control_id}: {old_state.value} → {new_state.value}")
        self.save_lifecycle_state()
        return True
    
    def create_new_version(self, control_id: str, changes: str, created_by: str = "system") -> bool:
        """Create a new version of a control"""
        if control_id not in self.registry:
            return False
        
        entry = self.registry[control_id]
        old_version_num = entry.current_version
        
        # Parse version (e.g., "1.0" -> "1.1")
        major, minor = map(int, old_version_num.split('.'))
        new_version = f"{major}.{minor + 1}"
        
        new_version_obj = ControlVersion(
            version=new_version,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            changes=changes,
            active=True
        )
        
        entry.versions.append(new_version_obj)
        entry.current_version = new_version
        entry.updated_at = datetime.now().isoformat()
        
        print(f"✓ {control_id}: Version {old_version_num} → {new_version}")
        return True
    
    def get_version_history(self, control_id: str) -> Optional[List[Dict]]:
        """Get full version history for a control"""
        if control_id not in self.registry:
            return None
        
        entry = self.registry[control_id]
        return [asdict(v) for v in entry.versions]
    
    def export_registry(self, output_file: str = "controls/registry.json"):
        """Export entire registry to JSON"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        registry_data = {
            control_id: entry.to_dict()
            for control_id, entry in self.registry.items()
        }
        
        with open(output_path, 'w') as f:
            json.dump(registry_data, f, indent=2)
        
        print(f"✓ Registry exported to {output_path}")
        return output_path
    
    def get_summary(self) -> Dict[str, Any]:
        """Get registry summary statistics"""
        total = len(self.registry)
        by_domain = {}
        by_state = {}
        
        for entry in self.registry.values():
            # Count by domain
            domain = entry.domain
            by_domain[domain] = by_domain.get(domain, 0) + 1
            
            # Count by lifecycle state
            state = entry.lifecycle_state.value
            by_state[state] = by_state.get(state, 0) + 1
        
        return {
            "total_controls": total,
            "by_domain": by_domain,
            "by_lifecycle_state": by_state,
            "loaded_from": str(self.controls_yaml_path),
        }
    
    def print_summary(self):
        """Print registry summary to console"""
        summary = self.get_summary()
        
        print("\n" + "=" * 80)
        print("📊 CONTROL REGISTRY SUMMARY")
        print("=" * 80)
        print(f"Total Controls Loaded: {summary['total_controls']}")
        print(f"Source: {summary['loaded_from']}")
        print()
        
        print("Controls by Domain:")
        for domain, count in sorted(summary['by_domain'].items()):
            print(f"  • {domain}: {count}")
        print()
        
        print("Controls by Lifecycle State:")
        for state, count in sorted(summary['by_lifecycle_state'].items()):
            print(f"  • {state}: {count}")
        print()
    
    def list_all(self):
        """List all controls in registry"""
        print("\n" + "=" * 80)
        print("📋 CONTROL REGISTRY")
        print("=" * 80)
        
        # Group by domain
        by_domain = {}
        for entry in self.registry.values():
            if entry.domain not in by_domain:
                by_domain[entry.domain] = []
            by_domain[entry.domain].append(entry)
        
        for domain in sorted(by_domain.keys()):
            print(f"\n{domain}")
            print("-" * 80)
            
            for entry in by_domain[domain]:
                lifecycle_badge = {
                    LifecycleState.DRAFT: "📝",
                    LifecycleState.APPROVED: "✅",
                    LifecycleState.ACTIVE: "🔄",
                    LifecycleState.DEPRECATED: "⚠️",
                    LifecycleState.RETIRED: "❌",
                }
                
                badge = lifecycle_badge.get(entry.lifecycle_state, "•")
                print(f"  {badge} {entry.control_id} (v{entry.current_version}) [{entry.lifecycle_state.value}]")
                print(f"     {entry.title}")


def main():
    """Demo: Load registry and show contents"""
    try:
        registry = ControlRegistry("level1/controls.yaml")
        
        # Print summary
        registry.print_summary()
        
        # List all controls
        registry.list_all()
        
        # Example: Get controls by domain
        print("\n" + "=" * 80)
        print("🔍 SEARCH BY DOMAIN: 'Access Control'")
        print("=" * 80)
        ac_controls = registry.get_controls_by_domain("Access Control")
        for entry in ac_controls:
            print(f"  • {entry.control_id}: {entry.title}")
        
        # Example: Update lifecycle state
        print("\n" + "=" * 80)
        print("🔄 UPDATING LIFECYCLE STATES")
        print("=" * 80)
        registry.set_lifecycle_state("SCF-001", LifecycleState.APPROVED)
        registry.set_lifecycle_state("SCF-002", LifecycleState.ACTIVE)
        registry.set_lifecycle_state("SCF-003", LifecycleState.APPROVED)
        
        # Example: Show version history
        print("\n" + "=" * 80)
        print("📜 VERSION HISTORY: SCF-001")
        print("=" * 80)
        history = registry.get_version_history("SCF-001")
        for version in history:
            print(f"  v{version['version']} ({version['created_at']}): {version['changes']}")
        
        # Export registry
        print("\n" + "=" * 80)
        print("💾 EXPORTING REGISTRY")
        print("=" * 80)
        registry.export_registry("controls/registry.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
