# Batch: [29/48] Identity & Access Management - IAM (part 3) × Families: SEF, STA, TVM
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-17, IAM-SaaS-18, IAM-SaaS-19, IAM-SaaS-20, IAM-SaaS-21
# Count: 5
# Target scope: Families: SEF, STA, TVM

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: SEF, STA, TVM — 38 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Families: SEF, STA, TVM (38 controls)

### Security Incident Management, E-Discovery, & Cloud Forensics
- **SEF-01** | Security Incident Management Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for Security Incident Management, E-Discovery, and Cloud
Forensics. Review and update the policies and procedures at least annually, or upon significant changes.
- **SEF-02** | Service Management Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the timely management of security incidents. Review
and update the policies and procedures at least annually, or upon significant changes.
- **SEF-03** | Incident Response Plans | Establish, document, approve, communicate, apply, evaluate and maintain a security 
incident response plan, which includes but is not limited to: a communication strategy 
for notifying relevant internal departments, impacted service customers, and other business 
critical relationships (such as supply-chain) that may be impacted.
- **SEF-04** | Incident Response Testing | Exercise the incident response plans at planned 
intervals or upon significant changes.
- **SEF-05** | Incident Response Metrics | Establish, monitor and report information security incident metrics.
- **SEF-06** | Event Triage Processes | Define, implement and evaluate processes, procedures and technical
measures supporting business processes to triage security-related events.
- **SEF-07** | Incident Management and Response | Define, implement and evaluate processes, procedures and technical measures for timely and 
effective response to security incidents in accordance with incident categories and severity 
levels. Review, update, and test processes and procedures at least annually.
- **SEF-08** | Security Breach Notification | Define and implement processes, procedures and technical measures for security breach 
notifications. Report material security breaches including any relevant supply chain 
breaches, as per applicable SLAs, laws and regulations.
- **SEF-09** | Incident Records Management | Establish and maintain a secure repository of security incident records. Regularly 
review the incident records to identify patterns, root causes, and systemic 
vulnerabilities, and implement relevant corrective measures.
- **SEF-10** | Points of Contact Maintenance | Maintain points of contact for applicable regulation authorities, national and local law enforcement, 
and other legal jurisdictional authorities. Review and update the points of contact at least annually.

### Supply Chain Management, Transparency, and Accountability
- **STA-01** | Supply Chain Risk Management Policies and Procedures | Establish, document, approve, communicate, apply, evaluate, and maintain 
policies and procedures for supply chain risk management. Review and update the policies 
and procedures at least annually, or upon significant changes.
- **STA-02** | SSRM Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the application of the Shared Security Responsibility
Model (SSRM) within the organization. Review and update the policies and procedures
at least annually, or upon significant changes.
- **STA-03** | SSRM Supply Chain | Apply, document, implement and manage the SSRM throughout the supply chain.
- **STA-04** | SSRM Guidance | Provide SSRM Guidance to the service customers detailing information about the SSRM 
applicability throughout the supply chain.
- **STA-05** | SSRM Control Ownership | Delineate the shared ownership and applicability of all CSA CCM controls according to the SSRM.
- **STA-06** | SSRM Documentation Review | Review and validate the SSRM documentation.
- **STA-07** | SSRM Control Implementation | Implement, operate, and audit or assess the portions of the SSRM
which the organization is responsible for.
- **STA-08** | Supply Chain Inventory | Develop and maintain an inventory of all supply chain relationships.
- **STA-09** | Service Bill of Material (BOM) | Define, implement, and enforce a process for establishing a Bill of Material for the service 
supply chain. Review and update the Bill of Material at least annually or upon significant changes.
- **STA-10** | Supply Chain Risk Management | Periodically review risk factors associated with supply chain relationships.
- **STA-11** | Primary Service and Contractual Agreement | Service agreements must incorporate at least the following mutually-agreed upon provisions and/or terms:
• Scope, characteristics and location of business relationship and services offered
• Information security requirements (including SSRM)
• Change management process
• Logging and monitoring capability
• Incident management and communication procedures
• Right to audit and third party assessment
• Service termination
• Interoperability and portability requirements
• Data privacy
• Operational Resilience
- **STA-12** | Supply Chain Agreement Review | Review supply chain agreements at least annually or upon significant changes.
- **STA-13** | Supply Chain Compliance Assessment | Define and implement a process for conducting internal assessments
to confirm conformance and effectiveness of standards, policies, procedures,
and service level agreement activities at least annually.
- **STA-14** | Supply Chain Service Agreement Compliance | Implement policies requiring all service providers throughout the supply chain
to comply with information security, confidentiality, access control, privacy,
audit, personnel policy and service level requirements and standards.
- **STA-15** | Supply Chain Governance Review | Review the organization's service providers' IT governance policies and procedures 
at least annually or upon significant changes.
- **STA-16** | Supply Chain Data Security Assessment | Define and implement a process for conducting risk-based security assessments 
of the supply chain.

### Threat & Vulnerability Management
- **TVM-01** | Threat and Vulnerability Management Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain policies and procedures to 
identify, report and prioritize the remediation of vulnerabilities and threats, in order to protect 
systems against vulnerability exploitation. Review and update the policies and procedures at least 
annually, or upon significant changes.
- **TVM-02** | Malware and Malicious Instructions Protection Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain policies and procedures to 
protect against malware and malicious instructions. Review and update the policies and procedures 
at least annually, or upon significant changes.
- **TVM-03** | Vulnerability Identification | Define, implement and evaluate processes, procedures and technical measures for the detection of 
vulnerabilities on organizationally managed assets at least monthly.
- **TVM-04** | Threat Analysis and Modelling | Define, implement, and evaluate a threat analysis process and procedures to identify, assess 
and review the threat landscape for cloud systems. Build threat models according to industry 
best practices to inform the risk mitigation strategy.
- **TVM-05** | Detection Updates | Define, implement and evaluate processes, procedures and technical
measures to update detection tools, threat signatures, and indicators of compromise
on a weekly, or more frequent basis.
- **TVM-06** | External Library Vulnerabilities | Define, implement and evaluate processes, procedures and technical
measures to identify updates for applications which use third party or open
source libraries according to the organization's vulnerability management policy.
- **TVM-07** | Penetration Testing | Define, implement and evaluate processes, procedures and technical
measures for the periodic performance of penetration testing by independent
third parties.
- **TVM-08** | Vulnerability Remediation Schedule | Define, implement and evaluate processes, procedures and technical measures 
based on identified risks to support scheduled and emergency responses to 
vulnerability identification.
- **TVM-09** | Vulnerability Prioritization | Use a risk-based method for effective prioritization of vulnerability
remediation using an industry recognized framework.
- **TVM-10** | Threat Response | Use a risk-based method for the prioritization and mitigation of threats, 
leveraging an industry-recognized framework to guide threat decision-making 
and protection measures.
- **TVM-11** | Vulnerability Management Reporting | Define and implement a process for tracking and reporting vulnerability
identification and remediation activities that includes stakeholder notification.
- **TVM-12** | Vulnerability Management Metrics | Establish, monitor and report metrics for vulnerability identification
and remediation at defined intervals.


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

**Save the output as:** `results/29_of_48_Identity_and_Access_Management_-_IAM_3_x_SEF_to_TVM_result.json`
