# Batch: [37/48] Logging and Monitoring - LOG × Families: A&A, AIS, BCR, CCC
# Source: SSCF -> Target: CCM
# Controls in this batch: LOG-SaaS-01, LOG-SaaS-02, LOG-SaaS-03, LOG-SaaS-04, LOG-SaaS-05, LOG-SaaS-06, LOG-SaaS-07
# Count: 7
# Target scope: Families: A&A, AIS, BCR, CCC

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: A&A, AIS, BCR, CCC — 34 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Families: A&A, AIS, BCR, CCC (34 controls)

### Audit & Assurance
- **A&A-01** | Audit and Assurance Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
audit and assurance policies and procedures and standards. Review and update
the policies and procedures at least annually, or upon significant changes.
- **A&A-02** | Independent Assessments | Conduct independent audit and assurance assessments according to
relevant standards at least annually.
- **A&A-03** | Risk Based Planning Assessment | Perform independent audit and assurance assessments according to
risk-based plans and policies,and in response to significant changes or emerging risks.
- **A&A-04** | Requirements Compliance | Verify compliance with all relevant standards, regulations, legal/contractual,
and statutory requirements applicable to the audit.
- **A&A-05** | Audit Management Process | Define and implement an Audit Management process aligned with relevant auditing standards to support audit
planning, risk analysis, security control assessment, conclusion, remediation
schedules, report generation, and review of past reports and supporting evidence.
- **A&A-06** | Remediation | Establish, document, approve, communicate, apply, evaluate and maintain
a risk-based corrective action plan to remediate audit findings, regularly review and
report remediation status to relevant stakeholders.

### Application & Interface Security
- **AIS-01** | Application and Interface Security Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for application security. Review and update the policies and procedures at least
annually, or upon significant changes.
- **AIS-02** | Application Security Baseline Requirements | Establish, document and maintain baseline requirements for securing
applications.
- **AIS-03** | Application Security Metrics | Define and implement technical and operational metrics in alignment
with business objectives, security requirements, and compliance obligations.
- **AIS-04** | Secure Application Development Lifecycle | Define and implement a secure SDLC process for application requirements analysis, planning, design, development,
testing, deployment, and operation in accordance with security requirements.
- **AIS-05** | Application Security Testing | Implement a testing strategy, including criteria for acceptance of
new information systems, upgrades and new versions, which provides application
security assurance and maintains compliance while meeting organizational delivery goals. Automate when applicable and possible.
- **AIS-06** | Secure Application Deployment | Establish and implement strategies and capabilities for secure, standardized,
and compliant application deployment. Automate where possible.
- **AIS-07** | Application Vulnerability Remediation | Define and implement a process to remediate application security
vulnerabilities, automating remediation when possible.
- **AIS-08** | API Security | Define and implement processes, procedures, and technical measures to secure APIs. Review and update
for any improvements at least annually or upon significant changes.

### Business Continuity Management and Operational Resilience
- **BCR-01** | Business Continuity Management Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
business continuity management and operational resilience policies and procedures.
Review and update the policies and procedures at least annually, or upon significant changes.
- **BCR-02** | Risk Assessment and Impact Analysis | Determine the impact of business disruptions and risks to establish
criteria for developing business continuity and operational resilience strategies
and capabilities. Review and update the risk assessment and impact analysis at least annually or upon significant changes.
- **BCR-03** | Business Continuity Strategy | Establish strategies to reduce the impact of business disruptions, and improve resiliency and 
recovery from business disruptions.
- **BCR-04** | Business Continuity Planning | Establish, document, approve, communicate, apply, evaluate and maintain
a business continuity plan based on the results of the operational resilience
strategies and capabilities.
- **BCR-05** | Documentation | Develop, identify, and acquire documentation, both internally and from external parties, that is relevant to
support the business continuity and operational resilience plans. Make the
documentation available to authorized stakeholders and review at least annually or upon significant changes.
- **BCR-06** | Business Continuity Exercises | Exercise and test business continuity and operational resilience
plans at least annually or upon significant changes.
- **BCR-07** | Communication | Establish and maintain communication channels with all relevant stakeholders in the
course of business continuity and resilience procedures.
- **BCR-08** | Backup | Periodically perform backups. Ensure the confidentiality,
integrity and availability of the backup, and verify restoration from backup
for resiliency.
- **BCR-09** | Disaster Response Plan | Establish, document, approve, communicate, apply, evaluate and maintain
a disaster response plan to recover from natural and man-made disasters. Update
the plan at least annually or upon significant changes.
- **BCR-10** | Response Plan Exercise | Exercise the disaster response plan annually or upon significant
changes, including if possible, the participation of local emergency authorities.
- **BCR-11** | Equipment Redundancy | Supplement business-critical equipment with both locally redundant and geographically dispersed equipment
located at a reasonable minimum distance in accordance with applicable industry
standards.

### Change Control and Configuration Management
- **CCC-01** | Change Management Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for managing the risks associated with applying changes
to assets owned, controlled or used by the organization. Review and update the policies and procedures at least annually, or upon significant changes.
- **CCC-02** | Quality Testing | Establish, maintain and implement a defined quality change control, approval and testing process
incorporating baselines, testing, and release standards.
- **CCC-03** | Change Management Technology | Implement a change management procedure to manage the risks associated with applying changes 
to assets, owned, controlled or used by the organization.
- **CCC-04** | Unauthorized Change Protection | Implement and enforce a procedure to authorize the addition, removal, update, and management 
of assets that are owned, controlled or used by the organization.
- **CCC-05** | Change Agreements | Include provisions limiting changes directly impacting service customers owned environments (tenants) 
to explicitly authorized requests within service level agreements.
- **CCC-06** | Change Management Baseline | Establish, document and implement change management and configuration baselines for all relevant 
authorized changes on organization assets. Review and update the baselines at least annually or upon significant changes.
- **CCC-07** | Detection of Baseline Deviation | Implement detection measures with proactive notification in case
of changes deviating from the established baseline.
- **CCC-08** | Exception Management | Implement a procedure for the management of exceptions, including
emergencies, in the change and configuration process. Align the procedure with
the requirements of GRC-04: Policy Exception Process.
- **CCC-09** | Change Restoration | Define and implement a process to proactively roll back changes to
a previous known good state in case of errors or security concerns.


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

**Save the output as:** `results/37_of_48_Logging_and_Monitoring_-_LOG_x_AandA_to_CCC_result.json`
