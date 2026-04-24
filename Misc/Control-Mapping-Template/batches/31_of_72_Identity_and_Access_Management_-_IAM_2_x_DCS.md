# Batch: [31/72] Identity & Access Management - IAM (part 2) × Family: DCS
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-09, IAM-SaaS-10, IAM-SaaS-11, IAM-SaaS-12, IAM-SaaS-13, IAM-SaaS-14, IAM-SaaS-15, IAM-SaaS-16
# Count: 8
# Target scope: Family: DCS

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Family: DCS — 18 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Family: DCS (18 controls)

### Datacenter Security
- **DCS-01** | Physical and Environmental Security Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain 
policies and procedures for physical and environmental security. Review and 
update the policies and procedures at least annually, or upon significant changes.
- **DCS-02** | Off-Site Equipment Disposal Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the secure disposal of equipment used outside the
organization's premises. If the equipment is not physically destroyed a data
destruction procedure that renders recovery of information impossible must be
applied. Review and update the policies and procedures at least annually, or upon significant changes.
- **DCS-03** | Off-Site Transfer Authorization Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the relocation or transfer of hardware, software,
or data/information to an offsite or alternate location. The relocation or transfer
request requires the written or cryptographically verifiable authorization.
Review and update the policies and procedures at least annually, or upon significant changes.
- **DCS-04** | Secure Area Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for maintaining a safe and secure working environment
in offices, rooms, and facilities. Review and update the policies and procedures
at least annually, or upon significant changes.
- **DCS-05** | Secure Media Transportation Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the secure transportation of physical media. Review
and update the policies and procedures at least annually, or upon significant changes.
- **DCS-06** | Assets Classification | Classify and document the physical, and logical assets (e.g., applications)
based on the organizational business risk. Review and update the assets’ classification 
at least annually, or upon significant changes.
- **DCS-07** | Assets Cataloguing and Tracking | Catalogue and track all relevant physical and logical assets located at all of the service provider's sites 
within a secured system. Review and update the catalogue at least annually or upon significant changes.
- **DCS-08** | Controlled Physical Access Points | Design and implement physical security perimeters to safeguard personnel, data,
and information systems.
- **DCS-09** | Equipment Identification | Use equipment identification as a method for connection authentication.
- **DCS-10** | Secure Area Authorization | Allow only authorized personnel access to secure areas, with all
ingress and egress points restricted, documented, and monitored by physical
access control mechanisms. Retain access control records on a periodic basis
as deemed appropriate by the organization.
- **DCS-11** | Surveillance System | Implement, maintain, and operate datacenter surveillance systems
at the external perimeter and at all the ingress and egress points to detect
unauthorized ingress and egress attempts.
- **DCS-12** | Adverse Event Response Training | Train datacenter personnel to safely manage adverse events, including but not limited 
to unauthorized ingress and egress attempts.
- **DCS-13** | Cabling Security | Define, implement and evaluate processes, procedures and technical
measures that ensure a risk-based protection of power and telecommunication
cables from a threat of interception, interference or damage at all facilities,
offices and rooms.
- **DCS-14** | Environmental Systems | Implement and maintain data center environmental control systems
that monitor, maintain and test for continual effectiveness the temperature
and humidity conditions within accepted industry standards.
- **DCS-15** | Secure Utilities | Secure, monitor, maintain, and test utilities services for continual
effectiveness at planned intervals.
- **DCS-16** | Equipment Location | Keep business-critical equipment away from locations subject to high
probability for environmental risk events.
- **DCS-17** | Datacenter Metrics | Establish, monitor and report datacenter security metrics to secure data center assets and services.
- **DCS-18** | Datacenter Operations Resilience | Define, implement and evaluate processes, procedures and technical measures to ensure continuous operations.


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

**Save the output as:** `results/31_of_72_Identity_and_Access_Management_-_IAM_2_x_DCS_result.json`
