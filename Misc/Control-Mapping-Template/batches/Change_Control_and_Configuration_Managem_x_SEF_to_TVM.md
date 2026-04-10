# Batch: Change Control and Configuration Management - CCC × Families: SEF, STA, TVM
# Source: SSCF -> Target: CCM
# Controls in this batch: CCC-SaaS-01, CCC-SaaS-02, CCC-SaaS-03, CCC-SaaS-04
# Count: 4
# Target scope: Families: SEF, STA, TVM

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls
address the same security requirement or capability. A "match" means the CCM
control substantively addresses the same security concern, even if scope or language differs.

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

---

## SSCF Controls to Map

### CCC-SaaS-01
**Title**: Programmatic Configurations Querying
**Domain**: Change Control and Configuration Management - CCC
**Description**: The SaaS platform must support programmatic querying of all current security configurations.

If these concepts exist on the SaaS platform, they must be readable via programmatic querying:

1. Authentication
2. RBAC Assignments
3. Entitlements
4. Permissions
5. Resource ACLs
6. Application-specific security concepts
7. Configurations affecting security log coverage (e.g., enabling/disabling streams)
**Details**: Configurations include, but not limited to:
- Authentication
- RBAC Assignments
- Entitlements
- Permissions
- Resource ACLs
- Application-specific security concepts

All security configurations must be readable via API.
**Guidelines**: The output of the API should be in a machine-readable format.

### CCC-SaaS-02
**Title**: Configurations Documentation
**Domain**: Change Control and Configuration Management - CCC
**Description**: The SaaS platform must provide up-to-date documentation of all customer-visible, security-relevant configurations and must make it readily available to SaaS customers.

If these concepts exist on the SaaS platform, configuration documentation must include, but not be limited to:
1. Authentication
2. RBAC Assignments
3. Entitlements
4. Permissions
5. Resource ACLs
6 Application-specific security concepts
7. Audit configuration
**Details**: Configurations dDocumentation must include, but not limited to:
- Authentication
-RBAC Assignments
-Entitlements
-Permissions
-Resource ACLs
-Application-specific security concepts

Documentation must be readily available to SaaS administrators.
**Guidelines**: Documentation should be available via the SaaS provider’s website, within the platform, or community page. Public documentation is recommended.

Documentation should also include versioning and change logs to support traceability and audit requirements.

Any custom language or non-industry standard terms should be explained in detail.

Documentation should include: 
1. Security onboarding documentation. 
2. Focus on the impact of the security configuration.
3. Add default security settings, if applicable. Describe dependencies between configurations, such as one configuration overriding another.
4. Publish the customer responsibility matrix against the Shared Responsibility model, ensuring the customer is aware of what domain areas are supported by the SaaS platform.

### CCC-SaaS-03
**Title**: New Configuration Updates
**Domain**: Change Control and Configuration Management - CCC
**Description**: The SaaS platform must provide notifications about software updates, including new or existing security configuration options, to SaaS customers.
**Details**: New security configuration updates must be notified to SaaS administrators. and users.

They can’t be forced to SaaS administrator and users unless specific “strong” security breach urgency or with delay.

Notification can be made via email or dashboard/UI/release notes (RSS)/Webhook
**Guidelines**: Updates should have a subscribable mechanism that includes relevant release documentation and changes made to the SaaS platform.

It is recommended that console notifications are visible when these changes take place, in addition to a subscribable mechanism.

### CCC-SaaS-04
**Title**: Security Configuration Guidelines
**Domain**: Change Control and Configuration Management - CCC
**Description**: The SaaS platform must provide SaaS customers with best practice security guidelines for relevant security configurations of the SaaS platform and services.
**Details**: The inactive session timeout must allow SaaS administrators to set the inactive session timeout within the SaaS platform or the security configuration API.
**Guidelines**: Security Configuration Guidelines should consider best practices in domains like IDP configuration, interface configuration, principles like least privilege, secure SSO configuration, avoidance of long-lived sessions, and application policies.

The SaaS platform should create a subscribable mechanism that includes relevant changes.

Security Configuration Guidelines should be available via the SaaS provider’s website, within the platform, or community page.


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
  "CCC-SaaS-01": {
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

**Save the output as:** `results/Change_Control_and_Configuration_Managem_x_SEF_to_TVM_result.json`
