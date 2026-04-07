# Postman Collection Guide

## Import Collection

1. Open Postman
2. Click **File** → **Import**
3. Choose **Raw Text** and paste the JSON below, OR
4. Download [scf-platform-collection.json](./scf-platform-collection.json)
5. Import environment file: [scf-environment.json](./scf-environment.json)

---

## Collection Structure

```
SCF Platform
├── System
│   ├── Health Check
│   └── Platform Info
├── Control Generation
│   └── Generate Controls from PDF
├── Control Management
│   ├── Create Control
│   ├── Get Control (Active Version)
│   ├── Get Control History
│   ├── Search Controls
│   ├── Update Control
│   ├── Activate Control
│   └── Deprecate Control
├── Policy Validation
│   ├── Validate Policy (Valid Case)
│   ├── Validate Policy (Invalid Case)
│   └── Run Policy Tests
├── Registry & Compliance
│   ├── Get Registry Metadata
│   ├── Get Audit Log
│   └── Get Compliance Report
```

---

## Environment Setup

### Create Variables

In Postman Environment, add:

```json
{
  "base_url": "http://localhost:8000",
  "api_version": "v1",
  "control_id": "SCF-001",
  "actor": "test_user@org.com",
  "timestamp": "{{$timestamp}}"
}
```

### Environment file (`scf-environment.json`):

```json
{
  "name": "SCF Platform",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "api_version",
      "value": "v1",
      "enabled": true
    },
    {
      "key": "control_id",
      "value": "SCF-001",
      "enabled": true
    }
  ]
}
```

---

## Key Endpoints

### 1. Health Check

**GET** `{{base_url}}/health`

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2024-03-27T14:30:00.000000",
  "version": "2.0.0",
  "services": {
    "registry": "operational",
    "extraction": "operational",
    "control_generation": "operational",
    "policy_engine": "operational"
  }
}
```

---

### 2. Generate Controls from PDF

**POST** `{{base_url}}/api/{{api_version}}/controls/generate`

**Body**: Form-data → file (PDF)

```
Key: file
Value: [Select PDF file]
```

**Pre-request Script**:
```javascript
// No special setup needed
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "message": "45 controls extracted and registered",
  "controls_generated": 45,
  "controls": [
    {
      "control_id": "SCF-001",
      "title": "Broker Enrollment Procedure",
      "version": "1.0",
      "status": "draft",
      "control_domain": "Access Control"
    }
  ],
  "timestamp": "2024-03-27T14:35:00Z"
}
```

**Test Script (Postman Tests tab)**:
```javascript
pm.test("Status is success", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql("success");
});

pm.test("Controls generated count > 0", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.controls_generated).to.be.greaterThan(0);
});

// Set control ID for subsequent tests
if (pm.response.code === 200) {
    var data = pm.response.json();
    pm.environment.set("control_id", data.controls[0].control_id);
}
```

---

### 3. Search Controls

**GET** `{{base_url}}/api/{{api_version}}/controls?query=broker&domain=Access+Control&limit=10`

**Query Parameters**:
| Name | Value | Type |
|------|-------|------|
| query | broker | string |
| domain | Access Control | string |
| control_type | Preventive | string (optional) |
| status | active | string (optional) |
| limit | 10 | number |

**Response (200 OK)**:
```json
[
  {
    "control_id": "SCF-001",
    "title": "Broker Enrollment Procedure",
    "version": "1.0",
    "status": "draft",
    "domain": "Access Control",
    "control_type": "Preventive",
    "relevance_score": 0.95
  }
]
```

---

### 4. Get Control (Active Version)

**GET** `{{base_url}}/api/{{api_version}}/controls/{{control_id}}`

**Query Parameters**:
| Name | Value |
|------|-------|
| version | active |

**Response (200 OK)**:
```json
{
  "control_id": "SCF-001",
  "version": "1.0",
  "title": "Broker Enrollment Procedure",
  "objective": "Ensure only authorised and verified brokers are permitted to submit claims.",
  "control_statement": "Brokers must submit enrollment requests on formal letterhead...",
  "control_domain": "Access Control",
  "control_family": "Third-Party and Agent Management",
  "control_type": "Preventive",
  "status": "active",
  "created_date": "2024-03-27T14:00:00Z",
  "created_by": "system",
  "risk_addressed": "Unauthorized or fraudulent access by unverified brokers...",
  "evidence_required": "Broker/agent registration register; unique code assignment logs...",
  "metrics": "% of applications bearing a valid registered broker code...",
  "assumptions": "Receiving Offices maintain a formal broker registry..."
}
```

---

### 5. Create Control

**POST** `{{base_url}}/api/{{api_version}}/controls`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "title": "NRI Nomination Eligibility Verification",
  "objective": "Ensure NRI nominations comply with scheme-specific eligibility rules",
  "control_statement": "Organizations must verify that NRI nominees are eligible for the relevant bond scheme before accepting nominations.",
  "control_domain": "Regulatory Compliance",
  "control_family": "Financial and Legal Compliance",
  "control_type": "Preventive",
  "risk_addressed": "Regulatory violations from ineligible NRI nominations",
  "evidence_required": "NRI eligibility checklists; rejection logs; approved nomination records",
  "metrics": "Number of NRI eligibility errors detected; % of nominations verified before acceptance",
  "assumptions": "Receiving Offices maintain current scheme eligibility matrix",
  "actor": "{{actor}}"
}
```

**Response (200 OK)**:
```json
{
  "control_id": "SCF-050",
  "version": "1.0",
  "title": "NRI Nomination Eligibility Verification",
  "status": "draft",
  ...
}
```

---

### 6. Update Control (New Version)

**PATCH** `{{base_url}}/api/{{api_version}}/controls/{{control_id}}`

**Body** (JSON):
```json
{
  "title": "Enhanced NRI Nomination Eligibility Verification",
  "objective": "Ensure NRI nominations strictly comply with scheme-specific eligibility rules with automated verification",
  "reason": "Added automated verification requirement for faster processing",
  "actor": "{{actor}}"
}
```

**Response (200 OK)**:
```json
{
  "control_id": "SCF-001",
  "version": "1.1",
  "title": "Enhanced NRI Nomination Eligibility Verification",
  "status": "draft",
  "amended_from_version": "1.0",
  ...
}
```

---

### 7. Activate Control

**POST** `{{base_url}}/api/{{api_version}}/controls/{{control_id}}/activate`

**Body** (JSON):
```json
{
  "status": "active",
  "reason": "Approved by compliance team after internal review",
  "actor": "{{actor}}",
  "approval_ticket": "JIRA-1234"
}
```

**Response (200 OK)**:
```json
{
  "control_id": "SCF-001",
  "version": "1.1",
  "status": "active",
  ...
}
```

---

### 8. Validate Policy

**POST** `{{base_url}}/api/{{api_version}}/policies/validate`

**Body** (JSON):
```json
{
  "control_id": "{{control_id}}",
  "context": {
    "actor_type": "broker",
    "action": "submit_claim",
    "metadata": {
      "has_enrollment_letter": true,
      "broker_code": "BR0001",
      "registered_brokers": ["BR0001", "BR0002", "BR0003"],
      "timestamp": "{{timestamp}}"
    }
  },
  "policy_type": "python"
}
```

**Response (200 OK)**:
```json
{
  "control_id": "SCF-001",
  "policy_name": "Broker Enrollment Procedure",
  "result": "PASS",
  "violations": [],
  "compliance_score": 1.0,
  "evidence_collected": {
    "actor_type": "broker",
    "action": "submit_claim",
    "metadata": {...}
  },
  "timestamp": "2024-03-27T14:40:00Z"
}
```

---

### 9. Run Policy Tests

**POST** `{{base_url}}/api/{{api_version}}/policies/run-tests`

**Body** (JSON):
```json
{
  "control_id": "{{control_id}}",
  "run_positive_tests": true,
  "run_negative_tests": true
}
```

**Response (200 OK)**:
```json
{
  "control_id": "SCF-001",
  "total_tests": 2,
  "passed_tests": 2,
  "failed_tests": 0,
  "results": [
    {
      "test_id": "SCF-001-positive-001",
      "test_name": "Valid broker enrollment with code",
      "expected_result": "PASS",
      "actual_result": "PASS",
      "passed": true,
      "violations": [],
      "timestamp": "2024-03-27T14:45:00Z"
    },
    {
      "test_id": "SCF-001-negative-001",
      "test_name": "Broker without enrollment letter",
      "expected_result": "FAIL",
      "actual_result": "FAIL",
      "passed": true,
      "violations": ["Missing enrollment letter"],
      "timestamp": "2024-03-27T14:45:01Z"
    }
  ],
  "success_rate": 100.0
}
```

---

### 10. Get Audit Log

**GET** `{{base_url}}/api/{{api_version}}/audit-log?control_id={{control_id}}&limit=20`

**Query Parameters**:
| Name | Value |
|------|-------|
| control_id | SCF-001 |
| start_date | 2024-03-01T00:00:00Z (optional) |
| end_date | 2024-03-31T23:59:59Z (optional) |
| limit | 20 |

**Response (200 OK)**:
```json
{
  "total_entries": 5,
  "entries": [
    {
      "event_id": "EVT-20240327143012-000001",
      "timestamp": "2024-03-27T14:30:12Z",
      "event_type": "control_created",
      "control_id": "SCF-001",
      "actor": "pdf_generation",
      "reason": "Generated from regulation.pdf",
      "details": {"version": "1.0", "status": "draft"}
    },
    {
      "event_id": "EVT-20240327144500-000002",
      "timestamp": "2024-03-27T14:45:00Z",
      "event_type": "control_updated",
      "control_id": "SCF-001",
      "actor": "test_user@org.com",
      "reason": "Clarified enrollment procedure",
      "details": {"new_version": "1.1", "changes": {"title": "Enhanced..."}}
    }
  ]
}
```

---

### 11. Get Compliance Report

**GET** `{{base_url}}/api/{{api_version}}/compliance/by-domain`

**Response (200 OK)**:
```json
[
  {
    "domain": "Access Control",
    "total_controls": 12,
    "active_controls": 11,
    "compliant_controls": 11,
    "non_compliant_controls": 1,
    "compliance_percentage": 91.67
  },
  {
    "domain": "Data Governance",
    "total_controls": 8,
    "active_controls": 8,
    "compliant_controls": 8,
    "non_compliant_controls": 0,
    "compliance_percentage": 100.0
  }
]
```

---

## Testing Workflow

### Test Scenario 1: Extract and Activate Control

1. **Generate Controls** (POST generate endpoint with PDF)
2. **Note** the first `control_id` (e.g., SCF-001)
3. **Get Control** (GET with {{control_id}}, version=active)
   - Should return control in "draft" status
4. **Activate Control** (POST activate endpoint)
   - Should change status to "active"
5. **Validate Policy** (POST validate with test context)
   - Should return "PASS"

### Test Scenario 2: Version Control

1. **Create Control** (POST create endpoint)
2. **Update Control** (PATCH endpoint)
   - Should create v1.1
3. **Get History** (GET history endpoint)
   - Should show both v1.0 and v1.1
4. **Get Active** (GET with version="active")
   - Should return v1.0 (still active)
5. **Activate v1.1** (POST activate endpoint)
   - Should make v1.1 active, v1.0 deprecated

### Test Scenario 3: Policy Compliance

1. **Run Tests** (POST run-tests endpoint)
   - Should pass both positive and negative tests
2. **Validate Positive** (POST validate with valid context)
   - Should return "PASS"
3. **Validate Negative** (POST validate with invalid context)
   - Should return "FAIL"

---

## Collection JSON Template

```json
{
  "info": {
    "name": "SCF Platform API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Generate Controls",
      "request": {
        "method": "POST",
        "url": {
          "raw": "{{base_url}}/api/{{api_version}}/controls/generate",
          "host": ["{{base_url}}"],
          "path": ["api", "{{api_version}}", "controls", "generate"]
        },
        "body": {
          "mode": "formdata",
          "formdata": [{"key": "file", "type": "file"}]
        }
      }
    }
  ]
}
```

---

## Export Results

### Export as JSON

In Postman, click **Export** on any response:
```json
{
  "info": {...},
  "exec": [...]
}
```

### Create Test Summary Report

Use Postman Monitor or Newman CLI:
```bash
npm install -g newman
newman run scf-platform-collection.json -e scf-environment.json -r json
```

---

## Tips & Tricks

1. **Use Variables**: Define {{control_id}} once, reuse everywhere
2. **Skip SSL**: If using localhost, disable SSL verification
3. **Pretty Print**: Response → Click "Pretty" for formatted JSON
4. **Use Snippets**: Code → Select language for sample requests
5. **Save Requests**: Click Save button to store custom requests

---

*Generated for SCF Platform v2.0.0*
*Last Updated: 2024-03-27*
