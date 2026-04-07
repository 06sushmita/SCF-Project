# 📑 SCF Platform – Documentation Index

Quick navigation to all project documentation and resources.

---

## 🚀 Getting Started

**New to SCF?** Start here:
1. **[README.md](../README.md)** – Platform overview + 3-minute setup
2. **[docs/GETTING_STARTED.md](GETTING_STARTED.md)** – Detailed setup guide
3. **[Swagger UI](http://localhost:8000/api/docs)** – Interactive API (after starting server)

---

## 📚 Documentation

### Core System
| Document | Purpose | Audience |
|----------|---------|----------|
| **[ARCHITECTURE.md](../ARCHITECTURE.md)** | Technical design & component details | Developers, Architects |
| **[docs/GETTING_STARTED.md](GETTING_STARTED.md)** | Setup, installation, first run | Everyone |
| **[README.md](../README.md)** | Platform overview & quick start | Everyone |

### API & Integration
| Document | Purpose |
|---|---|
| **[docs/POSTMAN.md](POSTMAN.md)** | Postman collection + API examples |
| **[Swagger UI](http://localhost:8000/api/docs)** | Interactive API explorer (live) |
| **[ReDoc](http://localhost:8000/api/redoc)** | API documentation (live) |

---

## 📂 Project Structure

```
scf-claude-lab/
│
├── 📄 README.md                 👈 START HERE
├── 📄 ARCHITECTURE.md           Technical design
├── 📄 requirements.txt          Python dependencies
│
├── 📁 agents/                   Core compliance engine
│   ├── extract.py              PDF → Clauses
│   ├── control.py              Clauses → Controls
│   ├── policy.py               Controls → Policies (Rego)
│   ├── registry.py             Versioning & lifecycle (Level 2)
│   ├── registry_v2.py          Registry with YAML support
│   ├── policy_generator_v2.py  Policy generation from YAML
│   └── models.py               Data structures
│
├── 📁 api/                      FastAPI REST layer
│   ├── main.py                 API endpoints + Swagger setup
│   └── schemas.py              Pydantic models
│
├── 📁 policies/                 Policy packages
│   ├── README.md               Policy overview
│   └── SCF-001-v1-0/           Sample policy package
│       ├── policy.rego         OPA/Rego policy
│       ├── evaluator.py        Python policy validator
│       ├── positive_test.json  Valid scenario
│       ├── negative_test.json  Invalid scenario
│       ├── evaluation_output.json  Test results
│       ├── README.md           Policy documentation
│       └── LEVEL3_SUMMARY.md   Acceptance criteria verification
│
├── 📁 controls/                 Control registry
│   └── controls_registry.json  Versioned control registry
│
├── 📁 level1/                   Original Level 1 assets
│   ├── controls.yaml           📌 Single source of truth
│   ├── generate.py             Demo generation script
│   └── risk.json               Risk categorization
│
├── 📁 docs/                     Documentation
│   ├── README.md               Documentation home
│   ├── GETTING_STARTED.md      Setup instructions
│   └── POSTMAN.md              API testing guide
│
├── 📁 tests/                    Test suites
│   ├── test_agents.py          Unit tests
│   └── test_policies.py        Policy validation tests
│
├── 📁 schemas/                  JSON schemas
├── 📁 templates/                Control templates
├── 📁 rules/                    Policy rules
└── 📁 tools/                    Utility scripts
```

---

## 🔌 API Quick Reference

### Health & Info
```bash
GET /health                      # Service status
GET /api/v1/info                # System information
```

### Controls
```bash
GET  /api/v1/controls           # List all controls
POST /api/v1/controls/generate  # Extract controls from PDF
GET  /api/v1/controls/{id}      # Get control details
```

### Policies
```bash
GET  /api/v1/policies/{id}      # Get policy
POST /api/v1/policies/validate  # Validate policy
```

### Registry & Audit
```bash
GET /api/v1/registry            # Registry metadata
GET /api/v1/audit-log           # Audit trail
```

**➡️ Full API docs: http://localhost:8000/api/docs (after starting server)**

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_agents.py -v

# Run with coverage
pytest --cov=agents tests/
```

---

## 🤖 Agents (Core System)

### Extract Agent
Reads PDFs, extracts clauses, removes duplicates

```bash
python agents/extract.py <pdf_file>
```

### Control Agent
Generates controls from clauses

```bash
python agents/control.py
```

### Policy Agent  
Converts controls to Rego + Python policies

```bash
python agents/policy.py
```

### Registry Agent
Manages versioning and lifecycle

```bash
python agents/registry.py
```

---

## 📊 Example Workflows

### 1. Extract Controls from PDF
```bash
POST /api/v1/controls/generate
Upload: regulatory_document.pdf
Response: 45 controls generated in 'draft' status
```

### 2. Validate Control via Policy
```bash
POST /api/v1/policies/validate
Input: { control_id: "SCF-001", context: {...} }
Response: { result: "PASS", compliance_score: 100.0 }
```

### 3. Search Controls by Domain
```bash
GET /api/v1/controls?domain=Access+Control
Response: 12 access control policies found
```

### 4. Get Control Version History
```bash
GET /api/v1/controls/SCF-001/history
Response: [v1.0, v1.1, v2.0, ...] with changelog
```

---

## 🎯 Key Concepts

| Term | Definition |
|------|-----------|
| **Control** | A regulatory requirement extracted from PDF |
| **Policy** | Executable logic (Rego/Python) that enforces a control |
| **Registry** | Versioned, lifecycle-tracked store of all controls |
| **Compliance Score** | Percentage of policy requirements met (0-100%) |
| **Rego** | OPA policy language (declarative, high-assurance) |
| **YAML** | Single source of truth for control definitions |

---

## 🚨 Troubleshooting

### API won't start
```bash
# Check port 8000 is free
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Reset and try again
pip install -r requirements.txt --force-reinstall
python -m api.main
```

### Import errors
```bash
# Reinstall NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Verify Python version
python --version  # Should be 3.9+
```

### Policy evaluation fails
```bash
# Check test file format
cat policies/SCF-001-v1-0/positive_test.json

# Run evaluator directly
cd policies/SCF-001-v1-0
python evaluator.py
```

---

## 📞 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OPA/Rego Docs**: https://www.openpolicyagent.org/
- **Swagger UI**: http://localhost:8000/api/docs
- **Project README**: [README.md](../README.md)
- **Architecture Details**: [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Last Updated**: March 30, 2026  
**Platform Version**: 2.0  
**Status**: Production Ready ✅
