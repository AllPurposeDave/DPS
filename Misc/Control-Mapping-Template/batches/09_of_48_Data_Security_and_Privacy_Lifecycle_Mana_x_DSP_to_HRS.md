# Batch: [9/48] Data Security and Privacy Lifecycle Management - DSP × Families: DSP, GRC, HRS
# Source: SSCF -> Target: CCM
# Controls in this batch: DSP-SaaS-01
# Count: 1
# Target scope: Families: DSP, GRC, HRS

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: DSP, GRC, HRS — 40 controls. Other target families are covered in separate batches.

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

### DSP-SaaS-01
**Title**: Blocking malicious file uploads
**Domain**: Data Security and Privacy Lifecycle Management - DSP
**Description**: If the SaaS platform allows unrestricted file attachments, it must provide administrative configuration that limits the acceptable file types using an allow list and must provide an option to disable any file uploads.
**Details**: (Intentionally Left Blank)

All security features provided must be documented with needed compute region (a map?)
**Guidelines**: Motivation: if the platform then exposes the ability to upload files externally (e.g., a support portal), this control is meant to disallow files that may contain malicious code (e.g., office documents)

We recommend that SaaS platforms consider adding file scanning capabilities.


---

## CCM Controls Reference — Families: DSP, GRC, HRS (40 controls)

### Data Security and Privacy Lifecycle Management
- **DSP-01** | Security and Privacy Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the preparation, classification, protection and handling of data
throughout its lifecycle, and according to all applicable laws and regulations,
standards, and risk level. Review and update the policies and procedures at
least annually, or upon significant changes.
- **DSP-02** | Secure Disposal | Apply industry accepted methods for the secure disposal of data from
storage media such that data is not recoverable by any forensic means.
- **DSP-03** | Data Inventory | Create and maintain a data inventory, at least for any sensitive, regulated and personal 
data. Review and update the inventory at least annually or upon significant changes.
- **DSP-04** | Data Classification | Classify data according to its type, criticality and sensitivity level.
- **DSP-05** | Data Flow Documentation | Create data flow documentation to identify what data is processed,
stored or transmitted where. Review data flow documentation at defined intervals,
at least annually, or upon significant changes.
- **DSP-06** | Data Ownership and Stewardship | Document ownership and stewardship of all relevant documented personal
and sensitive data. Perform review at least annually.
- **DSP-07** | Data Protection by Design and Default | Develop systems, products, and business practices based upon a principle
of security by design and industry best practices.
- **DSP-08** | Data Privacy by Design and Default | Develop systems, products, and business practices based upon a principle
of privacy by design and industry best practices. Ensure that systems' privacy
settings are configured by default, according to all applicable laws and regulations.
- **DSP-09** | Data Protection Impact Assessment | Conduct a Data Protection Impact Assessment (DPIA) to evaluate the
origin, nature, particularity and severity of the risks upon the processing
of personal data, according to any applicable laws, regulations and industry
best practices.
- **DSP-10** | Sensitive Data Transfer | Define, implement and evaluate processes, procedures and technical
measures that ensure any transfer of personal or sensitive data is protected
from unauthorized access and only processed within scope as permitted by the
respective laws and regulations.
- **DSP-11** | Personal Data Access, Reversal, Rectification and Deletion | Define and implement, processes, procedures and technical measures
to enable data subjects to request access to, modification, or deletion of their
personal data, according to any applicable laws and regulations.
- **DSP-12** | Limitation of Purpose in Personal Data Processing | Define, implement and evaluate processes, procedures and technical
measures to ensure that personal data is processed according to any applicable
laws and regulations and for the purposes declared to the data subject.
- **DSP-13** | Personal Data Sub-processing | Define, implement and evaluate processes, procedures and technical
measures for the transfer and sub-processing of personal data within the service
supply chain, according to any applicable laws and regulations.
- **DSP-14** | Disclosure of Data Sub-processors | Define, implement and evaluate processes, procedures and technical
measures to disclose the details of any personal or sensitive data access by
sub-processors to the data owner prior to initiation of that processing.
- **DSP-15** | Limitation of Production Data Use | Obtain authorization from data owners, and manage associated risk
before replicating or using production data in non-production environments.
- **DSP-16** | Data Retention and Deletion | Data retention, archiving and deletion is managed in accordance with
business requirements, applicable laws and regulations.
- **DSP-17** | Sensitive Data Protection | Define and implement, processes, procedures and technical measures
to protect sensitive data throughout it's lifecycle.
- **DSP-18** | Disclosure Notification | The service provider must implement and describe to service customers the procedure to manage and respond to requests 
for disclosure of Personal Data by Law Enforcement Authorities according to applicable laws and regulations
- **DSP-19** | Data Location | Define and implement, processes, procedures and technical measures
to specify and document the physical locations of data, including any locations
in which data is processed or backed up.

### Governance, Risk and Compliance
- **GRC-01** | Governance Program Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for an information governance program, which is sponsored
by the leadership of the organization. Review and update the policies and procedures
at least annually, or upon significant changes.
- **GRC-02** | Risk Management Program | Establish and maintain a formal, documented, and leadership-sponsored Enterprise 
Risk Management (ERM) program that includes policies and procedures for identification, 
evaluation, ownership, treatment, and acceptance of risks.
- **GRC-03** | Organizational Policy Reviews | Review all relevant organizational policies and associated procedures
at least annually or when a substantial change occurs within the organization.
- **GRC-04** | Policy Exception Process | Establish and follow an approved exception process as mandated by
the governance program whenever a deviation from an established policy occurs.
- **GRC-05** | Information Security Program | Develop and implement an Information Security Program, which includes
programs for all the relevant domains of the CCM.
- **GRC-06** | Governance Responsibility Model | Define and document roles and responsibilities for planning, implementing,
operating, assessing, and improving governance programs.
- **GRC-07** | Information System Regulatory Mapping | Identify and document all relevant standards, regulations, legal/contractual,
and statutory requirements, which are applicable to your organization. Review 
at least annually or upon significant changes.
- **GRC-08** | Special Interest Groups | Establish and maintain contact with cloud-related special interest
groups and other relevant entities in line with business context.

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


---

## Required Output Format

Respond with ONLY valid JSON (no markdown code fences, no extra text).
The JSON object has one key per source control ID:

```
{
  "DSP-SaaS-01": {
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

**Save the output as:** `results/09_of_48_Data_Security_and_Privacy_Lifecycle_Mana_x_DSP_to_HRS_result.json`
