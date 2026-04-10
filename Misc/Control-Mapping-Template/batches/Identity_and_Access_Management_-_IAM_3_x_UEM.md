# Batch: Identity & Access Management - IAM (part 3) × Family: UEM
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-17, IAM-SaaS-18, IAM-SaaS-19, IAM-SaaS-20, IAM-SaaS-21
# Count: 5
# Target scope: Family: UEM

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls
address the same security requirement or capability. A "match" means the CCM
control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Family: UEM — 14 controls. Other target families are covered in separate batches.

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

---

## SSCF Controls to Map

### IAM-SaaS-17
**Title**: Temporary Account Suspension
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support programmatic suspension and reactivation of accounts without requiring their deletion.

When account suspension is invoked, the SaaS platform must suspend or revoke active sessions.
**Details**: Privileges must be immediately enforced upon entitlement changes

Where not possible, forced re-authentication is allowed
**Guidelines**: Associated Non-Human Identities (NHIs) should be suspended when account suspension is triggered. 

The SaaS platform should allow for the suspension and reactivation of accounts, including any associated Non-Human Identities (NHIs). Upon reactivation, all NHIs linked to the account should be restored without any of them being revoked.

### IAM-SaaS-18
**Title**: Scopes requirements
**Domain**: Identity & Access Management - IAM
**Description**: If the SaaS platform supports a scoped protocol such as OAuth, then granular scopes must be created that allow for least privilege operations.

Read and write scopes are separated.
SaaS administrative actions, such as managing data, must be scoped separately.
**Details**: (Intentionally Left Blank)
**Guidelines**: While read and write scopes should be provided separately, the application may provide scopes such as manage or administrative, which combine lower-level scopes.

### IAM-SaaS-19
**Title**: Third Party Allowlisting
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must provide administrative controls to allow which third-party integrations can connect by users.
**Details**: When this control is invoked , the application must suspend or revoke existing sessions
**Guidelines**: If the SaaS platform does not have the ability to manage an allow list, it should allow SaaS platform administrators to block the installation of third-party applications globally by regular users.

### IAM-SaaS-20
**Title**: Inactive Session Timeout
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support the configuration of inactive UI session timeout settings.

The inactive session timeout must allow SaaS platform administrators to set the inactive UI session timeout within the UI of the SaaS platform or the security configuration API.
**Guidelines**: The SaaS platform should have a default inactive session timeout in minutes or hours, not weeks.

### IAM-SaaS-21
**Title**: Restricting User Invites
**Domain**: Identity & Access Management - IAM
**Description**: If users can be provisioned or invited by users other than administrators, the SaaS platform must support restricting this capability to specific roles.
**Details**: Read and write scopes are separated
Administrative actions such as managing data must be scoped separately
**Guidelines**: The SaaS platform should support the invitation of collaboration users. If such functionality is available, the SaaS platform administrators can restrict by role those users authorized to issue invitations.


---

## CCM Controls Reference — Family: UEM (14 controls)

### Universal Endpoint Management
- **UEM-01** | Endpoint Devices Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for all endpoints. Review and update the policies and
procedures at least annually, or upon significant changes.
- **UEM-02** | Application and Service Approval | Define, document, apply and evaluate a list of approved services,
applications and sources of applications (stores) acceptable for use by endpoints
when accessing or storing organization-managed data.
- **UEM-03** | Compatibility | Define and implement a process for the validation of the endpoint
device's compatibility with operating systems and applications.
- **UEM-04** | Endpoint Inventory | Maintain an inventory of all endpoints used to store, access and process company
data.
- **UEM-05** | Endpoint Management | Define, implement and evaluate processes, procedures and technical
measures to enforce policies and controls for all endpoints permitted to access
systems and/or store, transmit, or process organizational data.
- **UEM-06** | Automatic Lock Screen | Configure all relevant interactive-use endpoints to require an automatic
lock screen.
- **UEM-07** | Operating Systems | Manage changes to endpoint operating systems, patch levels, and/or
applications through the company's change management processes.
- **UEM-08** | Storage Encryption | Protect information from unauthorized disclosure on managed endpoint
devices with storage encryption.
- **UEM-09** | Anti-Malware Detection and Prevention | Configure managed endpoints with anti-malware detection and prevention
technology and services.
- **UEM-10** | Software Firewall | Configure managed endpoints with properly configured software firewalls.
- **UEM-11** | Data Loss Prevention | Configure managed endpoints with Data Loss Prevention (DLP) technologies
and rules in accordance with a risk assessment.
- **UEM-12** | Remote Locate | Enable remote geo-location capabilities for all managed mobile endpoints, according 
to all applicable laws and regulations.
- **UEM-13** | Remote Wipe | Define, implement and evaluate processes, procedures and technical
measures to enable the deletion of company data remotely on managed endpoint
devices.
- **UEM-14** | Third-Party Endpoint Security Posture | Define, implement and evaluate processes, procedures and technical
and/or contractual measures to maintain proper security of third-party endpoints
with access to organizational assets.


---

## Required Output Format

Respond with ONLY valid JSON (no markdown code fences, no extra text).
The JSON object has one key per source control ID:

```
{
  "IAM-SaaS-17": {
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

**Save the output as:** `results/Identity_and_Access_Management_-_IAM_3_x_UEM_result.json`
