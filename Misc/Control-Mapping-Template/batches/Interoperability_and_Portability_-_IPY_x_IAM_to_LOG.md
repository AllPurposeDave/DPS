# Batch: Interoperability & Portability - IPY × Families: IAM, IPY, I&S, LOG
# Source: SSCF -> Target: CCM
# Controls in this batch: IPY-SaaS-01, IPY-SaaS-02
# Count: 2
# Target scope: Families: IAM, IPY, I&S, LOG

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls
address the same security requirement or capability. A "match" means the CCM
control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: IAM, IPY, I&S, LOG — 42 controls. Other target families are covered in separate batches.

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

### IPY-SaaS-01
**Title**: Export Capability
**Domain**: Interoperability & Portability - IPY
**Description**: If the SaaS platform offers mass data export functionality, it must allow SaaS administrators to disable this functionality for non-administrative users.
**Details**: (Intentionally Left Blank)
**Guidelines**: Export capability should be disabled by default for non-administrative users.

### IPY-SaaS-02
**Title**: Integration Attribution
**Domain**: Interoperability & Portability - IPY
**Description**: The SaaS platform must implement a mechanism to allow or deny connections based on the verified creator of the integration. 

When SaaS platform users are prompted to accept integrations (e.g., via a consent screen), the acceptance process must display at least one verifiable attribute of the application's creator, such as their email address domain. This verifiable ownership attribute must be visible both during the acceptance process and in the list of connected integrations, as stipulated in IAM-SaaS-06.

Verification of the integration creator must be performed by the SaaS platform using an application-appropriate mechanism.
**Guidelines**: An example of a SaaS platform-appropriate mechanism can be confirmed by the email address of the creator, or the domain used in the OAuth consent (for relevant flows).


---

## CCM Controls Reference — Families: IAM, IPY, I&S, LOG (42 controls)

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

**Save the output as:** `results/Interoperability_and_Portability_-_IPY_x_IAM_to_LOG_result.json`
