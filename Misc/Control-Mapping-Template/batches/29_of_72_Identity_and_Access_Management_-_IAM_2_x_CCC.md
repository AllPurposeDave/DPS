# Batch: [29/72] Identity & Access Management - IAM (part 2) × Family: CCC
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-09, IAM-SaaS-10, IAM-SaaS-11, IAM-SaaS-12, IAM-SaaS-13, IAM-SaaS-14, IAM-SaaS-15, IAM-SaaS-16
# Count: 8
# Target scope: Family: CCC

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Family: CCC — 9 controls. Other target families are covered in separate batches.

### Confidence Levels — be precise
- **high**: The CCM control **directly and specifically requires** the same capability. The rationale must NOT use words like "partially," "broadly," "related to," or "touches on." If you need those words, it is medium, not high.
- **medium**: Partial overlap — the CCM control covers some but not all of the SSCF requirement, or addresses it at a broader scope.
- **low**: Tangential relationship only — shared vocabulary or domain but different actual requirements.

### Common Pitfalls to Avoid
- **Keyword matching is not semantic matching.** The word "access" in a physical-security control does NOT match a logical-access control. "Audit" in a financial-audit context does NOT match security-audit logging. Read both controls fully before deciding.
- **Umbrella controls are not automatic matches.** A CCM control like "maintain a security program" is too broad to be a high match for a specific technical requirement. Mark it medium or low.

### Rules
- Include ALL relevant matches, even low confidence ones
- Set `unique_to_source` to `true` ONLY if there are NO high or medium matches **in this target group**
- Provide a one-sentence rationale for each match explaining the **specific** overlap
- If no matches exist in this target group, return an empty matches array

### Output Format
Respond with ONLY valid JSON (no markdown code fences, no extra text). The JSON object has one key per source control ID, with a `matches` array, `unique_to_source` boolean, and `gap_rationale` string. See each batch file for the exact example and save path.

---

## SSCF Controls to Map

### IAM-SaaS-09
**Title**: User provisioning and deprovisioning
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support automated user provisioning and deprovisioning.

The SaaS platform must have a mechanism to limit the programmatic access of user provisioning and deprovisioning operations.

### IAM-SaaS-10
**Title**: Security Auditing Role
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must provide a Security Auditing role for read-only access to all security settings, including log access in UI and via programmatic means.

The Security Auditing role must allow visibility into security configurations and logging data.  

It must not enable viewing or modifying customer data or making changes to any configurations.

### IAM-SaaS-11
**Title**: Password Rules
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must define password strength requirements or configuration controls to comply with NIST guidelines.

If implemented through configuration controls, the following must be configurable:
1. Set Password length
2. Password reuse
3. Toggle Special Characters required
4. Password expiry

### IAM-SaaS-12
**Title**: Multi-Factor Authentication
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support the use of multi-factor authentication.

The SaaS platform must allow SaaS platform administrators to toggle on and off each factor.

The SaaS platform must have the capability to configure MFA enforcement (The user may not sign in without MFA).

### IAM-SaaS-13
**Title**: Disabling Anonymous Access
**Domain**: Identity & Access Management - IAM
**Description**: If the SaaS platform supports anonymous access, it must provide a mechanism to disable it globally.

### IAM-SaaS-14
**Title**: Disabling External Access for Unmanaged Users
**Domain**: Identity & Access Management - IAM
**Description**: If the SaaS platform supports access for external unmanaged users, it must provide a mechanism to disable it globally.

### IAM-SaaS-15
**Title**: Session Revocation/ Single Sign Out
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support a process to invalidate a user’s sessions via programmatic means.

Invalidation of the user session must have the capability to revoke user and application sessions (all device and UI sessions) in real-time.

### IAM-SaaS-16
**Title**: Entitlements Change Enforcement
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support immediate enforcement of entitlement changes. 

Where not possible, forced re-authentication is allowed.


---

## CCM Controls Reference — Family: CCC (9 controls)

### Change Control and Configuration Management
- **CCC-01** | Change Management Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for managing the risks associated with applying changes
to assets owned, controlled or used by the organization. Review and update the policies and procedures at least annually, or upon significant changes.
- **CCC-02** | Quality Testing | Establish, maintain and implement a defined quality change control, approval and testing process
incorporating baselines, testing, and release standards.
- **CCC-03** | Change Management Technology | Implement a change management procedure to manage the risks associated with applying changes 
to assets, owned, controlled or used by the organization.
- **CCC-04** | Unauthorized Change Protection | Implement and enforce a procedure to authorize the addition, removal, update, and management 
of assets that are owned, controlled or used by the organization.
- **CCC-05** | Change Agreements | Include provisions limiting changes directly impacting service customers owned environments (tenants) 
to explicitly authorized requests within service level agreements.
- **CCC-06** | Change Management Baseline | Establish, document and implement change management and configuration baselines for all relevant 
authorized changes on organization assets. Review and update the baselines at least annually or upon significant changes.
- **CCC-07** | Detection of Baseline Deviation | Implement detection measures with proactive notification in case
of changes deviating from the established baseline.
- **CCC-08** | Exception Management | Implement a procedure for the management of exceptions, including
emergencies, in the change and configuration process. Align the procedure with
the requirements of GRC-04: Policy Exception Process.
- **CCC-09** | Change Restoration | Define and implement a process to proactively roll back changes to
a previous known good state in case of errors or security concerns.


---

## Required Output Format

Respond with ONLY valid JSON (no markdown code fences, no extra text).
The JSON object has one key per source control ID:

```
{
  "IAM-SaaS-09": {
    "matches": [
      {"target_id": "XXX-01", "confidence": "high", "rationale": "One sentence explanation."},
      {"target_id": "YYY-02", "confidence": "medium", "rationale": "One sentence explanation."}
    ],
    "unique_to_source": false,
    "gap_rationale": ""
  },
  ...
}
```

**Save the output as:** `results/29_of_72_Identity_and_Access_Management_-_IAM_2_x_CCC_result.json`
