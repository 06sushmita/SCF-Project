"""
agents/control.py
ControlAgent: Converts extracted clauses into structured controls.
Wraps Level 1 generation logic in modular agent pattern.
"""

import re
from typing import List, Dict, Tuple
from datetime import datetime
from .models import (
    ControlVersion, ControlStatus, ControlDomain, ControlType, Control, AuditRecord
)


class ControlAgent:
    """
    Converts raw clauses into properly structured control objects.
    Handles domain inference, type classification, title/objective generation.
    """
    
    # Domain keywords and mappings (from Level 1)
    DOMAIN_MAP = [
        (
            ["phishing", "fraud", "caution", "rbi never", "impersonat",
             "social engineer", "personal information", "bank account details", "passwords"],
            "Information Security Awareness",
            "Fraud Prevention and User Education",
        ),
        (
            ["password", "authentication", "encrypt", "login",
             "access control", "restrict access", "unauthori"],
            "Access Control",
            "Identity and Access Management",
        ),
        (
            ["broker", "sub-agent", "brokerage", "enrol", "enroll",
             "delist", "code number", "registered broker", "receiving office"],
            "Access Control",
            "Third-Party and Agent Management",
        ),
        (
            ["nominat", "nominee", "beneficiar", "bond ledger", "bla",
             "joint holder", "sole holder", "minor"],
            "Data Governance",
            "Investor Rights and Record Management",
        ),
        (
            ["fema", "nri", "non-resident", "remittance",
             "income tax", "tds", "section 194"],
            "Regulatory Compliance",
            "Financial and Legal Compliance",
        ),
        (
            ["reimburs", "ecs", "30 days", "settlement", "cas nagpur",
             "working day", "brokerage payment", "brokerage claim"],
            "Financial Compliance",
            "Operational Financial Controls",
        ),
        (
            ["audit", "reconcil", "statement", "appendix", "report",
             "monitor", "log", "review", "inspect"],
            "Monitoring and Auditing",
            "Audit and Reconciliation Controls",
        ),
        (
            ["policy", "direction", "circular", "instruction", "master direction",
             "rules and regulations", "updated", "operative instruction"],
            "Governance and Compliance",
            "Policy and Regulatory Change Management",
        ),
    ]
    
    # Control type inference rules
    TYPE_RULES = {
        "Preventive": {
            "high": [
                "shall not", "must not", "prohibited", "not permitted", "never",
                "restrict", "prevent", "prohibit", "caution", "encrypt", "password",
                "authentication", "verify", "register", "enrol", "enroll",
                "allot", "appoint", "nominate", "mandate",
            ],
            "low": [
                "must", "shall", "required", "should", "ensure",
                "obtain", "submit", "provide", "issue",
            ],
        },
        "Detective": {
            "high": [
                "audit", "reconcil", "monitor", "inspect", "detect",
                "review", "track", "log", "logged", "alert",
            ],
            "low": [
                "report", "reporting", "statement", "appendix",
                "evidence", "record", "check", "notice",
            ],
        },
        "Corrective": {
            "high": [
                "delist", "cancel", "cancelled", "revoke", "amend", "rectify",
                "restore", "recover", "patch", "reimburs", "varied", "fresh nomination",
            ],
            "low": ["settle", "settlement", "update", "correct", "backup"],
        },
    }
    
    # Risk, evidence, metrics, assumptions (domain-keyed)
    RISK_MAP = {
        "Access Control": "Unauthorized or fraudulent access by unverified brokers, agents, or investors.",
        "Data Governance": "Disputed or fraudulent claims on investor assets due to missing or incorrect records.",
        "Monitoring and Auditing": "Undetected compliance breaches, financial discrepancies, or audit failures.",
        "Information Security Awareness": "Social engineering, phishing, or brand-impersonation attacks targeting investors or staff.",
        "Regulatory Compliance": "Regulatory sanctions or legal liability from non-compliance with applicable statutes.",
        "Financial Compliance": "Financial losses, delayed settlements, or adverse audit findings from improper payments.",
        "Governance and Compliance": "Operational non-compliance from outdated or inconsistently applied internal policies.",
    }
    
    EVIDENCE_MAP = {
        "Access Control": "Broker/agent registration register; unique code assignment logs; enrollment application copies.",
        "Data Governance": "BLA nomination records; Acknowledgement of Nomination copies; transfer and cancellation logs.",
        "Monitoring and Auditing": "Audit reports; Appendix IV reconciliation statements; monthly review logs.",
        "Information Security Awareness": "Staff training completion records; investor advisory notices; phishing incident logs.",
        "Regulatory Compliance": "Scheme eligibility checklists; rejected NRI nomination records; FEMA compliance documentation.",
        "Financial Compliance": "Brokerage settlement registers; ECS mandate forms; CAS Nagpur remittance acknowledgements.",
        "Governance and Compliance": "Version-controlled policy documents; RBI circular update logs; staff distribution acknowledgements.",
    }
    
    METRICS_MAP = {
        "Access Control": "% of applications bearing a valid registered broker code; number of unauthorised access incidents per quarter.",
        "Data Governance": "% of active BLAs with a registered nomination; number of acknowledgements issued vs. nominations filed.",
        "Monitoring and Auditing": "% of monthly reconciliation statements submitted on time; number of unreconciled items per period.",
        "Information Security Awareness": "% of staff completing anti-phishing training; number of phishing incidents reported per quarter.",
        "Regulatory Compliance": "Number of NRI eligibility errors detected during audits; % of staff trained on scheme-specific rules.",
        "Financial Compliance": "% of brokerage claims settled within 30 days; number of claims outstanding beyond the mandated period.",
        "Governance and Compliance": "Time elapsed from RBI circular publication to internal policy update; % of offices confirmed as updated.",
    }
    
    ASSUMPTIONS_MAP = {
        "Access Control": "Receiving Offices maintain a formal broker registry and have authority to assign and deactivate codes.",
        "Data Governance": "Receiving Offices have record-keeping systems capable of storing and retrieving per-BLA nomination data.",
        "Monitoring and Auditing": "Adequate audit infrastructure exists; personnel are assigned reconciliation responsibilities.",
        "Information Security Awareness": "Communication channels to all investors and staff are operational and regularly used.",
        "Regulatory Compliance": "Receiving Offices are notified of active bond schemes and applicable NRI eligibility restrictions.",
        "Financial Compliance": "Receiving Offices have access to ECS infrastructure and hold current mandates from all enrolled agents.",
        "Governance and Compliance": "A designated policy owner monitors RBI publications and is empowered to trigger internal reviews.",
    }
    
    # Objective templates (domain-keyed)
    OBJECTIVE_TEMPLATES = {
        "Information Security Awareness": "Ensure staff and investors are aware of {topic} to prevent social engineering and fraud.",
        "Access Control": "Ensure only authorised and verified parties are permitted to {topic}.",
        "Data Governance": "Ensure accurate and complete records are maintained for {topic}.",
        "Regulatory Compliance": "Ensure full compliance with applicable legal and regulatory requirements governing {topic}.",
        "Financial Compliance": "Ensure timely and accurate financial processing related to {topic}.",
        "Monitoring and Auditing": "Ensure {topic} is regularly reviewed, reconciled, and reported as required.",
        "Governance and Compliance": "Ensure {topic} is governed by current, enforceable, and consistently applied policy.",
    }
    
    # Title noise words
    TITLE_NOISE = re.compile(
        r"\b(the|a|an|of|in|on|at|to|for|and|or|with|by|from|that|which|"
        r"this|its|their|all|any|each|per|as|be|is|are|was|were)\b",
        re.I,
    )
    
    # Subject-to-modal mapping
    SUBJECT_MAP = [
        (re.compile(r"\breceiving offices?\b", re.I), "Receiving Offices must"),
        (re.compile(r"\bbrokers?\b", re.I), "Brokers must"),
        (re.compile(r"\binvestors?\b", re.I), "Investors must"),
        (re.compile(r"\borganis[ae]tions?\b", re.I), "Organizations must"),
        (re.compile(r"\bholders?\b", re.I), "Bond holders must"),
    ]
    
    def __init__(self):
        """Initialize agent with keyword mappings."""
        pass
    
    def generate_controls(self, clauses: List[str], counter_start: int = 1) -> List[Dict]:
        """
        Convert list of clauses into structured controls.
        
        Args:
            clauses: Pre-cleaned, de-duplicated clause strings
            counter_start: Starting control ID number
        
        Returns:
            List of control dictionaries with all fields
        """
        controls = []
        
        for idx, clause in enumerate(clauses, start=counter_start):
            domain, family = self._infer_domain_family(clause)
            ctrl_type = self._infer_control_type(clause)
            title = self._generate_title(clause)
            objective = self._generate_objective(clause, domain)
            statement = self._build_statement(clause)
            
            control = {
                "control_id": f"SCF-{idx:03d}",
                "title": title,
                "control_domain": domain,
                "control_family": family,
                "objective": objective,
                "control_statement": statement,
                "control_type": ctrl_type,
                "risk_addressed": self.RISK_MAP.get(domain, "Non-compliance with applicable regulatory requirements."),
                "evidence_required": self.EVIDENCE_MAP.get(domain, "Policy documents; audit records; compliance checklists."),
                "metrics": self.METRICS_MAP.get(domain, "Compliance rate as measured during periodic audits."),
                "assumptions": self.ASSUMPTIONS_MAP.get(domain, "Organization has defined compliance processes and assigned owners."),
            }
            controls.append(control)
        
        return controls
    
    def clause_to_control_version(self, clause_dict: Dict, actor: str = "system") -> ControlVersion:
        """
        Convert a clause dictionary to a ControlVersion object.
        Prepare for registry insertion.
        """
        return ControlVersion(
            version="1.0",
            control_id=clause_dict['control_id'],
            created_date=datetime.now().isoformat(),
            created_by=actor,
            status=ControlStatus.DRAFT,
            title=clause_dict['title'],
            objective=clause_dict['objective'],
            control_statement=clause_dict['control_statement'],
            control_domain=ControlDomain(clause_dict['control_domain']),
            control_family=clause_dict['control_family'],
            control_type=ControlType(clause_dict['control_type']),
            risk_addressed=clause_dict['risk_addressed'],
            evidence_required=clause_dict['evidence_required'],
            metrics=clause_dict['metrics'],
            assumptions=clause_dict['assumptions'],
            audit_trail=[
                AuditRecord(
                    timestamp=datetime.now().isoformat(),
                    actor=actor,
                    action="created",
                    reason="Generated from regulatory clause",
                )
            ],
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # TITLE GENERATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def _generate_title(self, clause: str) -> str:
        """Generate control title from clause."""
        text = re.sub(r"^\s*[\(\[]?[a-zA-Z0-9]{1,3}[\.\)\]]\s*", "", clause).strip()
        text = re.sub(
            r"^(we advise|it has come to our notice|please note|note that|"
            r"as a measure towards|in case of|in the event of)\s*",
            "", text, flags=re.I,
        ).strip()
        
        words = text.split()
        content = []
        for w in words:
            bare = w.strip(".,;:-()")
            if bare:
                content.append(bare)
            if len(content) >= 7:
                break
            if w.endswith((",", ";", ":")):
                break
        
        title = " ".join(content).strip(" ,;:.").title()
        return title[:90] if title else "Compliance Control"
    
    # ─────────────────────────────────────────────────────────────────────────
    # DOMAIN INFERENCE
    # ─────────────────────────────────────────────────────────────────────────
    
    def _infer_domain_family(self, text: str) -> Tuple[str, str]:
        """Infer control domain and family from clause keywords."""
        low = text.lower()
        for keywords, domain, family in self.DOMAIN_MAP:
            if any(kw in low for kw in keywords):
                return domain, family
        return "Governance and Compliance", "General Compliance"
    
    # ─────────────────────────────────────────────────────────────────────────
    # CONTROL TYPE INFERENCE
    # ─────────────────────────────────────────────────────────────────────────
    
    def _infer_control_type(self, clause: str) -> str:
        """Infer control type using keyword scoring."""
        low = clause.lower()
        scores = {t: 0 for t in self.TYPE_RULES}
        
        for ctype, buckets in self.TYPE_RULES.items():
            for kw in buckets["high"]:
                if kw in low:
                    scores[ctype] += 2
            for kw in buckets["low"]:
                if kw in low:
                    scores[ctype] += 1
        
        best_score = max(scores.values())
        if best_score == 0:
            return "Administrative"
        return max(scores, key=lambda t: scores[t])
    
    # ─────────────────────────────────────────────────────────────────────────
    # OBJECTIVE GENERATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def _generate_objective(self, clause: str, domain: str) -> str:
        """Generate control objective using domain template."""
        text = re.sub(r"^\s*[\(\[]?[a-zA-Z0-9]{1,3}[\.\)\]]\s*", "", clause).strip()
        words = text.split()
        topic_words = []
        
        for w in words[:6]:
            bare = w.strip(".,;:-()")
            if not self.TITLE_NOISE.match(bare) and bare:
                topic_words.append(bare.lower())
            if len(topic_words) >= 4:
                break
        
        topic = " ".join(topic_words) if topic_words else "this requirement"
        template = self.OBJECTIVE_TEMPLATES.get(
            domain,
            "Ensure compliance with the {topic} requirement as specified in the applicable regulation.",
        )
        return template.format(topic=topic)
    
    # ─────────────────────────────────────────────────────────────────────────
    # STATEMENT BUILDING
    # ─────────────────────────────────────────────────────────────────────────
    
    def _build_statement(self, clause: str) -> str:
        """Build control statement with proper grammar and modals."""
        stmt = re.sub(r"^\s*[\(\[]?[a-zA-Z0-9]{1,3}[\.\)\]]\s*", "", clause).strip()
        stmt = stmt[0].upper() + stmt[1:] if stmt else stmt
        
        low = stmt.lower()
        has_modal = re.search(r"\b(must|shall|should|may|required|advised)\b", low)
        
        if not has_modal:
            for pattern, replacement in self.SUBJECT_MAP:
                if pattern.search(stmt):
                    stmt = pattern.sub(replacement, stmt, count=1)
                    break
        
        if stmt and stmt[-1] not in ".!?":
            stmt += "."
        
        return stmt
