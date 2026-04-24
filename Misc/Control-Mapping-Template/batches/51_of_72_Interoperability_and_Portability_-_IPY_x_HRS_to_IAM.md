# Batch: [51/72] Interoperability & Portability - IPY × Families: HRS, IAM
# Source: SSCF -> Target: CCM
# Controls in this batch: IPY-SaaS-01, IPY-SaaS-02
# Count: 2
# Target scope: Families: HRS, IAM

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: HRS, IAM — 28 controls. Other target families are covered in separate batches.

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

### IPY-SaaS-01
**Title**: Export Capability
**Domain**: Interoperability & Portability - IPY
**Description**: If the SaaS platform offers mass data export functionality, it must allow SaaS administrators to disable this functionality for non-administrative users.

### IPY-SaaS-02
**Title**: Integration Attribution
**Domain**: Interoperability & Portability - IPY
**Description**: The SaaS platform must implement a mechanism to allow or deny connections based on the verified creator of the integration. 

When SaaS platform users are prompted to accept integrations (e.g., via a consent screen), the acceptance process must display at least one verifiable attribute of the application's creator, such as their email address domain. This verifiable ownership attribute must be visible both during the acceptance process and in the list of connected integrations, as stipulated in IAM-SaaS-06.

Verification of the integration creator must be performed by the SaaS platform using an application-appropriate mechanism.


---

## CCM Controls Reference — Families: HRS, IAM (28 controls)

### Human Resources
- **HRS-01** | Background Screening Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for background verification of all new employees (including
but not limited to remote employees, contractors, and third parties) according
to local laws, regulations, ethics, and contractual constraints and proportional
to the data classification to be accessed, the business requirements, and acceptable
risk. Review and update the policies and procedures at least annually, or upon significant changes.
- **HRS-02** | Acceptable Use of Technology Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for defining allowances and conditions for the acceptable
use of organizationally-owned or managed assets. Review and update the policies
and procedures at least annually, or upon significant changes.
- **HRS-03** | Clean Desk Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures that require unattended workspaces to not have openly
visible confidential data. Review and update the policies and procedures at
least annually, or upon significant changes.
- **HRS-04** | Remote and Home Working Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures to protect information accessed, processed or stored
at remote sites and locations. Review and update the policies and procedures
at least annually, or upon significant changes.
- **HRS-05** | Asset returns | Establish and document procedures for the return of organization-owned
assets by terminated employees, contractors and third parties.
- **HRS-06** | Employment Termination | Establish, document, and communicate to all relevant personnel the procedures
outlining the roles and responsibilities concerning changes in employment.
- **HRS-07** | Employment Agreement Process | Employees sign the employee agreement prior to being granted access
to organizational information systems, resources and assets.
- **HRS-08** | Employment Agreement Content | The organization includes within the employment agreements provisions
and/or terms for adherence to established information governance and security
policies.
- **HRS-09** | Personnel Roles and Responsibilities | Establish, document and communicate roles and responsibilities of employees, 
as they relate to information assets' security and privacy.
- **HRS-10** | Non-Disclosure Agreements | Identify, document, and review, at planned intervals, requirements
for non-disclosure/confidentiality agreements reflecting the organization's
needs for the protection of data and operational details.
- **HRS-11** | Security Awareness Training | Establish, document, approve, communicate, apply, evaluate and maintain
a security awareness training program for all employees of the organization
and provide regular training updates.
- **HRS-12** | Personal and Sensitive Data Awareness and Training | Provide employees with access to sensitive organizational and
personal data with appropriate security awareness training and regular updates
in organizational procedures, processes, and policies relating to their professional
function relative to the organization.
- **HRS-13** | Compliance User Responsibility | Make employees aware of their roles and responsibilities for maintaining
awareness and compliance with established policies and procedures and applicable
legal, statutory, or regulatory compliance obligations.

### Identity & Access Management
- **IAM-01** | Identity and Access Management Policy and Procedures | Establish, document, approve, communicate, implement, apply, evaluate, and 
maintain policies and procedures for identity and access management. Review
and update the policies and procedures at least annually, or upon significant changes.
- **IAM-02** | Credentials Management Policy and Procedures | Establish, document, approve, communicate, implement, apply, evaluate, and 
maintain policies and procedures for the management of authentication credentials, 
including passwords. Review and update the policies and procedures at least annually, 
or upon significant changes.
- **IAM-03** | Identity Inventory | Manage, store, and regularly review the inventory of identities, and monitor 
their level of access.
- **IAM-04** | Separation of Duties | Employ the separation of duties principle when implementing information
system access.
- **IAM-05** | Least Privilege | Employ the least privilege principle when implementing information
system access.
- **IAM-06** | Access Provisioning | Define and implement an identity access provisioning process which authorizes,
records, and communicates access changes to data and assets.
- **IAM-07** | Access Changes and Revocation | De-provision or modify identity access in a timely manner.
- **IAM-08** | Access Review | Review and revalidate identity access for least privilege and separation of duties with a 
frequency that is commensurate with organizational risk tolerance, and at least annually 
or upon significant changes.
- **IAM-09** | Segregation of Privileged Access Roles | Define, implement and evaluate processes, procedures and technical
measures for the segregation of privileged access roles.
- **IAM-10** | Management of Privileged Access Roles | Define and implement an access process to ensure privileged access
roles and rights are granted for a time limited period, and implement procedures
to prevent the accumulation of segregated privileged access.
- **IAM-11** | Service Customers Approval for Agreed Privileged Access Roles | Define, implement and evaluate processes and procedures for service customers
to participate, where applicable, in the granting of access for agreed, high
risk (as defined by the organizational risk assessment) privileged access roles.
- **IAM-12** | Unique Identities | Define, implement and evaluate processes, procedures and technical measures that 
ensure identities’ activities are identifiable through uniquely associated IDs.
- **IAM-13** | Strong Authentication | Define, implement and evaluate processes, procedures and technical
measures for authenticating access to systems, application and data assets,
including multifactor authentication for at least privileged user and sensitive
data access. Adopt digital certificates or alternatives which achieve an equivalent
level of security for system identities.
- **IAM-14** | Credentials Management | Define, implement and evaluate processes, procedures and technical measures for the 
secure management of authentication credentials, including passwords.
- **IAM-15** | Authorization Mechanisms | Define, implement and evaluate processes, procedures and technical
measures to verify access to data and system functions is authorized.


---

## Required Output Format

Respond with ONLY valid JSON (no markdown code fences, no extra text).
The JSON object has one key per source control ID:

```
{
  "IPY-SaaS-01": {
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

**Save the output as:** `results/51_of_72_Interoperability_and_Portability_-_IPY_x_HRS_to_IAM_result.json`
