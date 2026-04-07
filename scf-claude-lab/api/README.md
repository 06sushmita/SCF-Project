# 🌐 API Module - REST Layer

This module exposes the SCF platform capabilities via a **production-ready FastAPI REST API** with 15+ endpoints, Swagger documentation, and Pydantic validation.

---

## 📂 Files & Importance

### 🔴 **CRITICAL** (Must Exist & Work)

#### **main.py** | Importance: 🌟🌟🌟🌟🌟
- **Purpose**: FastAPI application entry point - defines all REST endpoints
- **Contains**:
  - FastAPI app initialization
  - 15+ endpoint definitions (Control CRUD, Policy validation, Registry queries, Health checks)
  - Error handling & middleware
  - CORS configuration
  - Swagger/ReDoc auto-documentation
- **Key Endpoints**:
  - `GET /health` – Liveness check
  - `POST /api/v1/controls/generate` – Generate controls from PDF
  - `GET /api/v1/controls` – Search controls (query, domain, type, status)
  - `GET /api/v1/controls/{id}` – Get single control
  - `PATCH /api/v1/controls/{id}` – Update control (creates new version)
  - `POST /api/v1/controls/{id}/activate` – Activate control
  - `POST /api/v1/controls/{id}/deprecate` – Deprecate control
  - <b>+ 8 more policy & registry endpoints</b>
- **Used By**: FastAPI server startup; external services calling the API
- **Critical for**: All API functionality; platform accessibility
- **How to Run**:
  ```bash
  python -m api.main
  # Output: Application startup complete [press Ctrl+C to quit]
  # Access: http://localhost:8000/api/docs (Swagger UI)
  ```
- **Port**: 8000 (configurable via environment)

---

#### **schemas.py** | Importance: 🌟🌟🌟🌟
- **Purpose**: Pydantic validation models for all API request/response payloads
- **Contains**:
  - `ControlSchema` – Request/response model for controls
  - `CreateControlRequest` – Payload for creating new controls
  - `UpdateControlRequest` – Payload for updating controls
  - `PolicySchema` – Policy model
  - `SearchFiltersSchema` – Query parameter models
  - `ErrorSchema` – Error response format
  - `AuditSchema` – Audit log entry format
  - ~15 additional validation models
- **Purpose**: 
  - Automatic request validation (rejects invalid JSON)
  - Type hints for IDE autocomplete
  - Auto-generated API docs (Swagger reads these)
  - Runtime type checking
- **Used By**: 
  - All endpoints in `main.py`
  - Swagger/ReDoc documentation generation
  - FastAPI auto-validation middleware
- **Critical for**: 
  - API reliability (bad requests caught early)
  - Documentation accuracy
  - Type safety

---

#### **__init__.py** | Importance: 🌟
- **Purpose**: Makes `api/` a Python package
- **Current**: Typically empty; could import FastAPI app for external use

---

## 🔗 Connections to Other Modules

| Import | From | Used For |
|--------|------|----------|
| `ExtractAgent, ControlAgent, PolicyAgent, RegistryAgent` | `../agents/*` | Orchestrate platform logic in endpoints |
| `Control, Version, Audit, Policy` | `../agents/models.py` | Define data structures |
| `ControlSchema, CreateControlRequest, etc.` | `schemas.py` | Validate/document requests |

---

## 📊 API Workflow Example

```
Client Request (JSON)
    ↓
FastAPI Middleware (CORS, logging)
    ↓
Endpoint Handler in main.py
    ↓
Pydantic Validation (schemas.py)
    ↓
Agent Orchestration (extract.py → control.py → registry.py)
    ↓
Response Model Validation (schemas.py)
    ↓
JSON Response → Client
```

---

## 🧪 Testing

- **API Tests**: Use Swagger UI at `http://localhost:8000/api/docs`
- **Postman Collection**: See [../docs/POSTMAN.md](../docs/POSTMAN.md)
- **Unit Tests**: Run `pytest tests/test_agents.py -v`

---

## 🔐 Deployment Considerations

| Aspect | Details |
|--------|---------|
| Port | 8000 (change via `PORT` env var) |
| Host | 127.0.0.1 (localhost only by default) |
| CORS | Enabled for `*` (restrict in production) |
| Docs | Enabled at `/api/docs` (disable in production) |
| Logging | INFO level (change to WARNING in prod) |

For production deployment, see [../DEPLOYMENT.md](../DEPLOYMENT.md).
