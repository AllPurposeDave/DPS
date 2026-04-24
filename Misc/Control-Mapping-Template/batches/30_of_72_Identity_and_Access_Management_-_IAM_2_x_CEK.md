# Batch: [30/72] Identity & Access Management - IAM (part 2) × Family: CEK
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-09, IAM-SaaS-10, IAM-SaaS-11, IAM-SaaS-12, IAM-SaaS-13, IAM-SaaS-14, IAM-SaaS-15, IAM-SaaS-16
# Count: 8
# Target scope: Family: CEK

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Family: CEK — 21 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Family: CEK (21 controls)

### Cryptography, Encryption & Key Management
- **CEK-01** | Encryption and Key Management Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for Cryptography, Encryption and Key Management. Review
and update the policies and procedures at least annually, or upon significant changes.
- **CEK-02** | CEK Roles and Responsibilities | Define and implement cryptographic, encryption and key management
roles and responsibilities.
- **CEK-03** | Data Protection | Provide data protection at-rest, in-transit, and where applicable, in-use by
using cryptographic libraries certified to approved standards.
- **CEK-04** | Encryption Algorithm | Utilize encryption algorithms following industry standards for protecting data, based on 
the data classification and associated risks.
- **CEK-05** | Encryption Change Management | Establish a standard change management procedure, to accommodate
changes from internal and external sources, for review, approval, implementation
and communication of cryptographic, encryption and key management technology
changes.
- **CEK-06** | Encryption Change Cost Benefit Analysis | Manage and adopt changes to cryptography-, encryption-, and key management-related
systems (including policies and procedures) that fully account for downstream
effects of proposed changes, including residual risk, cost, and benefits analysis.
- **CEK-07** | Encryption Risk Management | Establish and maintain an encryption and key management risk program
that includes provisions for risk assessment, risk treatment, risk context,
monitoring, and feedback.
- **CEK-08** | Service Customer Key Management Capability | Service providers must provide the capability for service customers 
to manage their own data encryption keys.
- **CEK-09** | Encryption and Key Management Audit | Audit encryption and key management systems, policies, and processes
with a frequency that is proportional to the risk exposure of the system with
audit occurring preferably continuously but at least annually and upon any
security event(s).
- **CEK-10** | Key Generation | Generate Cryptographic keys using industry accepted cryptographic
libraries specifying the algorithm strength and the random number generator
used.
- **CEK-11** | Key Purpose | Manage cryptographic secret and private keys that are provisioned
for a unique purpose.
- **CEK-12** | Key Rotation | Rotate cryptographic keys in accordance with the calculated cryptoperiod,
which includes provisions for considering the risk of information disclosure
and legal and regulatory requirements.
- **CEK-13** | Key Revocation | Define, implement and evaluate processes, procedures and technical
measures to revoke and remove cryptographic keys prior to the end of its established
cryptoperiod, when a key is compromised, or an entity is no longer part of the
organization, which include provisions for legal and regulatory requirements.
- **CEK-14** | Key Destruction | Define, implement, and evaluate processes, procedures, and technical measures to securely destroy cryptographic keys 
when they are no longer needed, which include provisions for legal and regulatory requirements.
- **CEK-15** | Key Activation | Define, implement and evaluate processes, procedures and technical
measures to create keys in a pre-activated state when they have been generated
but not authorized for use, which include provisions for legal and regulatory
requirements.
- **CEK-16** | Key Suspension | Define, implement and evaluate processes, procedures and technical
measures to monitor, review and approve key transitions from any state to/from
suspension, which include provisions for legal and regulatory requirements.
- **CEK-17** | Key Deactivation | Define, implement and evaluate processes, procedures and technical
measures to deactivate keys at the time of their expiration date, which include
provisions for legal and regulatory requirements.
- **CEK-18** | Key Archival | Define, implement and evaluate processes, procedures and technical
measures to manage archived keys in a secure repository requiring least privilege
access, which include provisions for legal and regulatory requirements.
- **CEK-19** | Key Compromise | Define, implement and evaluate processes, procedures and technical
measures to use compromised keys to encrypt information only in controlled circumstance,
and thereafter exclusively for decrypting data and never for encrypting data,
which include provisions for legal and regulatory requirements.
- **CEK-20** | Key Recovery | Define, implement and evaluate processes, procedures and technical
measures to assess the risk to operational continuity versus the risk of the
keying material and the information it protects being exposed if control of
the keying material is lost, which include provisions for legal and regulatory
requirements.
- **CEK-21** | Key Inventory Management | Define, implement and evaluate processes, procedures and technical
measures in order for the key management system to track and report all cryptographic
materials and changes in status, which include provisions for legal and regulatory
requirements.


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

**Save the output as:** `results/30_of_72_Identity_and_Access_Management_-_IAM_2_x_CEK_result.json`
