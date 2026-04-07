"""
agents/registry.py
RegistryAgent: Manages control versioning, lifecycle, and search.
Provides immutable audit trail and fast lookup.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from .models import (
    Control, ControlVersion, ControlStatus, AuditRecord,
    ControlSearchResult, RegistryMetadata, ControlDomain, ControlType
)


class RegistryAgent:
    """
    Manages the control registry with full versioning and lifecycle support.
    
    Features:
    - Immutable version history (append-only)
    - Lifecycle state management (draft → active → deprecated)
    - Full-text search with tagging
    - JSON-based persistence (no external DB required)
    - Complete audit trail for compliance
    """
    
    def __init__(self, registry_path: str = "controls/controls_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.controls: Dict[str, Control] = {}
        self.audit_log: List[Dict] = []
        self._load_registry()
    
    # ─────────────────────────────────────────────────────────────────────────
    # PERSISTENCE LAYER
    # ─────────────────────────────────────────────────────────────────────────
    
    def _load_registry(self) -> None:
        """Load registry from disk."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for control_data in data.get('controls', []):
                    control = Control.from_dict(control_data)
                    self.controls[control.control_id] = control
        else:
            self.controls = {}
    
    def _save_registry(self) -> None:
        """Persist registry to disk (atomic)."""
        registry_data = {
            "registry_version": "2.0",
            "last_updated": datetime.now().isoformat(),
            "total_controls": len(self.controls),
            "controls": [c.to_dict() for c in self.controls.values()],
        }
        
        # Write to temp file first, then atomic rename
        temp_path = self.registry_path.parent / f"{self.registry_path.name}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)
        temp_path.replace(self.registry_path)
    
    def _record_audit_event(self, event_type: str, control_id: str, 
                           actor: str, reason: Optional[str] = None,
                           details: Optional[Dict] = None) -> Dict:
        """Create an immutable audit record."""
        event = {
            "event_id": f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.audit_log):06d}",
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "control_id": control_id,
            "actor": actor,
            "reason": reason,
            "details": details or {},
        }
        self.audit_log.append(event)
        return event
    
    # ─────────────────────────────────────────────────────────────────────────
    # CONTROL REGISTRY OPERATIONS (CRUD)
    # ─────────────────────────────────────────────────────────────────────────
    
    def create_control(self, control_version: ControlVersion, actor: str,
                       reason: str = "Initial control creation") -> Control:
        """
        Create a new control with initial version (1.0).
        Status defaults to 'draft' pending approval.
        """
        if control_version.control_id in self.controls:
            raise ValueError(f"Control {control_version.control_id} already exists")
        
        if control_version.version != "1.0":
            raise ValueError("First version must be 1.0")
        
        # Create initial audit record
        control_version.audit_trail.append(AuditRecord(
            timestamp=datetime.now().isoformat(),
            actor=actor,
            action="created",
            reason=reason,
        ))
        
        # Create control and add version
        control = Control(control_id=control_version.control_id)
        control.add_version(control_version)
        self.controls[control.control_id] = control
        
        # Record audit event
        self._record_audit_event(
            "control_created",
            control_version.control_id,
            actor,
            reason=reason,
            details={"version": "1.0", "status": "draft"}
        )
        
        self._save_registry()
        return control
    
    def update_control(self, control_id: str, changes: Dict, 
                      actor: str, reason: str = "Version update") -> ControlVersion:
        """
        Create a new minor version (e.g., 1.0 → 1.1) with specified changes.
        Original version remains unchanged (immutable).
        """
        control = self.get_control(control_id)
        if not control:
            raise ValueError(f"Control {control_id} not found")
        
        current = control.get_active_version()
        if not current:
            raise ValueError(f"No active version for {control_id}")
        
        # Calculate new version number (minor bump)
        major, minor = map(int, current.version.split('.'))
        new_version_str = f"{major}.{minor + 1}"
        
        # Create new version with merged fields
        new_version_dict = current.to_dict()
        new_version_dict.update(changes)
        new_version_dict['version'] = new_version_str
        new_version_dict['created_date'] = datetime.now().isoformat()
        new_version_dict['created_by'] = actor
        new_version_dict['amended_from_version'] = current.version
        new_version_dict['amendment_reason'] = reason
        new_version_dict['audit_trail'] = []  # Fresh audit trail for this version
        
        # Convert back to ControlVersion object
        new_version = ControlVersion.from_dict(new_version_dict)
        new_version.audit_trail.append(AuditRecord(
            timestamp=datetime.now().isoformat(),
            actor=actor,
            action="updated",
            reason=reason,
            changes=changes,
        ))
        
        # Add version
        control.add_version(new_version)
        
        # Record audit event
        self._record_audit_event(
            "control_updated",
            control_id,
            actor,
            reason=reason,
            details={"new_version": new_version_str, "changes": changes}
        )
        
        self._save_registry()
        return new_version
    
    def activate_control(self, control_id: str, version: Optional[str] = None,
                        actor: str = "system", reason: str = "Activated") -> ControlVersion:
        """
        Transition a control version from 'draft' to 'active'.
        Only one version can be active at a time.
        """
        control = self.get_control(control_id)
        if not control:
            raise ValueError(f"Control {control_id} not found")
        
        # Deactivate current active version
        current_active = control.get_active_version()
        if current_active:
            current_active.status = ControlStatus.ACTIVE
            # Keep it active until we activate the new one
        
        # Get target version (specified or latest)
        if version:
            target = control.get_version(version)
            if not target:
                raise ValueError(f"Version {version} not found for {control_id}")
        else:
            # Activate the latest draft
            drafts = [v for v in control.versions if v.status == ControlStatus.DRAFT]
            if not drafts:
                raise ValueError(f"No draft versions available for {control_id}")
            target = drafts[-1]  # Latest draft
        
        # Transition to active
        target.status = ControlStatus.ACTIVE
        target.audit_trail.append(AuditRecord(
            timestamp=datetime.now().isoformat(),
            actor=actor,
            action="activated",
            reason=reason,
        ))
        
        # Ensure only one active version
        for v in control.versions:
            if v != target and v.status == ControlStatus.ACTIVE:
                v.status = ControlStatus.DEPRECATED
                v.audit_trail.append(AuditRecord(
                    timestamp=datetime.now().isoformat(),
                    actor="system",
                    action="deprecated",
                    reason=f"Superseded by version {target.version}",
                ))
        
        # Record audit event
        self._record_audit_event(
            "control_activated",
            control_id,
            actor,
            reason=reason,
            details={"version": target.version}
        )
        
        self._save_registry()
        return target
    
    def deprecate_control(self, control_id: str, version: Optional[str] = None,
                         actor: str = "system", reason: str = "Deprecated") -> bool:
        """Mark a control or version as deprecated."""
        control = self.get_control(control_id)
        if not control:
            return False
        
        if version:
            v = control.get_version(version)
            if not v:
                return False
            v.status = ControlStatus.DEPRECATED
        else:
            # Deprecate the active version
            active = control.get_active_version()
            if active:
                active.status = ControlStatus.DEPRECATED
        
        # Record audit
        self._record_audit_event(
            "control_deprecated",
            control_id,
            actor,
            reason=reason,
        )
        
        self._save_registry()
        return True
    
    # ─────────────────────────────────────────────────────────────────────────
    # LOOKUP & RETRIEVAL
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_control(self, control_id: str) -> Optional[Control]:
        """Retrieve a control by ID."""
        return self.controls.get(control_id)
    
    def get_control_version(self, control_id: str, 
                           version: str = "active") -> Optional[ControlVersion]:
        """
        Get a specific control version.
        version: "1.0", "1.1", "active" (default), "latest", etc.
        """
        control = self.get_control(control_id)
        if not control:
            return None
        
        if version == "active":
            return control.get_active_version()
        elif version == "latest":
            return control.versions[-1] if control.versions else None
        else:
            return control.get_version(version)
    
    def get_all_controls(self, status: Optional[ControlStatus] = None) -> List[Control]:
        """Get all controls, optionally filtered by status."""
        if status is None:
            return list(self.controls.values())
        
        return [
            c for c in self.controls.values()
            if c.get_active_version()
            and c.get_active_version().status == status
        ]
    
    def get_control_history(self, control_id: str) -> List[ControlVersion]:
        """Get all versions of a control in chronological order."""
        control = self.get_control(control_id)
        return control.versions if control else []
    
    # ─────────────────────────────────────────────────────────────────────────
    # SEARCH & FILTERING
    # ─────────────────────────────────────────────────────────────────────────
    
    def search(self, query: str = "", domain: Optional[str] = None,
              control_type: Optional[str] = None,
              status: Optional[str] = None,
              exact_match: bool = False) -> List[ControlSearchResult]:
        """
        Full-text search with filtering.
        
        Args:
            query: Search term (searches title, objective, tags)
            domain: Filter by control domain
            control_type: Filter by control type (Preventive/Detective/Corrective)
            status: Filter by status (draft/active/deprecated)
            exact_match: If True, only match exact query strings
        
        Returns:
            List of matching controls with relevance scores
        """
        results = []
        query_lower = query.lower()
        
        for control_id, control in self.controls.items():
            # Get active version (or latest if no active)
            version = control.get_active_version()
            if not version:
                version = control.versions[-1] if control.versions else None
            
            if not version:
                continue
            
            # Apply status filter
            if status and version.status.value != status:
                continue
            
            # Apply domain filter
            if domain and version.control_domain.value != domain:
                continue
            
            # Apply type filter
            if control_type and version.control_type.value != control_type:
                continue
            
            # Calculate relevance score
            relevance = 0.0
            if query:
                # Title match (highest weight)
                if exact_match:
                    if query_lower == version.title.lower():
                        relevance = 1.0
                else:
                    if query_lower in version.title.lower():
                        relevance += 0.5
                    # Objective match (medium weight)
                    if query_lower in version.objective.lower():
                        relevance += 0.3
                    # Tag match (low weight)
                    if any(query_lower in tag.lower() for tag in control.search_tags):
                        relevance += 0.2
                
                if relevance > 0:
                    results.append(ControlSearchResult(
                        control_id=control_id,
                        title=version.title,
                        version=version.version,
                        status=version.status.value,
                        domain=version.control_domain.value,
                        control_type=version.control_type.value,
                        relevance_score=min(relevance, 1.0),
                    ))
            else:
                # No query = include all matching filters
                results.append(ControlSearchResult(
                    control_id=control_id,
                    title=version.title,
                    version=version.version,
                    status=version.status.value,
                    domain=version.control_domain.value,
                    control_type=version.control_type.value,
                    relevance_score=1.0,
                ))
        
        # Sort by relevance (descending)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results
    
    def search_by_domain(self, domain: str) -> List[ControlSearchResult]:
        """Get all controls in a specific domain."""
        return self.search(domain=domain)
    
    def search_by_type(self, control_type: str) -> List[ControlSearchResult]:
        """Get all controls of a specific type."""
        return self.search(control_type=control_type)
    
    def add_tags(self, control_id: str, tags: List[str]) -> bool:
        """Add search tags to a control."""
        control = self.get_control(control_id)
        if not control:
            return False
        
        control.search_tags.extend(tags)
        control.search_tags = list(set(control.search_tags))  # Deduplicate
        self._save_registry()
        return True
    
    # ─────────────────────────────────────────────────────────────────────────
    # METADATA & STATISTICS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_metadata(self) -> RegistryMetadata:
        """Get registry metadata and statistics."""
        by_domain = {}
        by_type = {}
        active_count = 0
        deprecated_count = 0
        total_versions = 0
        
        for control in self.controls.values():
            active_version = control.get_active_version()
            if active_version:
                active_count += 1
                domain = active_version.control_domain.value
                by_domain[domain] = by_domain.get(domain, 0) + 1
                
                ctype = active_version.control_type.value
                by_type[ctype] = by_type.get(ctype, 0) + 1
            
            for v in control.versions:
                total_versions += 1
                if v.status == ControlStatus.DEPRECATED:
                    deprecated_count += 1
        
        return RegistryMetadata(
            registry_version="2.0",
            last_updated=datetime.now().isoformat(),
            total_controls=len(self.controls),
            active_controls=active_count,
            deprecated_controls=deprecated_count,
            total_versions=total_versions,
            by_domain=by_domain,
            by_type=by_type,
        )
    
    def get_audit_log(self, control_id: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> List[Dict]:
        """Retrieve audit events with optional filtering."""
        results = self.audit_log.copy()
        
        if control_id:
            results = [e for e in results if e['control_id'] == control_id]
        
        if start_date:
            results = [e for e in results if e['timestamp'] >= start_date]
        
        if end_date:
            results = [e for e in results if e['timestamp'] <= end_date]
        
        return results
    
    # ─────────────────────────────────────────────────────────────────────────
    # EXPORT & SNAPSHOTS
    # ─────────────────────────────────────────────────────────────────────────
    
    def export_snapshot(self, output_path: str, include_deprecated: bool = False) -> str:
        """Export registry snapshot (YAML or JSON)."""
        data = {
            "registry_metadata": self.get_metadata().to_dict(),
            "controls": [],
        }
        
        for control in self.controls.values():
            for version in control.versions:
                if not include_deprecated and version.status == ControlStatus.DEPRECATED:
                    continue
                data['controls'].append(version.to_dict())
        
        output_file = Path(output_path)
        if output_file.suffix == '.yaml':
            import yaml
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:  # JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
