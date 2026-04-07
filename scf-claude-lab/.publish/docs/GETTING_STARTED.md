# SCF Platform – Complete Getting Started Guide

## 🎯 Mission

Transform regulatory PDFs into **executable, testable, auditable compliance controls** with a single command.

```
PDF → Clauses → Controls → Policies → API → Compliance Reports
```

---

## 📦 What You're Getting

### Three Levels of Compliance Automation

| Level | Component | Output | Status |
|-------|-----------|--------|--------|
| **1** | Extract & Filter | Meaningful clauses | ✅ Complete |
| **2** | Generate & Version | Structured controls with history | ✅ Complete |
| **3** | Policy-as-Code | Executable policies + tests | ✅ Complete |

### Deliverables

```bash
✅ agents/               # Modular extraction, control, policy, registry
✅ api/                  # FastAPI with 15+ endpoints
✅ controls/             # Immutable registry with versioning
✅ policies/             # Rego + Python + test cases
✅ tests/                # Unit, integration, policy tests
✅ docs/                 # Architecture, deployment, API ref
✅ Swagger UI            # Interactive API documentation
✅ Audit logging         # Every action tracked
```

---

## 🚀 3-Minute Setup

```bash
# 1. Install
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"

# 2. Run
python -m api.main

# 3. Visit
https://localhost:8000/api/docs
```

Done! 🎉

---

## 💼 Real-World Workflow

### Scenario: New RBI Regulation Released

#### Day 1: Extract & Generate

```bash
# Upload PDF via API
curl -X POST http://localhost:8000/api/v1/controls/generate \
  -F "file=@new_rbi_master_directions.pdf"

# Get: 40+ controls in draft status
# Automatically categorized by domain
# Full audit trail: who generated, when, from what PDF
```

#### Day 2: Review in Swagger

```
http://localhost:8000/api/docs
  → GET /api/v1/controls
  → Enter: domain=Regulatory Compliance
  → View: 12 controls for compliance domain
```

#### Day 3: Activate & Test

```bash
# Activate control
curl -X POST http://localhost:8000/api/v1/controls/SCF-050/activate \
  -d '{"status":"active", "reason":"Approved by Chief 
Compliance Officer", "approval_ticket":"JIRA-5678"}'

# Run policy tests
curl -X POST http://localhost:8000/api/v1/policies/run-tests \
  -d '{"control_id":"SCF-050", "run_positive_tests":true, "run_negative_tests":true}'

# Result: ✅ 2/2 tests passed, 100% compliance
```

#### Day 4: Deploy to Production

```bash
# Export compliance report
curl http://localhost:8000/api/v1/compliance/by-domain > compliance_report.json

# Audit trail for regulators
curl http://localhost:8000/api/v1/audit-log > audit_trail.json

# Ship it!
```

---

## 📐 System Architecture

### Big Picture

```
┌─────────────────────────────────────┐
│   Regulators' PDFs                   │
│   (RBI, SEBI, SEC, etc.)             │
└─────────────┬───────────────────────┘
              │ Upload
              ▼
┌─────────────────────────────────────┐
│   Extract Agent                      │
│   • Clean text                       │
│   • Tokenize sentences               │
│   • Filter by obligation verbs       │
│   • Deduplicate                      │
└─────────────┬───────────────────────┘
              │ Clauses
              ▼
┌─────────────────────────────────────┐
│   Control Agent                      │
│   • Infer domain (Access, Audit, etc)
│   • Classify type (Preventive, etc)  │
│   • Generate objectives              │
│   • Build statements                 │
└─────────────┬───────────────────────┘
              │ Controls v1.0
              ▼
┌─────────────────────────────────────┐
│   Registry Agent (Level 2)           │
│   • Version controls (1.0→1.1→2.0)   │
│   • Manage lifecycle (draft→active)  │
│   • Immutable audit trail            │  
│   • Search index                     │
└─────────────┬───────────────────────┘
              │ Active Controls
              ▼
┌─────────────────────────────────────┐
│   Policy Agent (Level 3)             │
│   • Generate Rego policies           │
│   • Generate Python validators       │
│   • Create test cases                │
│   • Scoring & compliance             │
└─────────────┬───────────────────────┘
              │ Policies + Tests
              ▼
┌─────────────────────────────────────┐
│   FastAPI REST Layer                 │
│   • 15+ endpoints                    │
│   • Swagger/ReDoc docs               │
│   • Audit logging                    │
│   • Error handling                   │
└─────────────┬───────────────────────┘
              │ REST/JSON
              ▼
┌─────────────────────────────────────┐
│   Clients                            │
│   • Postman (manual testing)         │
│   • GRC systems (automated sync)     │
│   • Compliance dashboards            │
│   • Audit systems                    │
└─────────────────────────────────────┘
```

---

## 🔑 Key Concepts

### 1. **Controls**
**Definition**: A structured requirement extracted from regulatory text.

**Structure**:
```json
{
  "control_id": "SCF-001",
  "title": "Broker Enrollment Procedure",
  "objective": "Ensure only authorized brokers can submit claims",
  "control_statement": "Brokers must receive unique code before submitting claims",
  "type": "Preventive",
  "domain": "Access Control",
  "version": "1.1",
  "status": "active"
}
```

### 2. **Versioning** (Level 2)
**Every control is immutable and versioned**:
- v1.0: Initial extraction
- v1.1: Title clarification
- v2.0: Major update after new regulation

**Never delete**: Mark as "deprecated" with reason

### 3. **Lifecycle** (Level 2)
**3 states**:
- `draft` – Not yet approved
- `active` – In production, actively enforced
- `deprecated` – Superseded, no longer used

**Transition requires**:
- Actor (who)
- Timestamp (when)
- Reason (why)
- Optional approval

### 4. **Policies** (Level 3)
**Definition**: Executable rules to validate compliance.

**Two formats**:
1. **Rego** – OPA-compatible; for enterprise deployments
2. **Python** – Vanilla Python; for embedding

**Must include**:
- ✅ Positive test (should PASS)
- ✅ Negative test (should FAIL)
- ✅ Compliance scoring

### 5. **Audit Trail**
**Every action logged**:
```json
{
  "event_id": "EVT-20240327143012-000001",
  "timestamp": "2024-03-27T14:30:12Z",
  "event_type": "control_created",
  "actor": "pdf_generation",
  "reason": "Generated from regulation.pdf",
  "changes": {"version": "1.0"}
}
```

---

## 🎯 Common Tasks

### Task 1: Upload Regulation & Generate Controls

```bash
# Step 1: Prepare PDF
cp ~/Downloads/rbi_master_directions.pdf .

# Step 2: Upload
curl -X POST http://localhost:8000/api/v1/controls/generate \
  -F "file=@rbi_master_directions.pdf"

# Step 3: Check results
curl http://localhost:8000/api/v1/registry | jq '.total_controls'
```

### Task 2: Search for Specific Control

```bash
# By domain
curl "http://localhost:8000/api/v1/controls?domain=Access%20Control"

# By keyword
curl "http://localhost:8000/api/v1/controls?query=broker"

# Combined
curl "http://localhost:8000/api/v1/controls?query=broker&domain=Access%20Control&type=Preventive"
```

### Task 3: Activate Control & Test  Policy

```bash
# Activate
curl -X POST http://localhost:8000/api/v1/controls/SCF-001/activate \
  -d '{"status":"active","actor":"compliance@org.com","reason":"Approved"}'

# Run tests
curl -X POST http://localhost:8000/api/v1/policies/run-tests \
  -d '{"control_id":"SCF-001"}'

# Validate with custom context
curl -X POST http://localhost:8000/api/v1/policies/validate \
  -d '{
    "control_id":"SCF-001",
    "context":{
      "actor_type":"broker",
      "action":"submit_claim",
      "metadata":{"broker_code":"BR0001"}
    }
  }'
```

### Task 4: View Version History

```bash
# Get all versions
curl http://localhost:8000/api/v1/controls/SCF-001/history

# Result: Array of versions with timestamps and reasons
```

### Task 5: Audit Compliance

```bash
# Get all recent events
curl "http://localhost:8000/api/v1/audit-log?limit=20"

# Filter by control
curl "http://localhost:8000/api/v1/audit-log?control_id=SCF-001"

# Filter by date range
curl "http://localhost:8000/api/v1/audit-log?start_date=2024-03-01T00:00:00Z&end_date=2024-03-31T23:59:59Z"
```

### Task 6: Generate Compliance Report

```bash
# By domain
curl http://localhost:8000/api/v1/compliance/by-domain

# Result:
# {
#   "domain": "Access Control",
#   "total_controls": 15,
#   "active_controls": 14,
#   "compliance_percentage": 93.3%
# }
```

---

## 🧪 Testing & Validation

### Run Unit Tests
```bash
pytest tests/test_agents.py -v
```

### Test API Endpoints
```bash
pytest tests/test_api.py -v
```

### Test Policies
```bash
pytest tests/test_policies.py -v
```

### Manual Testing with Postman
```
See: docs/POSTMAN.md for collection
```

---

## 📊 Data Organization

### controls/ Directory
```
controls/
├── controls_registry.json    # Master registry (all versions)
├── controls_v1.0.yaml       # Historical snapshot
├── controls_v1.1.yaml       # Historical snapshot
└── risk_registry.json        # Risk catalog
```

### policies/ Directory
```
policies/
├── SCF-001-v1-0/
│   ├── policy.rego           # OPA policy
│   ├── policy.py             # Python policy
│   ├── positive_test.json    # Valid case
│   ├── negative_test.json    # Invalid case
│   └── README.md             # Documentation
└── SCF-002-v1-0/
    └── [same structure]
```

---

## 🔒 Security & Compliance

### Audit Logging
✅ Every operation logged  
✅ Actor, timestamp, reason captured  
✅ Immutable append-only log  
✅ Queryable by date range, control, actor  

### Version Control
✅ Never delete controls (only deprecate)  
✅ Full change history  
✅ Reason for every change required  
✅ Previous versions always accessible  

### Policy Enforcement
✅ Policies are testable  
✅ Compliance metrics quantified  
✅ Pass/FAIL decisions audited  
✅ Test cases in git-tracking  

---

## 🚀 Production Deployment

### Docker
```bash
docker build -t scf:2.0 .
docker run -p 8000:8000 scf:2.0
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

### Enterprise
- Enable HTTPS/TLS
- Add authentication (JWT/OAuth2)
- Set up centralized logging (ELK)
- Configure monitoring (Prometheus)
- Add rate limiting
- Document runbooks

See [DEPLOYMENT.md](../DEPLOYMENT.md) for details.

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| "NLTK models not found" | `python -c "import nltk; nltk.download('punkt')"` |
| "Port 8000 in use" | `lsof -i :8000` then `kill -9 <PID>` |
| "PyPDF2 error" | `pip install --upgrade PyPDF2` |
| "Policy not found" | Check `policies/` dir exists with correct structure |

---

## ✨ What Makes This Enterprise-Grade?

### ✅ Immutability
Controls are never modified—only versioned. Old versions always accessible.

### ✅ Auditability
Every change logged: who, when, why, what. Useful for regulators.

### ✅ Testability
Policy test cases (positive + negative). CI/CD ready.

### ✅ Scalability
REST API. Easy to integrate with other systems (GRC, dashboards).

### ✅ Compliance
Automatically categorized by domain (Access, Audit, Finance, etc.).

### ✅ Documentation
Every endpoint documented. Swagger/ReDoc included.

---

## 📚 Next Steps

1. **Setup**: Follow "3-Minute Setup" above ✅
2. **Upload PDF**: Use Generate endpoint
3. **Explore API**: Visit Swagger UI
4. **Test Policies**: Run test suite
5. **Deploy**: Follow [DEPLOYMENT.md](../DEPLOYMENT.md)

---

## 🎓 Learn More

- [ARCHITECTURE.md](../ARCHITECTURE.md) – System design deep-dive
- [DEPLOYMENT.md](../DEPLOYMENT.md) – Production setup
- [docs/POSTMAN.md](POSTMAN.md) – API testing
- [http://localhost:8000/api/docs](http://localhost:8000/api/docs) – Interactive docs

---

## 💡 Pro Tips

### 1. **Use Environment Variables**
```bash
export BASE_URL="http://localhost:8000"
export API_KEY="your-secret-key"

curl $BASE_URL/api/v1/registry \
  -H "Authorization: Bearer $API_KEY"
```

### 2. **Batch Operations**
```bash
# Generate, activate, and test all at once
for control in $(curl $BASE_URL/api/v1/controls | jq '.[] | .control_id'); do
  curl -X POST $BASE_URL/api/v1/controls/$control/activate \
    -d '{"status":"active","actor":"system"}'
done
```

### 3. **Export for Audit**
```bash
# Annual compliance snapshot
curl $BASE_URL/api/v1/registry | jq . > compliance_snapshot_2024Q1.json
curl $BASE_URL/api/v1/audit-log | jq . > audit_trail_2024Q1.json
```

---

<div align="center">

## 🎯 Ready?

[Start Installation](#-3-minute-setup) | [View Docs](../docs/) | [Open Swagger](http://localhost:8000/api/docs)

**Questions?** Check troubleshooting or docs.

</div>

---

*Platform Version: 2.0.0*  
*Last Updated: 2024-03-27*  
*Status: Production Ready*
