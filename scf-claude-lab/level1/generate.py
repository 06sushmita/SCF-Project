import json
import re
import string
import nltk
import yaml
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from PyPDF2 import PdfReader
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Download required NLTK models on first run; quiet=True suppresses repeated console noise.
for pkg in ("punkt", "punkt_tab", "stopwords"):
    nltk.download(pkg, quiet=True)

# Build a global stop-word set once so every tokenisation call can reuse it cheaply.
STOP_WORDS = set(stopwords.words("english"))


# ─────────────────────────────────────────────────────────────────────────────
# PDF TEXT CLEANING
# ─────────────────────────────────────────────────────────────────────────────

def _clean_raw(text: str) -> str:
    # PDFs often embed soft hyphens at line-breaks (e.g. "pre-\nvention").
    # Rejoining them before any further processing prevents split tokens.
    text = re.sub(r"-\s*\n\s*", "", text)
    # Collapse runs of spaces and tabs to a single space so word boundaries
    # are predictable for the tokeniser and keyword matchers.
    text = re.sub(r"[ \t]+", " ", text)
    # Multiple blank lines carry no semantic content; collapse to one newline.
    text = re.sub(r"\n{2,}", "\n", text)
    # Flatten remaining single newlines so sent_tokenize sees continuous prose
    # rather than fragments broken across lines.
    text = re.sub(r"\n", " ", text)
    # Final pass: remove any double-spaces introduced by the substitutions above.
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# NOISE FILTER
# ─────────────────────────────────────────────────────────────────────────────

# Compiled once at module load; reused for every clause. Using \b word-boundary
# anchors prevents partial matches (e.g. "may" inside "dismay").
_OBLIGATION_VERBS = re.compile(
    r"\b(must|shall|should|may not|required|advised|prohibited|not permitted|"
    r"never|ensure|maintain|submit|register|allot|settle|issue|appoint|"
    r"nominate|verify|delist|quote|arrange|obtain|provide|restrict|"
    r"comply|adhere|follow|inform)\b",
    re.I,
)

# RBI circular reference patterns appear in appendix lists, not in enforceable
# policy text. Matching them lets us drop entire reference-list sentences early.
_CIRCULAR_REF = re.compile(r"CO\.DT\.|IDMD\.CDD\.|No\.[A-Z0-9\-/]+\s+dated", re.I)

# Sentences that are purely a section number or single letter (e.g. "1.", "A)")
# are structural markers, not requirements.
_SECTION_NUM = re.compile(r"^[\d\s\.\)\(A-Za-z]{0,6}$")

# Roman-numeral list entries like "ii)" or "ix)" are reference indices only.
_ROMAN_REF = re.compile(r"^(i{1,4}v?|vi{0,3}|ix|x{1,3})\)", re.I)

# Two or more of these signals in a single sentence indicates an address block.
_ADDRESS_SIGS = {
    "telephone", "fax", "@rbi.org.in", "www.",
    "fort , mumbai", "central office building", "shahid bhagat singh",
}

# Salutation and closing lines are document formalities, not controls.
_SALUTATION = re.compile(
    r"^(dear\s+sir|yours\s+faithfully|encl\.|chief\s+general)", re.I
)


def is_meaningful(clause: str) -> bool:
    # Very short strings cannot carry a complete requirement; 45 chars is the
    # minimum for a clause like "Brokers must quote their code on applications."
    s = clause.strip()
    if len(s) < 45:
        return False

    # PDFs extracted from scanned documents often contain Devanagari (Hindi)
    # characters encoded as high-codepoint bytes. A ratio above 30 % signals
    # that the sentence is not English policy text.
    if sum(ord(c) > 127 for c in s) / len(s) > 0.30:
        return False

    if _SECTION_NUM.match(s) or _ROMAN_REF.match(s):
        return False

    if _CIRCULAR_REF.search(s):
        return False

    low = s.lower()

    # Address blocks typically contain at least two of the signals above.
    if sum(sig in low for sig in _ADDRESS_SIGS) >= 2:
        return False

    if _SALUTATION.match(low):
        return False

    # Six words or fewer in ALL CAPS is almost always a section heading.
    if s.isupper() and len(s.split()) <= 6:
        return False

    # A clause with no obligation verb cannot be converted to an enforceable
    # control statement, so there is nothing useful to extract.
    if not _OBLIGATION_VERBS.search(s):
        return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# DEDUPLICATION
# ─────────────────────────────────────────────────────────────────────────────

def is_duplicate(clause: str, seen: list, threshold: float = 0.72) -> bool:
    # Jaccard similarity over content tokens (stop-words and punctuation removed)
    # is used instead of simple substring matching because the same requirement
    # can appear across pages with minor wording differences. A threshold of 0.72
    # is tight enough to keep genuinely distinct clauses while dropping near-copies.
    toks_new = set(word_tokenize(clause.lower())) - STOP_WORDS - set(string.punctuation)
    for prev in seen:
        toks_prev = set(word_tokenize(prev.lower())) - STOP_WORDS - set(string.punctuation)
        if not toks_new or not toks_prev:
            continue
        jaccard = len(toks_new & toks_prev) / len(toks_new | toks_prev)
        if jaccard >= threshold:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL STATEMENT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

# Maps a subject found in the raw clause to a "Subject must" opener. This lets
# us inject a modal verb when the original text uses present-tense description
# ("Receiving Offices settle claims...") rather than an explicit obligation form.
_SUBJECT_MAP = [
    (re.compile(r"\breceiving offices?\b", re.I), "Receiving Offices must"),
    (re.compile(r"\bbrokers?\b", re.I),           "Brokers must"),
    (re.compile(r"\binvestors?\b", re.I),         "Investors must"),
    (re.compile(r"\borganis[ae]tions?\b", re.I),  "Organizations must"),
    (re.compile(r"\bholders?\b", re.I),           "Bond holders must"),
]


def build_statement(clause: str) -> str:
    # Strip leading list enumerators ("a.", "1.", "(i)", "c.") so the
    # control statement starts with actual content, not a list marker.
    stmt = re.sub(r"^\s*[\(\[]?[a-zA-Z0-9]{1,3}[\.\)\]]\s*", "", clause).strip()
    stmt = stmt[0].upper() + stmt[1:] if stmt else stmt

    # Only inject "must" when no modal verb is already present; otherwise the
    # injected word would duplicate or conflict with the existing modal.
    low = stmt.lower()
    has_modal = re.search(r"\b(must|shall|should|may|required|advised)\b", low)
    if not has_modal:
        for pattern, replacement in _SUBJECT_MAP:
            if pattern.search(stmt):
                stmt = pattern.sub(replacement, stmt, count=1)
                break

    # Policy statements are expected to be complete sentences; append a full
    # stop if the clause ends with anything other than terminal punctuation.
    if stmt and stmt[-1] not in ".!?":
        stmt += "."
    return stmt


# ─────────────────────────────────────────────────────────────────────────────
# TITLE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

# These common function words add length to a title without adding meaning;
# filtering them out leaves only the content words that identify the control.
_TITLE_NOISE = re.compile(
    r"\b(the|a|an|of|in|on|at|to|for|and|or|with|by|from|that|which|"
    r"this|its|their|all|any|each|per|as|be|is|are|was|were)\b",
    re.I,
)


def generate_title(clause: str) -> str:
    # Remove list enumerators so the title does not start with "A." or "1.".
    text = re.sub(r"^\s*[\(\[]?[a-zA-Z0-9]{1,3}[\.\)\]]\s*", "", clause).strip()

    # These openers describe the context of the requirement, not the requirement
    # itself. Removing them produces a more direct, audit-friendly title.
    text = re.sub(
        r"^(we advise|it has come to our notice|please note|note that|"
        r"as a measure towards|in case of|in the event of)\s*",
        "", text, flags=re.I,
    ).strip()

    # Collect up to seven content words. Stop early at a comma or semicolon
    # because those punctuation marks usually separate the key noun phrase
    # from subordinate clauses that would make the title too long.
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


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN / FAMILY INFERENCE
# ─────────────────────────────────────────────────────────────────────────────

# Ordered from most-specific to least-specific so that a clause matching both
# "phishing" and "email" is classified as fraud-awareness rather than the
# more generic governance bucket that also contains "email".
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


def infer_domain_family(text: str):
    # Walk the ordered list and return on the first match so more-specific
    # domains win over broader ones that share some keywords.
    low = text.lower()
    for keywords, domain, family in DOMAIN_MAP:
        if any(kw in low for kw in keywords):
            return domain, family
    return "Governance and Compliance", "General Compliance"


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL TYPE INFERENCE
# ─────────────────────────────────────────────────────────────────────────────

# Two-tier keyword scoring prevents the most common obligation words ("must",
# "shall") from drowning out the stronger semantic signals ("delist", "audit").
# High-confidence keywords score 2; supporting keywords score 1. The control
# type with the highest total score wins; ties default to Administrative.
_TYPE_RULES = {
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


def infer_control_type(clause: str) -> str:
    low = clause.lower()
    scores = {t: 0 for t in _TYPE_RULES}
    for ctype, buckets in _TYPE_RULES.items():
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


# ─────────────────────────────────────────────────────────────────────────────
# OBJECTIVE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

# Per-domain sentence templates keep objectives consistent across all controls
# in the same domain, making the YAML easier to parse during an audit review.
_OBJECTIVE_TEMPLATES = {
    "Information Security Awareness":
        "Ensure staff and investors are aware of {topic} to prevent social engineering and fraud.",
    "Access Control":
        "Ensure only authorised and verified parties are permitted to {topic}.",
    "Data Governance":
        "Ensure accurate and complete records are maintained for {topic}.",
    "Regulatory Compliance":
        "Ensure full compliance with applicable legal and regulatory requirements governing {topic}.",
    "Financial Compliance":
        "Ensure timely and accurate financial processing related to {topic}.",
    "Monitoring and Auditing":
        "Ensure {topic} is regularly reviewed, reconciled, and reported as required.",
    "Governance and Compliance":
        "Ensure {topic} is governed by current, enforceable, and consistently applied policy.",
}


def generate_objective(clause: str, domain: str) -> str:
    # Extract a short noun phrase from the start of the clause to fill the
    # {topic} slot in the template. Stop-words are skipped so the topic
    # phrase contains only meaningful content words.
    text = re.sub(r"^\s*[\(\[]?[a-zA-Z0-9]{1,3}[\.\)\]]\s*", "", clause).strip()
    words = text.split()
    topic_words = []
    for w in words[:6]:
        bare = w.strip(".,;:-()")
        if not _TITLE_NOISE.match(bare) and bare:
            topic_words.append(bare.lower())
        if len(topic_words) >= 4:
            break
    topic = " ".join(topic_words) if topic_words else "this requirement"
    template = _OBJECTIVE_TEMPLATES.get(
        domain,
        "Ensure compliance with the {topic} requirement as specified in the applicable regulation.",
    )
    return template.format(topic=topic)


# ─────────────────────────────────────────────────────────────────────────────
# LOOKUP TABLES  (risk, evidence, metrics, assumptions)
# ─────────────────────────────────────────────────────────────────────────────

# Each table is keyed on control_domain so a single domain lookup populates
# four fields consistently. This also makes it easy to extend: adding a new
# domain entry in DOMAIN_MAP automatically gains correct metadata here.

RISK_MAP = {
    "Access Control":
        "Unauthorized or fraudulent access by unverified brokers, agents, or investors.",
    "Data Governance":
        "Disputed or fraudulent claims on investor assets due to missing or incorrect records.",
    "Monitoring and Auditing":
        "Undetected compliance breaches, financial discrepancies, or audit failures.",
    "Information Security Awareness":
        "Social engineering, phishing, or brand-impersonation attacks targeting investors or staff.",
    "Regulatory Compliance":
        "Regulatory sanctions or legal liability from non-compliance with applicable statutes.",
    "Financial Compliance":
        "Financial losses, delayed settlements, or adverse audit findings from improper payments.",
    "Governance and Compliance":
        "Operational non-compliance from outdated or inconsistently applied internal policies.",
}

EVIDENCE_MAP = {
    "Access Control":
        "Broker/agent registration register; unique code assignment logs; enrollment application copies.",
    "Data Governance":
        "BLA nomination records; Acknowledgement of Nomination copies; transfer and cancellation logs.",
    "Monitoring and Auditing":
        "Audit reports; Appendix IV reconciliation statements; monthly review logs.",
    "Information Security Awareness":
        "Staff training completion records; investor advisory notices; phishing incident logs.",
    "Regulatory Compliance":
        "Scheme eligibility checklists; rejected NRI nomination records; FEMA compliance documentation.",
    "Financial Compliance":
        "Brokerage settlement registers; ECS mandate forms; CAS Nagpur remittance acknowledgements.",
    "Governance and Compliance":
        "Version-controlled policy documents; RBI circular update logs; staff distribution acknowledgements.",
}

METRICS_MAP = {
    "Access Control":
        "% of applications bearing a valid registered broker code; number of unauthorised access incidents per quarter.",
    "Data Governance":
        "% of active BLAs with a registered nomination; number of acknowledgements issued vs. nominations filed.",
    "Monitoring and Auditing":
        "% of monthly reconciliation statements submitted on time; number of unreconciled items per period.",
    "Information Security Awareness":
        "% of staff completing anti-phishing training; number of phishing incidents reported per quarter.",
    "Regulatory Compliance":
        "Number of NRI eligibility errors detected during audits; % of staff trained on scheme-specific rules.",
    "Financial Compliance":
        "% of brokerage claims settled within 30 days; number of claims outstanding beyond the mandated period.",
    "Governance and Compliance":
        "Time elapsed from RBI circular publication to internal policy update; % of offices confirmed as updated.",
}

ASSUMPTIONS_MAP = {
    "Access Control":
        "Receiving Offices maintain a formal broker registry and have authority to assign and deactivate codes.",
    "Data Governance":
        "Receiving Offices have record-keeping systems capable of storing and retrieving per-BLA nomination data.",
    "Monitoring and Auditing":
        "Adequate audit infrastructure exists; personnel are assigned reconciliation responsibilities.",
    "Information Security Awareness":
        "Communication channels to all investors and staff are operational and regularly used.",
    "Regulatory Compliance":
        "Receiving Offices are notified of active bond schemes and applicable NRI eligibility restrictions.",
    "Financial Compliance":
        "Receiving Offices have access to ECS infrastructure and hold current mandates from all enrolled agents.",
    "Governance and Compliance":
        "A designated policy owner monitors RBI publications and is empowered to trigger internal reviews.",
}


# ─────────────────────────────────────────────────────────────────────────────
# RISK REGISTRY  (written to risk.json)
# ─────────────────────────────────────────────────────────────────────────────

# The risk registry is a standalone JSON file that maps every domain to its
# full risk profile. It lets other tools (dashboards, GRC platforms) consume
# the risk data without parsing the full controls YAML, and provides a single
# source of truth that risk_addressed in every control points back to.
RISK_REGISTRY = {
    "risks": [
        {
            "risk_id": "RSK-001",
            "domain": "Information Security Awareness",
            "risk_title": "Phishing and Social Engineering via RBI Brand Impersonation",
            "description": (
                "Attackers impersonate RBI through emails, SMS, or phone calls to extract "
                "sensitive investor information such as bank account details or passwords."
            ),
            "likelihood": "High",
            "impact": "High",
            "inherent_risk_rating": "Critical",
            "mitigating_controls": ["Staff awareness training", "Investor advisories", "Incident reporting channel"],
            "residual_risk_rating": "Medium",
            "risk_owner": "Compliance / Information Security Team",
            "regulatory_reference": "RBI Master Directions — Caution notice on impersonation",
        },
        {
            "risk_id": "RSK-002",
            "domain": "Access Control — Third-Party and Agent Management",
            "risk_title": "Unauthorized Broker Activity and Fraudulent Brokerage Claims",
            "description": (
                "Unregistered or deactivated brokers submit applications or claims using "
                "invalid or stolen broker codes, resulting in fraudulent payments."
            ),
            "likelihood": "Medium",
            "impact": "High",
            "inherent_risk_rating": "High",
            "mitigating_controls": [
                "Formal broker enrollment procedure",
                "Unique code assignment and verification",
                "Dormant broker delisting after 2 years",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Receiving Office Operations Manager",
            "regulatory_reference": "RBI Master Directions — Section A: Appointment / Delisting of Brokers",
        },
        {
            "risk_id": "RSK-003",
            "domain": "Access Control — Third-Party and Agent Management",
            "risk_title": "Misuse of RBI Brand by Sub-Agents",
            "description": (
                "Sub-agents appointed by Receiving Offices falsely claim RBI endorsement "
                "in marketing materials, misleading investors and exposing Receiving Offices "
                "to regulatory and reputational liability."
            ),
            "likelihood": "Medium",
            "impact": "Medium",
            "inherent_risk_rating": "Medium",
            "mitigating_controls": [
                "Contractual brand-use prohibition in sub-agent agreements",
                "Periodic audit of agent marketing materials",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Receiving Office Compliance Officer",
            "regulatory_reference": "RBI Master Directions — Section A.2: Appointment of sub-agents",
        },
        {
            "risk_id": "RSK-004",
            "domain": "Financial Compliance",
            "risk_title": "Delayed or Non-Compliant Brokerage Settlement",
            "description": (
                "Brokerage claims are not settled within the mandated 30-day window, "
                "leading to agent disputes, regulatory findings, and reputational damage."
            ),
            "likelihood": "Medium",
            "impact": "Medium",
            "inherent_risk_rating": "Medium",
            "mitigating_controls": [
                "30-day settlement SLA tracking",
                "Monthly ECS payment cycle",
                "Advance reimbursement from CAS Nagpur",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Finance / Treasury Team",
            "regulatory_reference": "RBI Master Directions — Section B.3: Brokerage claims",
        },
        {
            "risk_id": "RSK-005",
            "domain": "Monitoring and Auditing",
            "risk_title": "Unreconciled Brokerage Reimbursement Accounts",
            "description": (
                "Failure to submit accurate monthly remittance reports or Appendix IV statements "
                "results in unreconciled advance payments and adverse audit findings."
            ),
            "likelihood": "Low",
            "impact": "High",
            "inherent_risk_rating": "High",
            "mitigating_controls": [
                "Monthly CAS remittance reporting",
                "Appendix IV statement submission for 10% balance",
                "Internal reconciliation review",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Finance / Audit Team",
            "regulatory_reference": "RBI Master Directions — Section B.3d: Reimbursement centralized at CAS Nagpur",
        },
        {
            "risk_id": "RSK-006",
            "domain": "Data Governance",
            "risk_title": "Missing or Invalid Nomination Records for Bond Holders",
            "description": (
                "Bond proceeds are disbursed to the wrong party or disputed in court because "
                "nominations were never registered, were registered after maturity, or were "
                "not updated following a bond transfer."
            ),
            "likelihood": "Medium",
            "impact": "High",
            "inherent_risk_rating": "High",
            "mitigating_controls": [
                "Mandatory nomination registration with written acknowledgement",
                "Automatic nomination cancellation on transfer",
                "Per-BLA nomination tracking",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Receiving Office Records Manager",
            "regulatory_reference": "RBI Master Directions — Section C: Nomination Facility",
        },
        {
            "risk_id": "RSK-007",
            "domain": "Data Governance",
            "risk_title": "Unauthorized or Undocumented Nomination Changes",
            "description": (
                "Nomination records are altered without the bond holder's written consent, "
                "enabling a fraudulent beneficiary to claim bond proceeds."
            ),
            "likelihood": "Low",
            "impact": "High",
            "inherent_risk_rating": "High",
            "mitigating_controls": [
                "Written change requests with date-stamped registration",
                "Access-controlled nomination modification workflow",
                "Audit log of all nomination events",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Receiving Office Compliance Officer",
            "regulatory_reference": "RBI Master Directions — Section C.4: Variation/cancellation of nomination",
        },
        {
            "risk_id": "RSK-008",
            "domain": "Regulatory Compliance",
            "risk_title": "Invalid NRI Nomination Under Prohibited Bond Scheme",
            "description": (
                "A Non-Resident Indian is registered as a nominee under the 7.75% Savings "
                "(Taxable) Bonds 2018 scheme where NRI nominations are explicitly prohibited, "
                "creating a FEMA compliance violation."
            ),
            "likelihood": "Low",
            "impact": "High",
            "inherent_risk_rating": "High",
            "mitigating_controls": [
                "Scheme-specific NRI eligibility checklist at point of registration",
                "Staff training on active scheme restrictions",
                "Rejection log for non-compliant nomination requests",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Regulatory Compliance Officer",
            "regulatory_reference": "RBI Master Directions — Section C.8: NRI nomination restrictions",
        },
        {
            "risk_id": "RSK-009",
            "domain": "Governance and Compliance",
            "risk_title": "Operations Based on Outdated Master Directions",
            "description": (
                "Staff or Receiving Offices apply superseded rules because internal policy "
                "documents were not updated simultaneously with the publication of revised "
                "RBI Master Directions."
            ),
            "likelihood": "Medium",
            "impact": "Medium",
            "inherent_risk_rating": "Medium",
            "mitigating_controls": [
                "Designated policy owner monitors RBI publications",
                "Version-controlled policy documents with revision dates",
                "Mandatory distribution acknowledgement from all Receiving Offices",
            ],
            "residual_risk_rating": "Low",
            "risk_owner": "Policy / Compliance Team",
            "regulatory_reference": "RBI Master Directions — Foreword: simultaneous update obligation",
        },
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

Tk().withdraw()
pdf_file = askopenfilename(title="Select PDF file", filetypes=[("PDF Files", "*.pdf")])
if not pdf_file:
    print("No file selected. Exiting.")
    exit()

# Read every page and join into one cleaned string before sentence tokenisation
# so that clauses spanning a page boundary are not split into two fragments.
reader = PdfReader(pdf_file)
raw_pages = []
for page in reader.pages:
    t = page.extract_text()
    if t:
        raw_pages.append(t)
full_text = _clean_raw("\n".join(raw_pages))

# sent_tokenize uses the Punkt model trained on English prose; it handles
# abbreviations and decimal numbers better than a simple split on ".".
clauses = sent_tokenize(full_text)

controls = []
seen: list[str] = []
counter = 1

for raw_clause in clauses:
    clause = _clean_raw(raw_clause)

    if not is_meaningful(clause):
        continue
    if is_duplicate(clause, seen):
        continue

    seen.append(clause)

    domain, family = infer_domain_family(clause)
    ctrl_type      = infer_control_type(clause)
    title          = generate_title(clause)
    objective      = generate_objective(clause, domain)
    statement      = build_statement(clause)

    controls.append({
        "control_id":        f"SCF-{counter:03}",
        "title":             title,
        "control_domain":    domain,
        "control_family":    family,
        "objective":         objective,
        "control_statement": statement,
        "control_type":      ctrl_type,
        "risk_addressed":    RISK_MAP.get(domain,     "Non-compliance with applicable regulatory requirements."),
        "evidence_required": EVIDENCE_MAP.get(domain, "Policy documents; audit records; compliance checklists."),
        "metrics":           METRICS_MAP.get(domain,  "Compliance rate as measured during periodic audits."),
        "assumptions":       ASSUMPTIONS_MAP.get(domain, "Organization has defined compliance processes and assigned owners."),
    })
    counter += 1

# Write controls.yaml — allow_unicode preserves any non-ASCII characters that
# survived the noise filter; width=120 prevents YAML from wrapping mid-sentence.
with open("controls.yaml", "w", encoding="utf-8") as f:
    yaml.dump({"controls": controls}, f, sort_keys=False, allow_unicode=True, width=120)

# Write risk.json — indent=2 keeps it human-readable and diff-friendly in version control.
with open("risk.json", "w", encoding="utf-8") as f:
    json.dump(RISK_REGISTRY, f, indent=2, ensure_ascii=False)

print(f"Done — {counter - 1} controls written to controls.yaml")
print(f"       {len(RISK_REGISTRY['risks'])} risks written to risk.json")