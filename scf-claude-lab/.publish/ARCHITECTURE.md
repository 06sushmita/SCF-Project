# 📐 SCF Platform – System Architecture

**Secure Control Framework**: Transforms regulatory PDFs into versioned, executable compliance controls.

**Technology Stack**: Python 3.9+ | FastAPI | OPA/Rego | NLTK | YAML

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SYSTEMS                            │
│  (PDF Regulators, Compliance Teams, GRC Platforms)                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FASTAPI REST LAYER                            │
│  POST /generate-controls | GET /controls | POST /validate          │
│  GET /registry | GET /policies | POST /policy-check                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AGENT ORCHESTRATION                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Extract    │  │   Control    │  │   Policy     │             │
│  │   Agent      │→ │   Agent      │→ │   Agent      │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│           ↓               ↓                   ↓                    │
│      ┌──────────────────────────────────────────────┐              │
│      │      Registry Agent (Lifecycle Mgmt)        │              │
│      └──────────────────────────────────────────────┘              │
│           ↓               ↓                   ↓                    │
│      ┌──────────────────────────────────────────────┐              │
│      │   Validation Agent (Policy Testing)         │              │
│      └──────────────────────────────────────────────┘              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Controls Reg.   │  │  Risk Registry   │  │  Policy Artifacts│ │
│  │  (JSON)          │  │  (JSON)          │  │  (Rego/Python)   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│  ┌──────────────────┐  ┌──────────────────────────────────┐        │
│  │  Audit History   │  │  Test Results & Compliance Logs  │        │
│  │  (JSON)          │  │  (JSON)                          │        │
│  └──────────────────┘  └──────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. EXTRACTION LAYER (Level 1)

### **Agents: ExtractAgent**

**Input**: PDF file containing regulatory text
**Process**:
- Text cleaning (soft hyphen removal, whitespace normalization)
- Sentence tokenization (NLTK Punkt)
- Noise filtering (obligation detection, circular references, address blocks)
- Duplicate detection (Jaccard similarity ≥ 0.72)

**Output**: Clean list of clauses

**Payload Example**:
```json
{
  "source_file": "rbi_master_directions.pdf",
  "clauses": [
    "Receiving Offices must verify broker registration before allocating a code.",
    "Brokers seeking enrollment must submit applications on business letterhead..."
  ],
  "statistics": {
    "total_sentences": 1250,
    "meaningful_clauses": 45,
    "duplicates_removed": 8
  }
}
```

---

## 2. CONTROL GENERATION LAYER (Level 1+)

### **Agents: ControlAgent**

**Input**: Extracted clauses
**Process**:
- Domain inference (keyword matching against 8 control domains)
- Control type classification (Preventive/Detective/Corrective)
- Title generation (7-word noun phrases, stop-word removal)
- Objective template filling (domain-specific templates with topic extraction)
- Statement normalization (modal verb injection, enumeration removal)
- Metadata enrichment (risk, evidence, metrics, assumptions)

**Output**: Structured control objects

**Data Model**:
```yaml
control_id: SCF-001
title: Broker Enrollment Procedure
control_domain: Access Control
control_family: Third-Party and Agent Management
control_type: Preventive
objective: Ensure only authorized and verified brokers can submit claims.
control_statement: Brokers must submit enrollment requests on formal letterhead and receive a unique code before claiming brokerage.
risk_addressed: Unauthorized or fraudulent broker access
evidence_required: Broker registration logs; code assignment records
metrics: "% of applications with valid codes; unauthorized access incidents per quarter"
assumptions: "Receiving offices maintain active broker registry and have authority to assign codes"
```

---

## 3. REGISTRY & LIFECYCLE LAYER (Level 2)

### **Agents: RegistryAgent**

**Responsibilities**:
- **Versioning**: Each control version is immutable; updates increment version (1.0 → 1.1 → 2.0)
- **Lifecycle States**:
  - `draft` – Created, not yet approved for use
  - `active` – In production, actively enforced
  - `deprecated` – Superseded, no longer used
- **Change History**: Audit trail with user, timestamp, reason for each state transition
- **Search Index**: Fast lookups by domain, family, type, title, keywords

**Data Model**:
```json
{
  "registry_version": "2.0",
  "last_updated": "2024-03-27T14:30:00Z",
  "controls": [
    {
      "control_id": "SCF-001",
      "versions": [
        {
          "version": "1.0",
          "created_date": "2024-01-15",
          "created_by": "system",
          "status": "deprecated",
          "reason_deactivated": "Superseded by v1.1 with clearer language",
          "content": { /* ... */ }
        },
        {
          "version": "1.1",
          "created_date": "2024-02-20",
          "created_by": "compliance_team",
          "status": "active",
          "amended_from_version": "1.0",
          "changes": "Clarified enrollment procedure; added deadline requirement",
          "content": { /* ... */ }
        }
      ],
      "current_version": "1.1",
      "search_tags": ["broker", "enrollment", "access-control", "third-party"]
    }
  ]
}
```

### **Registry API**:
```python
class ControlRegistry:
    def add_control(self, control: Control, status: str = "draft") → ControlVersion
    def update_control(self, control_id: str, changes: dict, reason: str) → ControlVersion
    def deprecate_control(self, control_id: str, reason: str) → bool
    def activate_control(self, control_id: str, version: str) → bool
    def get_control(self, control_id: str, version: str = "active") → ControlVersion
    def search(self, query: str, domain: str = None, type: str = None) → List[ControlVersion]
    def get_history(self, control_id: str) → List[ControlVersion]
```

---

## 4. POLICY-AS-CODE LAYER (Level 3)

### **Agents: PolicyAgent**

**Purpose**: Convert each control into executable, testable policies

**Policy Formats**:
1. **OPA/Rego** – High-assurance policy evaluation (CEL-compliant)
2. **Python** – For simpler, developer-friendly policies

### **Rego Policy Structure**:

Each control directory contains:
```
policies/
  SCF-001-broker-enrollment/
    policy.rego              # Main policy logic
    positive_test.json       # Valid example (should ALLOW)
    negative_test.json       # Invalid example (should DENY)
    README.md               # Policy description
```

**Example Rego Policy**:
```rego
package scf.broker_enrollment

# SCF-001: Broker Enrollment Procedure
# Ensure only formally enrolled brokers with valid codes can submit claims

import future.keywords

# Allow defined brokers with valid codes
allow if {
    context.actor_type == "broker"
    context.has_enrollment_letter == true
    context.broker_code != null
    context.broker_code in data.registered_brokers
}

# Deny all others
deny if {
    not allow
}

# Metrics for compliance monitoring
metrics if {
    count_valid_brokers := count([b | b in data.registered_brokers])
    unauthorized_attempts := count([attempt | attempt in data.access_attempts; not allow])
}
```

**Python Policy Example**:
```python
class SCF001BrokerEnrollment(PolicyValidator):
    """Broker Enrollment Procedure - Preventive Control"""
    
    def __init__(self):
        self.control_id = "SCF-001"
        self.name = "Broker Enrollment Procedure"
        
    def validate(self, context: PolicyContext) -> PolicyResult:
        """
        Validates that:
        1. Applicant is a registered broker
        2. Applicant holds a valid broker code
        3. Applicant submitted formal enrollment letter
        """
        violations = []
        
        if context.actor_type != "broker":
            violations.append(f"DENY: Actor is not a broker (type={context.actor_type})")
        
        if not context.has_enrollment_letter:
            violations.append("DENY: Missing formal enrollment letter")
        
        if context.broker_code not in self.registered_brokers:
            violations.append(f"DENY: Invalid broker code '{context.broker_code}'")
        
        return PolicyResult(
            control_id=self.control_id,
            status="PASS" if not violations else "FAIL",
            violations=violations,
            evidence_collected=context.to_dict(),
            timestamp=datetime.now().isoformat()
        )
```

### **Test Cases**:

**Positive Test (PASS)**: Valid enrollment request
```json
{
  "test_id": "SCF-001-positive-001",
  "test_name": "Valid broker enrollment with code",
  "context": {
    "actor_type": "broker",
    "has_enrollment_letter": true,
    "broker_code": "BR0001",
    "registered_brokers": ["BR0001", "BR0002"]
  },
  "expected_result": "PASS"
}
```

**Negative Test (FAIL)**: Missing enrollment letter
```json
{
  "test_id": "SCF-001-negative-001",
  "test_name": "Broker without enrollment letter",
  "context": {
    "actor_type": "broker",
    "has_enrollment_letter": false,
    "broker_code": "BR0001",
    "registered_brokers": ["BR0001"]
  },
  "expected_result": "FAIL",
  "expected_violations": ["Missing formal enrollment letter"]
}
```

---

## 5. API LAYER

### **Framework**: FastAPI

### **Core Endpoints**:

#### **A. Control Management**
- `POST /api/v1/controls/generate` – Extract and generate controls from PDF
- `GET /api/v1/controls?domain=...&type=...` – Search controls
- `GET /api/v1/controls/{control_id}` – Retrieve specific control
- `POST /api/v1/controls/{control_id}/versions` – Create new version
- `PATCH /api/v1/controls/{control_id}` – Update control
- `DELETE /api/v1/controls/{control_id}` – Deprecate control

#### **B. Registry & Lifecycle**
- `GET /api/v1/registry` – Full control registry with versions
- `GET /api/v1/registry/search?q=...` – Full-text search
- `GET /api/v1/controls/{control_id}/history` – Version history with audit trail

#### **C. Policy Validation**
- `POST /api/v1/policies/validate` – Run policy check against context
- `GET /api/v1/policies/{control_id}` – Get policy for a control
- `POST /api/v1/policies/run-tests` – Execute test suite for a policy

#### **D. Compliance Reporting**
- `GET /api/v1/compliance/report?domain=...` – Compliance status by domain
- `GET /api/v1/compliance/failures` – Recent policy violations
- `GET /api/v1/audit-log?start_date=...&end_date=...` – Audit trail

### **Request/Response Examples**:

#### **Generate Controls**:
```bash
curl -X POST http://localhost:8000/api/v1/controls/generate \
  -F "file=@regulation.pdf" \
  -H "Authorization: Bearer token"
```

**Response**:
```json
{
  "status": "success",
  "message": "45 controls extracted",
  "controls": [
    {
      "control_id": "SCF-001",
      "status": "draft",
      "version": "1.0",
      "title": "Broker Enrollment Procedure"
    }
  ],
  "risk_registry_size": 9,
  "timestamp": "2024-03-27T14:30:00Z"
}
```

#### **Search Controls**:
```bash
curl "http://localhost:8000/api/v1/controls?domain=Access+Control&type=Preventive"
```

#### **Validate Policy**:
```bash
curl -X POST http://localhost:8000/api/v1/policies/validate \
  -H "Content-Type: application/json" \
  -d '{
    "control_id": "SCF-001",
    "context": {
      "actor_type": "broker",
      "has_enrollment_letter": true,
      "broker_code": "BR0001",
      "registered_brokers": ["BR0001"]
    }
  }'
```

**Response**:
```json
{
  "control_id": "SCF-001",
  "policy_name": "Broker Enrollment Procedure",
  "result": "PASS",
  "violations": [],
  "compliance_score": 1.0,
  "timestamp": "2024-03-27T14:32:45Z"
}
```

---

## 6. TESTING STRATEGY

### **Test Pyramid**:
```
          ▲
         ╱ ╲
        ╱   ╱ Policy Integration Tests (5%)
       ╱   ╱
      ╱───╱
     ╱   ╱ API Integration Tests (20%)
    ╱   ╱
   ╱───╱
  ╱   ╱ Unit Tests (75%)
 ╱   ╱
╱───╱
```

### **Test Suites**:

1. **Unit Tests** (`test_agents.py`)
   - Clause extraction and cleaning
   - Domain/type/objective inference
   - Title and statement generation
   - Registry operations (CRUD, versioning)

2. **Policy Tests** (`test_policies.py`)
   - Each control policy evaluated against positive + negative test cases
   - Compliance metrics calculated
   - Side-effect-free (no database mutations)

3. **API Tests** (`test_api.py`)
   - Endpoint availability and response codes
   - Request/response schema validation
   - End-to-end workflows (extract → register → validate)
   - Error handling (missing fields, invalid policy, etc.)

4. **Integration Tests** (`test_integration.py`)
   - Full PDF → Control → Policy → API flow
   - Registry state consistency across operations
   - Audit log completeness

---

## 7. DEPLOYMENT

### **Container Structure**:
```
docker-compose.yml
  services:
    scf-api:          # FastAPI service (port 8000)
    scf-opa:          # OPA server for policy evaluation (port 8181)
    scf-storage:      # SQLite or PostgreSQL (port 5432)
```

### **Environment Configuration**:
```bash
# .env
API_HOST=0.0.0.0
API_PORT=8000
DB_URL=file:./scf.db
OPA_URL=http://localhost:8181
LOG_LEVEL=INFO
ENABLE_SWAGGER=true
```

### **Startup**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database & load controls
python scripts/init_db.py

# Start API server
python -m api.main

# In separate terminal, start OPA
opa run --server
```

---

## 8. FILE STRUCTURE

```
scf-claude-lab/
├── README.md                          # Setup & quickstart
├── ARCHITECTURE.md                    # This file
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # Container orchestration
├── .env.example                       # Environment template
│
├── agents/
│   ├── __init__.py
│   ├── extract.py                     # ExtractAgent: PDF → clauses
│   ├── control.py                     # ControlAgent: clauses → controls
│   ├── policy.py                      # PolicyAgent: controls → policies
│   ├── registry.py                    # RegistryAgent: lifecycle mgmt
│   └── validation.py                  # ValidationAgent: policy testing
│
├── api/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app definition
│   ├── schemas.py                     # Pydantic request/response models
│   ├── endpoints.py                   # API route handlers
│   └── auth.py                        # Example: token-based auth
│
├── controls/
│   ├── controls_registry.json         # Current registry (v2.0)
│   ├── controls_v1.0.yaml             # Historical snapshot
│   ├── controls_v1.1.yaml             # Historical snapshot
│   └── risk_registry.json             # Risk catalog
│
├── policies/
│   ├── SCF-001-broker-enrollment/
│   │   ├── policy.rego                # OPA policy definition
│   │   ├── policy.py                  # Python policy validator
│   │   ├── positive_test.json         # Valid case
│   │   └── negative_test.json         # Invalid case
│   ├── SCF-002-nomination-mgmt/
│   │   ├── policy.rego
│   │   ├── policy.py
│   │   └── tests/
│   └── ...
│
├── tests/
│   ├── __init__.py
│   ├── test_agents.py                 # Unit tests for agents
│   ├── test_policies.py               # Policy validation tests
│   ├── test_api.py                    # API integration tests
│   └── test_integration.py            # End-to-end flows
│
├── docs/
│   ├── API.md                         # API reference
│   ├── DEPLOYMENT.md                  # Docker & cloud setup
│   ├── POSTMAN.md                     # Postman collection guide
│   └── examples/
│       ├── valid_enrollment.json      # Example: valid policy context
│       └── invalid_nomination.json    # Example: invalid policy context
│
└── level1/
    ├── __init__.py
    ├── generate.py                    # Legacy extraction script
    ├── word_library.py                # Keyword dictionaries
    ├── controls.yaml                  # Initial control snapshot
    └── risk.json                      # Initial risk snapshot
```

---

## 9. WORKFLOW: End-to-End Example

### **Scenario**: New RBI Circular Released

**Step 1: Extract Controls (ExtractAgent)**
```bash
python -c "
  from agents.extract import ExtractAgent
  agent = ExtractAgent()
  clauses = agent.extract('new_rbi_circular.pdf')
  print(f'Extracted {len(clauses)} clauses')
"
```

**Step 2: Generate Controls (ControlAgent)**
```bash
curl -X POST http://localhost:8000/api/v1/controls/generate \
  -F "file=@new_rbi_circular.pdf"
```

**Step 3: Review & Activate (RegistryAgent via API)**
```bash
curl -X PATCH http://localhost:8000/api/v1/controls/SCF-050 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active",
    "version": "1.0",
    "reason": "Approved by compliance team"
  }'
```

**Step 4: Test Policy (PolicyAgent + ValidationAgent)**
```bash
curl -X POST http://localhost:8000/api/v1/policies/run-tests \
  -H "Content-Type: application/json" \
  -d '{"control_id": "SCF-050"}'
```

**Response**:
```json
{
  "control_id": "SCF-050",
  "policy_name": "Broker Enrollment Update",
  "positive_tests_passed": 3,
  "negative_tests_passed": 2,
  "overall_result": "PASS",
  "metrics": {
    "compliance_score": 0.98,
    "violations_detected": 0
  }
}
```

---

## 10. Security & Compliance

### **Built-in Controls**:
- ✅ **API Authentication**: Token-based (Auth0/JWT)
- ✅ **Audit Logging**: Every operation logged with user, timestamp, changes
- ✅ **Version Control**: Immutable control history (never delete, only deprecate)
- ✅ **Policy Isolation**: OPA policies run in sandbox environment
- ✅ **Change Approval**: Lifecycle transitions require documented reason
- ✅ **Compliance Reports**: Automated policy violation tracking

### **Audit Trail Example**:
```json
{
  "event_id": "EVT-2024-001234",
  "timestamp": "2024-03-27T14:35:12Z",
  "event_type": "control_activated",
  "actor": "compliance_team@org.com",
  "control_id": "SCF-050",
  "action": "ACTIVATE",
  "from_status": "draft",
  "to_status": "active",
  "reason": "Approved by Compliance Officer",
  "evidence": {
    "approval_ticket": "JIRA-1234",
    "reviewer": "chief_compliance@org.com"
  }
}
```

---

## Conclusion

This architecture enables:
- ✅ **Rapid regulatory response** (PDF → API in minutes)
- ✅ **Auditable control management** (immutable versioning + audit trail)
- ✅ **Executable compliance** (policies testable in isolation or via API)
- ✅ **Scalable validation** (OPA + distributed policy evaluation)
- ✅ **Regulator-grade documentation** (every decision traced and timestamped)

**Next Steps**: Implement each agent, then build out API endpoints and test suite.
