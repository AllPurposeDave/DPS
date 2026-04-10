# Batch: Logging and Monitoring - LOG × Families: SEF, STA, TVM
# Source: SSCF -> Target: CCM
# Controls in this batch: LOG-SaaS-01, LOG-SaaS-02, LOG-SaaS-03, LOG-SaaS-04, LOG-SaaS-05, LOG-SaaS-06, LOG-SaaS-07
# Count: 7
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

### LOG-SaaS-01
**Title**: Logged Events Scope
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform must provide security logs to SaaS customers.

Events from both NHIs and humans must be captured in logs, including:
1. Sign in attempts (fail + pass)
2. All configuration changes 
3. Creating integrations, including into other SaaS platforms.
4. Creation, deletion, and/or modification of API keys.
5. OAuth access key generation using a refresh token.
6. User impersonation (including by local administrators or user-to-user role assumption).
7. Creation and modification of user accounts and their permissions
8. Each authentication step, including MFA stages and the factor used.
9. Bulk export and mass data reporting activity.
**Details**: Events that must be captured in logs include at least:
-Sign in attempts (fail + pass)
-all configuration changes 
-user level changes of sharing
-creating integrations to other Saas apps
-Creation or modification of API keys
-OAuth access key generation using a refresh token
-user impersonation from local admins
-user to user impersonation
-failed authorization (e.g., accessing URL user is not authorized to)
-Creation and modification of user accounts and their permissions
-Each authentication step, including MFA stages and factor used
-Bulk export and mass data reporting activity
**Guidelines**: The logs should be in a machine-readable format (suggested example JSON).

Logs should include
1. All configuration changes that impact the customer UI and configuration.
2. Non-administrative changes.
3. Sharing of objects.

Logs for User Impersonation: the User ID does not need to include email address or full name, just a unique identifier of the impersonating user.

### LOG-SaaS-02
**Title**: Log Records Mandatory Fields
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform Logs must contain the following security-relevant information: 
1. Timestamp
2. User ID/username, or NHI ID (If applicable)
3. Impersonation user ID, whether from a customer or SaaS provider.
4. IP address
5. User agent (if applicable)
6. Source of change context (API/UI/App)
7. Action
8. Target resource
9. Non-sensitive session identifier
**Details**: Each log must include at least the following fields: 
-timestamp,
-user id, 
-level of permissions
-visibility level
-impersonation user id whether from customer or vendor or application
-ip address
-user agent (if applicable)
-source of change context (API/UI/App)
-action
-target resource
-Non-sensitive session identifier
**Guidelines**: The logs should 
1. Describe the source of change - API vs UI vs 3rd party app vs SaaS provider, making changes to customer visible configurations.
2. Describe target resource (field/display names).
3. Describe the session identifier.

If items like an IP address are not applicable, they can be excluded.

For clarity, this only applies to the SaaS platform logs (not backend activity)

Non-sensitive session identifier is a unique identifier representing an authenticated session (not a confidential session value)

### LOG-SaaS-03
**Title**: Programmatic Logs Delivery
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform must support programmatic log delivery via a push or pull mechanism.
**Guidelines**: The logs should be in a machine-readable format (suggested example JSON). 

Common delivery mechanisms include pulling logs from the SaaS platform API endpoint or automatic delivery from the SaaS platform via webhook or cloud storage bucket.

For SaaS platforms where logs may be delivered out of order and a pull mechanism from the customer is available, customers should be able to query based on log delivery time (as opposed to event time). This prevents gaps for out-of-order logs that are continuously retrieved.

### LOG-SaaS-04
**Title**: Logs Retention
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform Logs must be retained and are available to customers.

Logs must be made available to the customer for a minimum of 7 days.
**Details**: Logs must be available to customers for at least 7 days.
**Guidelines**: It is recommended that logs are available for 30 days or longer for critical log types such as login events.

### LOG-SaaS-05
**Title**: Logs Delivery Latency
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform Logs must be delivered without undue delay or latency.

Logs must be made available and deliverable to or by the customer without undue delay, but at most within 24 hours.
**Details**: Logs must be made available and retrievable by the customer without undue delay but at most within 24 hours
**Guidelines**: The SaaS platform should allow throttling mechanisms to allow the timely delivery of logs to customers.

### LOG-SaaS-06
**Title**: Log Events Documentation
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform must provide documentation for log events.

Log format, log types, and specific fields provided by the SaaS platform must be documented and accessible by customers.
**Details**: Log format, log types and specific fields provided by the vendor must be documented and accessible by SaaS customers
**Guidelines**: Documentation should be available via the SaaS provider’s website, within the platform, or community page. Public documentation is recommended.

Documentation should also include versioning and change logs to support traceability and audit requirements.

Any custom language or non-industry standard terms should be explained in detail.

### LOG-SaaS-07
**Title**: Log Integrity
**Domain**: Logging and Monitoring - LOG
**Description**: If the SaaS platform allows logs to be mutable, it must provide an administrative mechanism for logs to be made immutable.
**Details**: Logs must be able to be stored in a way which prevents users (including admins) from modifying them.
**Guidelines**: The SaaS provider can still be compliant if they have a specific use case that needs mutable logs, provided that a mechanism exists to disable mutability. This is specifically relevant for platforms that deal with data where logs are redirected to a data storage layer, which the customer fully controls (e.g., storage buckets, database tables)


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
  "LOG-SaaS-01": {
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

**Save the output as:** `results/Logging_and_Monitoring_-_LOG_x_SEF_to_TVM_result.json`
