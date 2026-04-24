# Batch: [43/72] Identity & Access Management - IAM (part 3) × Families: IPY, I&S, LOG
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-17, IAM-SaaS-18, IAM-SaaS-19, IAM-SaaS-20, IAM-SaaS-21
# Count: 5
# Target scope: Families: IPY, I&S, LOG

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: IPY, I&S, LOG — 27 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Families: IPY, I&S, LOG (27 controls)

### Interoperability & Portability
- **IPY-01** | Interoperability and Portability Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for interoperability and portability including
requirements for:
a. Communications between application interfaces
b. Information processing interoperability
c. Application development portability
d. Information/Data exchange, usage, portability, integrity, and persistence
Review and update the policies and procedures at least annually, or upon significant changes.
- **IPY-02** | Application Interface Availability | Provide application interface(s) to service customers so that they programmatically
retrieve their data to enable interoperability and portability.
- **IPY-03** | Secure Interoperability and Portability Management | Implement cryptographically secure network protocols for the management, import 
and export of data, according to industry standards.
- **IPY-04** | Data Portability Contractual Obligations | Agreements must include provisions specifying service customers' access to data
upon contract termination and will include:
a. Data format
b. Length of time the data will be stored
c. Scope of the data retained and made available to the service customers
d. Data deletion policy

### Infrastructure Security
- **I&S-01** | Infrastructure and Virtualization Security Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for infrastructure and virtualization security. Review
and update the policies and procedures at least annually, or upon significant changes.
- **I&S-02** | Capacity and Resource Planning | Plan and monitor the availability, quality, and adequate capacity
of resources in order to deliver the required system performance as determined
by the business.
- **I&S-03** | Network Security | Monitor, encrypt and restrict communications between environments, services, and applications
to only authenticated and authorized connections, as justified by the business.
Review these configurations at least annually, and support them by a documented
justification of all allowed services, protocols, ports, and compensating controls.
- **I&S-04** | OS Hardening and Base Controls | Harden host and guest OS, hypervisor or infrastructure control plane
according to their respective best practices, and supported by technical controls,
as part of a security baseline.
- **I&S-05** | Production and Non-Production Environments | Separate production and non-production environments to reduce the risk of sensitive 
production data being used in non-production environments. Production data is 
sanitized or protected before any authorized non-production use.
- **I&S-06** | Segmentation and Segregation | Design, develop, deploy and configure applications and infrastructures such that 
service customer (tenant) access is appropriately segmented and segregated, 
monitored and restricted.
- **I&S-07** | Migration to Cloud Environments | Use secure and encrypted communication channels when migrating servers,
services, applications, or data to cloud environments. Such channels must include
only up-to-date and approved protocols.
- **I&S-08** | Network Architecture Documentation | Identify and document high-risk environments based on data sensitivity, threat exposure, 
and business impact.
- **I&S-09** | Network Defense | Define, implement and evaluate processes, procedures and defense-in-depth
techniques for protection, detection, and timely response to network-based attacks.

### Logging and Monitoring
- **LOG-01** | Logging and Monitoring Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for logging and monitoring. Review and update the policies
and procedures at least annually, or upon significant changes.
- **LOG-02** | Audit Logs Protection | Define, implement and evaluate processes, procedures and technical
measures to ensure the security and retention of audit logs.
- **LOG-03** | Security Monitoring and Alerting | Identify and monitor security-related events within applications
and the underlying infrastructure. Define and implement a system to generate
alerts to responsible stakeholders based on such events and corresponding metrics.
- **LOG-04** | Audit Logs Access and Accountability | Restrict audit log access to authorized identities and maintain records of that access.
- **LOG-05** | Audit Logs Monitoring and Response | Implement and maintain capabilities to correlate and monitor security audit logs for the 
detection of suspicious or anomalous activity that deviates from typical or expected 
patterns. Establish and follow a defined process to review and take appropriate and timely 
actions on detected anomalies.
- **LOG-06** | Clock Synchronization | Use a reliable time source across all relevant information processing
systems.
- **LOG-07** | Logging Scope | Establish, document and implement which information meta/data system
events should be logged. Review and update the scope at least annually or whenever
there is a change in the threat environment, and as per relevant regulatory requirements.
- **LOG-08** | Audit Logs Sanitization | Define, implement and evaluate technical measures for service customers to detect and scrub or tokenize 
sensitive data from logs to prevent unauthorized exposure, as per applicable laws and regulations.
- **LOG-09** | Log Records | Generate audit records containing relevant security information.
- **LOG-10** | Audit Records Protection | Protect audit records from unauthorized access, modification, and deletion.
- **LOG-11** | Encryption Monitoring and Reporting | Establish and maintain a monitoring and internal reporting capability
over the operations of cryptographic, encryption and key management policies,
processes, procedures, and controls.
- **LOG-12** | Transaction/Activity Logging | Log and monitor key lifecycle management events to enable auditing
and reporting on usage of cryptographic keys.
- **LOG-13** | Access Control Logs | Monitor and log physical access using an auditable access control
system.
- **LOG-14** | Failures and Anomalies Reporting | Define, implement and evaluate processes, procedures and technical
measures for the reporting of anomalies and failures of the monitoring system
and provide immediate notification to the accountable party.


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

**Save the output as:** `results/43_of_72_Identity_and_Access_Management_-_IAM_3_x_IPY_to_LOG_result.json`
