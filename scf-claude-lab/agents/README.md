# 🤖 Agents Module - Core Business Logic

This module contains the **five core agents** that handle all compliance control automation. These are the heart of the SCF platform.

---

## 📂 Files & Importance

### 🔴 **CRITICAL** (Must Exist & Work)

#### **models.py** | Importance: 🌟🌟🌟🌟🌟
- **Purpose**: Defines immutable data structures for the entire system
- **Contains**: 
  - `Control` – Represents a single compliance control
  - `Version` – Version history tracking
  - `Audit` – Immutable audit log entries
  - `Policy` – Policy specifications
  - `TestCase` – Test case definitions
- **Why Critical**: Every other module imports from here. Data model bugs cascade everywhere.
- **Users**: All agents depend on this; API schemas use these
- **Maintenance**: Changes here require coordination across all modules

---

#### **extract.py** | Importance: 🌟🌟🌟🌟
- **Purpose**: Level 1 - Converts raw regulatory PDFs into structured clauses
- **Contains**: `ExtractAgent` class
- **Process**:
  1. PDF text extraction (PyPDF2)
  2. Sentence tokenization (NLTK Punkt)
  3. Noise filtering (circular refs, addresses, gibberish)
  4. Duplicate removal (Jaccard similarity ≥ 0.72)
- **Input**: PDF binary + metadata
- **Output**: List of cleaned, deduplicated clauses
- **Usage**: API endpoint `/api/v1/controls/generate` → ExtractAgent
- **Critical for**: PDF compliance document ingestion

---

#### **control.py** | Importance: 🌟🌟🌟🌟
- **Purpose**: Level 1+ - Converts clauses into structured compliance controls
- **Contains**: `ControlAgent` class
- **Process**:
  1. Domain inference (keyword matching → 8 domains)
  2. Type classification (Preventive/Detective/Corrective)
  3. Title generation (7-word noun phrases)
  4. Objective creation (domain-specific templates + topic extraction)
  5. Statement normalization (modal verbs, enumerations)
- **Input**: Extracted clauses
- **Output**: Structured `Control` objects with metadata
- **Usage**: API → Control search/create workflow
- **Critical for**: Converting free text into actionable controls

---

#### **registry.py** | Importance: 🌟🌟🌟🌟
- **Purpose**: Level 2 - Manages control versioning & lifecycle
- **Contains**: `RegistryAgent` class
- **Capabilities**:
  - Immutable version history (1.0 → 1.1 → 2.0)
  - Lifecycle (draft → active → deprecated → archived)
  - Full audit trail (who changed what, when, why)
  - Search/filter/tag operations
  - Conflict detection (version collisions)
- **Data Store**: [controls_registry.json](../controls/controls_registry.json)
- **Usage**: API endpoints for control CRUD, versioning, status changes
- **Critical for**: Compliance traceability & audit requirements

---

#### **policy.py** | Importance: 🌟🌟🌟
- **Purpose**: Level 3 - Converts controls into executable policies
- **Contains**: `PolicyAgent` class
- **Generates**:
  - **Rego policies** (OPA-compatible, cloud-native)
  - **Python validators** (embeddable in Python apps)
  - **Test cases** (positive + negative examples)
  - **Compliance scoring** (0-100%)
- **Input**: Structured `Control` objects
- **Output**: Policy artifacts in `policies/` folder
- **Usage**: API endpoint `/api/v1/policies/{control_id}`
- **Critical for**: Converting controls to enforcement code

---

### 🟡 **IMPORTANT** (Infrastructure)

#### **__init__.py** | Importance: 🌟🌟
- **Purpose**: Makes `agents/` a Python package
- **Current**: Empty (agents imported directly)
- **Could contain**: Convenience imports (e.g., `from agents import ExtractAgent`)

---

## 🔄 Agent Dependency Graph

```
User Input (PDF)
    ↓
ExtractAgent (Level 1: Extract) 
    ↓ [clauses]
ControlAgent (Level 1+: Structure)
    ↓ [controls]
RegistryAgent (Level 2: Versioning)
    ↓ [versioned controls]
PolicyAgent (Level 3: Policies)
    ↓ [executable policies]
Output (Rego + Python + Tests)
```

---

## 🧪 Testing

- **Test File**: `../tests/test_agents.py`
- **Coverage**: All 5 agents have test cases
- **Run Tests**:
  ```bash
  pytest tests/test_agents.py -v
  ```

---

## 🔗 Related Files

| File | Relationship |
|------|--------------|
| [../api/main.py](../api/main.py) | Imports & orchestrates these agents |
| [../api/schemas.py](../api/schemas.py) | Uses models.py data structures |
| [../controls/controls_registry.json](../controls/controls_registry.json) | Persistent storage for RegistryAgent |
| [../policies/](../policies/) | Output destination for PolicyAgent |
