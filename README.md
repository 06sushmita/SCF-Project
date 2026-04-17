# 🔐 Secure Control Framework (SCF) Platform

**Enterprise-grade regulatory compliance automation system.**

Transform regulatory PDFs → Versioned Controls → Executable Policies → API-Driven Compliance Engine

[![Platform](https://img.shields.io/badge/Platform-FastAPI-009688?style=flat)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?style=flat)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat)]()

---

> 🎉 **New to SCF?** Start with [START_HERE.md](START_HERE.md) for comprehensive setup guide + navigation  
> 📚 **Full Documentation Hub**: See [docs/INDEX.md](docs/INDEX.md)

---




| Level | Feature | Status |
|-------|---------|--------|
| **1. Extraction** | PDF parsing, clause extraction, deduplication | ✅ Complete |
| **2. Registry** | Versioned control management, lifecycle tracking | ✅ Complete |
| **3. Policy-as-Code** | Rego policies, test cases, compliance scoring | ✅ Complete |
| **API & Docs** | FastAPI, Swagger, REST endpoints | ✅ Complete |

---

## 🚀 Quick Start 

### 1. Install

```bash
cd scf-claude-lab

# Setup environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Start API

```bash
python -m api.main
```

You'll see:
```
INFO:     Uvicorn running on http://localhost:8000
```

### 3. Access Interfaces

| Interface | URL | Purpose |
|-----------|-----|---------|
| **Swagger UI** | http://localhost:8000/api/docs | Interactive API testing |
| **ReDoc** | http://localhost:8000/api/redoc | API documentation |
| **Health Check** | http://localhost:8000/health | API status |

---

## 📂 Project Structure

```
scf-claude-lab/
├── agents/                    # Core compliance engine
│   ├── models.py             # Data structures
│   ├── extract.py            # PDF extraction
│   ├── control.py            # Control generation
│   ├── policy.py             # Policy generation
│   ├── registry.py           # Versioning & lifecycle
│   └── registry_v2.py        # Level 2 registry (reads control.yaml)
│
├── api/                       # REST API
│   ├── main.py               # FastAPI app + endpoints
│   └── schemas.py            # Pydantic models
│
├── policies/                  # Policy packages
│   ├── README.md             # Policy overview
│   └── SCF-001-v1-0/
│       ├── policy.rego       # OPA policy
│       ├── evaluator.py      # Python validator
│       ├── positive_test.json
│       ├── negative_test.json
│       └── evaluation_output.json
│
├── controls/                  # Control registry
│   └── controls_registry.json
│
├── docs/                      # Documentation
│   ├── GETTING_STARTED.md    # Detailed setup guide
│   └── POSTMAN.md            # API testing
│
├── level1/
│   ├── controls.yaml         # 📌 Single source of truth
│   └── generate.py
│
├── schemas/                   # JSON schemas
├── tests/                     # Unit tests
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

---

## 🔌 API Endpoints

### Control Operations
```bash
POST /api/v1/controls/generate      # Extract & generate controls
GET  /api/v1/controls              # List controls
GET  /api/v1/controls/{id}         # Get specific control
POST /api/v1/controls/{id}/activate # Activate control
```

### Policy Validation
```bash
POST /api/v1/policies/validate     # Validate policy
GET  /api/v1/policies/{id}         # Get policy
```

### Registry & Audit
```bash
GET  /api/v1/registry              # Registry metadata
GET  /api/v1/audit-log             # Audit trail
GET  /api/v1/compliance/by-domain  # Compliance report
```

**➡️ Try in Swagger UI: http://localhost:8000/api/docs**

---

## 📚 Detailed Documentation

### Getting Started
See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for:
- Detailed setup instructions
- Example workflows
- Common scenarios

### API Testing
See [docs/POSTMAN.md](docs/POSTMAN.md) for:
- Postman collection setup
- Sample requests
- API examples

### System Architecture  
See [ARCHITECTURE.md](ARCHITECTURE.md) for:
- Technical design
- Component interactions
- Data flows

---

## 🧪 Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_agents.py

# Run with coverage
pytest --cov=agents tests/
```

---

## 💡 Usage Examples

### Via API (Swagger UI)

1. Visit http://localhost:8000/api/docs
2. Click on any endpoint
3. Click "Try it out"
4. Modify request (if needed)
5. Click "Execute"

### Via Python

```python
from agents import ControlRegistry, PolicyAgent

# Load controls from YAML
registry = ControlRegistry("level1/controls.yaml")
registry.print_summary()

# Generate policies
generator = PolicyAgent()
generator.generate_all_policies()
```

### Via CLI

```bash
# Level 2: Control Registry (reads control.yaml)
python agents/registry_v2.py

# Level 3: Policy Generator
python agents/policy_generator_v2.py
```

---

## 📊 Platform Features

### Level 1: Extraction
✅ PDF parsing with NLTK  
✅ Clause extraction & filtering  
✅ Duplicate detection (Jaccard similarity)  
✅ Clean compliance clause output  

### Level 2: Control Registry
✅ Versioned control management  
✅ Lifecycle tracking (draft → active → deprecated)  
✅ Full audit trail  
✅ Searchable by domain/type  

### Level 3: Policy-as-Code  
✅ Automatic Rego policy generation  
✅ Positive & negative test cases  
✅ Compliance scoring (0-100%)  
✅ Deterministic pass/fail results  

### API & Integration
✅ FastAPI with OpenAPI/Swagger  
✅ 15+ REST endpoints  
✅ Request/response validation  
✅ Comprehensive audit logging  

---

## 🔑 Key Concepts

**Control**: Regulatory requirement extracted from PDF  
**Policy**: Executable logic (Rego) that enforces a control  
**Registry**: Versioned, lifecycle-tracked store of controls  
**Compliance Score**: Percentage of policy requirements met (0-100%)  

---

## ⚙️ Technology Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Policy Language | OPA/Rego |
| CLI/Scripting | Python 3.9+ |
| Text Processing | NLTK |
| Configuration | YAML |
| Database | JSON (file-based) |
| Testing | pytest |

---

## 📝 License

MIT License - See LICENSE file

---

## 📞 Support

For detailed documentation:
- **Setup Issues**: See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- **API Questions**: Visit http://localhost:8000/api/docs (Swagger)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
