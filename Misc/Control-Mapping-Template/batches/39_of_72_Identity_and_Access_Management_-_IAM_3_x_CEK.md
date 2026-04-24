# Batch: [39/72] Identity & Access Management - IAM (part 3) × Family: CEK
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-17, IAM-SaaS-18, IAM-SaaS-19, IAM-SaaS-20, IAM-SaaS-21
# Count: 5
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

### IAM-SaaS-17
**Title**: Temporary Account Suspension
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support programmatic suspension and reactivation of accounts without requiring their deletion.

When account suspension is invoked, the SaaS platform must suspend or revoke active sessions.

### IAM-SaaS-18
**Title**: Scopes requirements
**Domain**: Identity & Access Management - IAM
**Description**: If the SaaS platform supports a scoped protocol such as OAuth, then granular scopes must be created that allow for least privilege operations.

Read and write scopes are separated.
SaaS administrative actions, such as managing data, must be scoped separately.

### IAM-SaaS-19
**Title**: Third Party Allowlisting
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must provide administrative controls to allow which third-party integrations can connect by users.

### IAM-SaaS-20
**Title**: Inactive Session Timeout
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support the configuration of inactive UI session timeout settings.

The inactive session timeout must allow SaaS platform administrators to set the inactive UI session timeout within the UI of the SaaS platform or the security configuration API.

### IAM-SaaS-21
**Title**: Restricting User Invites
**Domain**: Identity & Access Management - IAM
**Description**: If users can be provisioned or invited by users other than administrators, the SaaS platform must support restricting this capability to specific roles.


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

**Save the output as:** `results/39_of_72_Identity_and_Access_Management_-_IAM_3_x_CEK_result.json`
