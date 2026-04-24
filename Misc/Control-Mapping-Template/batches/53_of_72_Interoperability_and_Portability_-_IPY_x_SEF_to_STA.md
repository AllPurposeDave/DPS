# Batch: [53/72] Interoperability & Portability - IPY × Families: SEF, STA
# Source: SSCF -> Target: CCM
# Controls in this batch: IPY-SaaS-01, IPY-SaaS-02
# Count: 2
# Target scope: Families: SEF, STA

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: SEF, STA — 26 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Families: SEF, STA (26 controls)

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

**Save the output as:** `results/53_of_72_Interoperability_and_Portability_-_IPY_x_SEF_to_STA_result.json`
