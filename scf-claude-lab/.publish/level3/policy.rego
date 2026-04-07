# ============================================================================
# SCF - Secure Control Framework
# Consolidated Policies
# Generated: 2026-04-06T08:49:59.276467
# ============================================================================

package scf

import future.keywords

# ============================================================================
# CONTROL DEFINITIONS
# ============================================================================


# SCF-001: Procedure For Enrollment / Registration Of Brokers

SCF-001_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-001_is_authorized
}

SCF-001_deny if {
    not SCF-001_allow
}

SCF-001_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-001_decision := {
    "control_id": "SCF-001",
    "title": "Procedure For Enrollment / Registration Of Brokers",
    "type": "Preventive",
    "domain": "Access Control",
    "decision": SCF-001_allow ? "ALLOW" : "DENY",
    "result": SCF-001_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-001_allow ? 100 : 0,
}

# SCF-002: The Broker Seeking Enrolment/Registration May Submit The

SCF-002_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-002_is_authorized
}

SCF-002_deny if {
    not SCF-002_allow
}

SCF-002_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-002_decision := {
    "control_id": "SCF-002",
    "title": "The Broker Seeking Enrolment/Registration May Submit The",
    "type": "Preventive",
    "domain": "Access Control",
    "decision": SCF-002_allow ? "ALLOW" : "DENY",
    "result": SCF-002_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-002_allow ? 100 : 0,
}

# SCF-003: The Receiving Office Should Allot A Code

SCF-003_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-003_is_authorized
}

SCF-003_deny if {
    not SCF-003_allow
}

SCF-003_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-003_decision := {
    "control_id": "SCF-003",
    "title": "The Receiving Office Should Allot A Code",
    "type": "Preventive",
    "domain": "Access Control",
    "decision": SCF-003_allow ? "ALLOW" : "DENY",
    "result": SCF-003_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-003_allow ? 100 : 0,
}

# SCF-004: That In Cases Where Receiving Offices Engage

SCF-004_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-004_is_authorized
}

SCF-004_deny if {
    not SCF-004_allow
}

SCF-004_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-004_decision := {
    "control_id": "SCF-004",
    "title": "That In Cases Where Receiving Offices Engage",
    "type": "Preventive",
    "domain": "Access Control",
    "decision": SCF-004_allow ? "ALLOW" : "DENY",
    "result": SCF-004_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-004_allow ? 100 : 0,
}

# SCF-005: No Tds On Payment Of Brokerage No

SCF-005_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-005_is_authorized
}

SCF-005_deny if {
    not SCF-005_allow
}

SCF-005_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-005_decision := {
    "control_id": "SCF-005",
    "title": "No Tds On Payment Of Brokerage No",
    "type": "Preventive",
    "domain": "Access Control",
    "decision": SCF-005_allow ? "ALLOW" : "DENY",
    "result": SCF-005_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-005_allow ? 100 : 0,
}

# SCF-006: Receiving Offices Are To Settle The Brokerage

SCF-006_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-006_is_authorized
}

SCF-006_deny if {
    not SCF-006_allow
}

SCF-006_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-006_decision := {
    "control_id": "SCF-006",
    "title": "Receiving Offices Are To Settle The Brokerage",
    "type": "Corrective",
    "domain": "Access Control",
    "decision": SCF-006_allow ? "ALLOW" : "DENY",
    "result": SCF-006_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-006_allow ? 100 : 0,
}

# SCF-007: Receiving Offices Are Advised To First Settle

SCF-007_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-007_is_authorized
}

SCF-007_deny if {
    not SCF-007_allow
}

SCF-007_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-007_decision := {
    "control_id": "SCF-007",
    "title": "Receiving Offices Are Advised To First Settle",
    "type": "Corrective",
    "domain": "Access Control",
    "decision": SCF-007_allow ? "ALLOW" : "DENY",
    "result": SCF-007_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-007_allow ? 100 : 0,
}

# SCF-008: Improvement In Customer Service

SCF-008_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-008_is_authorized
}

SCF-008_deny if {
    not SCF-008_allow
}

SCF-008_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-008_decision := {
    "control_id": "SCF-008",
    "title": "Improvement In Customer Service",
    "type": "Preventive",
    "domain": "Access Control",
    "decision": SCF-008_allow ? "ALLOW" : "DENY",
    "result": SCF-008_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-008_allow ? 100 : 0,
}

# SCF-009: A Sole Holder Or All The Joint

SCF-009_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-009_is_authorized
}

SCF-009_deny if {
    not SCF-009_allow
}

SCF-009_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-009_decision := {
    "control_id": "SCF-009",
    "title": "A Sole Holder Or All The Joint",
    "type": "Preventive",
    "domain": "Data Governance",
    "decision": SCF-009_allow ? "ALLOW" : "DENY",
    "result": SCF-009_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-009_allow ? 100 : 0,
}

# SCF-010: The Nomination Should Be Made Before Maturity

SCF-010_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-010_is_authorized
}

SCF-010_deny if {
    not SCF-010_allow
}

SCF-010_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-010_decision := {
    "control_id": "SCF-010",
    "title": "The Nomination Should Be Made Before Maturity",
    "type": "Preventive",
    "domain": "Data Governance",
    "decision": SCF-010_allow ? "ALLOW" : "DENY",
    "result": SCF-010_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-010_allow ? 100 : 0,
}

# SCF-011: When Nomination Has Been Made In Favour

SCF-011_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-011_is_authorized
}

SCF-011_deny if {
    not SCF-011_allow
}

SCF-011_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-011_decision := {
    "control_id": "SCF-011",
    "title": "When Nomination Has Been Made In Favour",
    "type": "Preventive",
    "domain": "Data Governance",
    "decision": SCF-011_allow ? "ALLOW" : "DENY",
    "result": SCF-011_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-011_allow ? 100 : 0,
}

# SCF-012: A Nomination Made By The Holder(S Of

SCF-012_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-012_is_authorized
}

SCF-012_deny if {
    not SCF-012_allow
}

SCF-012_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-012_decision := {
    "control_id": "SCF-012",
    "title": "A Nomination Made By The Holder(S Of",
    "type": "Corrective",
    "domain": "Access Control",
    "decision": SCF-012_allow ? "ALLOW" : "DENY",
    "result": SCF-012_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-012_allow ? 100 : 0,
}

# SCF-013: Nomination Will Also Stand Cancelled If The

SCF-013_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-013_is_authorized
}

SCF-013_deny if {
    not SCF-013_allow
}

SCF-013_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-013_decision := {
    "control_id": "SCF-013",
    "title": "Nomination Will Also Stand Cancelled If The",
    "type": "Corrective",
    "domain": "Data Governance",
    "decision": SCF-013_allow ? "ALLOW" : "DENY",
    "result": SCF-013_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-013_allow ? 100 : 0,
}

# SCF-014: If The Nominee Is A Minor

SCF-014_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-014_is_authorized
}

SCF-014_deny if {
    not SCF-014_allow
}

SCF-014_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-014_decision := {
    "control_id": "SCF-014",
    "title": "If The Nominee Is A Minor",
    "type": "Preventive",
    "domain": "Data Governance",
    "decision": SCF-014_allow ? "ALLOW" : "DENY",
    "result": SCF-014_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-014_allow ? 100 : 0,
}

# SCF-015: Receiving Offices To Issue â€˜Acknowledgement Of Nomination.'

SCF-015_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-015_is_authorized
}

SCF-015_deny if {
    not SCF-015_allow
}

SCF-015_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-015_decision := {
    "control_id": "SCF-015",
    "title": "Receiving Offices To Issue â€˜Acknowledgement Of Nomination.'",
    "type": "Preventive",
    "domain": "Access Control",
    "decision": SCF-015_allow ? "ALLOW" : "DENY",
    "result": SCF-015_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-015_allow ? 100 : 0,
}

# SCF-016: 8 % Savings Taxable Bonds

SCF-016_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-016_is_authorized
}

SCF-016_deny if {
    not SCF-016_allow
}

SCF-016_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-016_decision := {
    "control_id": "SCF-016",
    "title": "8 % Savings Taxable Bonds",
    "type": "Preventive",
    "domain": "Data Governance",
    "decision": SCF-016_allow ? "ALLOW" : "DENY",
    "result": SCF-016_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-016_allow ? 100 : 0,
}

# SCF-017: In Case Detailed Clarifications Are Required On

SCF-017_allow if {
    input.context != null
    input.context.actor_type != null
    SCF-017_is_authorized
}

SCF-017_deny if {
    not SCF-017_allow
}

SCF-017_is_authorized if {
    input.context.metadata.authorized == true
}

SCF-017_decision := {
    "control_id": "SCF-017",
    "title": "In Case Detailed Clarifications Are Required On",
    "type": "Preventive",
    "domain": "Governance and Compliance",
    "decision": SCF-017_allow ? "ALLOW" : "DENY",
    "result": SCF-017_allow ? "PASS" : "FAIL",
    "compliance_score": SCF-017_allow ? 100 : 0,
}