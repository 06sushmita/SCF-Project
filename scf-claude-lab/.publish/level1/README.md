# 📦 Level 1 - Legacy Extraction System (Original Implementation)

This folder contains the **original Level 1 implementation** of the SCF system - the proof-of-concept that extracts regulatory text from PDFs into compliance clauses. 

⚠️ **Status**: LEGACY - Superseded by the modular agents system, but kept for reference and historical context.

---

## 📂 Files & Importance

### 🟡 **REFERENCE ONLY** (Historical/Backup)

#### **generate.py** | Importance: 🌟🌟
- **Purpose**: Original PDF extraction script (Level 1)
- **Functionality**:
  - PDF text extraction
  - Sentence tokenization
  - Duplicate removal (Jaccard similarity)
  - Obligation filtering
- **Status**: Replaced by [../agents/extract.py](../agents/extract.py)
- **Why Kept**: Reference implementation; can compare with new version
- **Usage**: 
  ```bash
  python level1/generate.py <pdf_file>
  # Output: Extracted clauses (printed to stdout)
  ```
- **Differences from New System**:
  - No API layer (CLI only)
  - No versioning/lifecycle
  - No audit trail
  - No structured data models

---

#### **controls.yaml** | Importance: 🌟
- **Purpose**: Historical control output snapshot from original system
- **Format**: YAML (one control per entry)
- **Contains**: Controls generated from sample regulatory documents
- **Status**: ARCHIVED (not updated)
- **Usage**: Reference - shows what Level 1 output looked like
- **Replaced By**: [../controls/controls_registry.json](../controls/controls_registry.json) (JSON format, with versioning)

---

#### **word_library.py** | Importance: 🌟
- **Purpose**: Keyword mappings for domain/obligation detection
- **Contains**:
  - Obligation verbs (must, shall, will, should, may, etc.)
  - Domain keywords (Access Control, Data Protection, etc.)
  - Stop words
- **Usage**: Referenced by `generate.py` for filtering/classification
- **Status**: Still used by legacy extract.py; can be refactored into agents/models.py

---

#### **risk.json** | Importance: 🌟
- **Purpose**: Risk/compliance metadata for original extractions
- **Format**: JSON
- **Contains**: Risk scores, compliance domains, severity levels
- **Status**: ARCHIVED (not updated)
- **Note**: Superseded by risk data in [controls_registry.json](../controls/controls_registry.json)

---

#### **rejected_clauses.txt** | Importance: 🌟
- **Purpose**: Log of clauses filtered out during extraction
- **Contains**: Plain text lines that were deduplicated or marked as noise
- **Usage**: Quality review - shows what extraction logic filtered
- **Status**: Historical reference only
- **Note**: Current system has equivalent filtering in `ExtractAgent`

---

## 🔄 Migration Path

```
Original Level 1 (level1/)
├── generate.py
├── controls.yaml
├── word_library.py
└── risk.json
    ↓ (refactored into)
Modern Modular System (agents/)
├── extract.py (uses word_library)
├── control.py
├── registry.py
├── policy.py
└── models.py
    ↓ (exposed via)
REST API (api/)
├── main.py
└── schemas.py
```

---

## 📊 Comparison: Old vs. New

| Feature | Level 1 (Legacy) | Modern System |
|---------|------------------|---------------|
| **Execution** | CLI script | REST API + CLI |
| **Versioning** | None | Immutable versions (1.0 → 1.1 → 2.0) |
| **Lifecycle** | N/A | draft → active → deprecated → archived |
| **Audit Trail** | No | Complete (who, when, why) |
| **Search/Filter** | grep only | Full-text, faceted, tagged |
| **Policy Generation** | None | Rego + Python |
| **Test Cases** | Manual | Auto-generated positive/negative tests |
| **API** | None | 15+ REST endpoints |
| **Type Safety** | Untyped | Pydantic validation |
| **Documentation** | README only | Swagger + ReDoc + Guides |

---

## ⚠️ Do NOT Modify

- Do **NOT** update files in this folder (legacy)
- Do **NOT** use `generate.py` for new extractions (use API instead)
- Do **NOT** commit new history to YAML/JSON here

---

## 🔗 Migration Guide

If you need to:

| Need | Use This | Not This |
|------|----------|----------|
| Extract PDF → clauses | [../api/main.py](../api/main.py) POST `/api/v1/controls/generate` | `level1/generate.py` |
| View control registry | [../controls/controls_registry.json](../controls/controls_registry.json) | `level1/controls.yaml` |
| Search controls | [../api/main.py](../api/main.py) GET `/api/v1/controls?query=...` | `grep` on YAML |
| Generate policies | [../agents/policy.py](../agents/policy.py) | Not available in Level 1 |

---

## 📚 Reference

See [../IMPLEMENTATION_COMPLETE.md](../IMPLEMENTATION_COMPLETE.md) for migration summary.
