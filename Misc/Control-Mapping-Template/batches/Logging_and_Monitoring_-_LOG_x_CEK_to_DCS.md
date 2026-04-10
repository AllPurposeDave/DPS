# Batch: Logging and Monitoring - LOG × Families: CEK, DCS
# Source: SSCF -> Target: CCM
# Controls in this batch: LOG-SaaS-01, LOG-SaaS-02, LOG-SaaS-03, LOG-SaaS-04, LOG-SaaS-05, LOG-SaaS-06, LOG-SaaS-07
# Count: 7
# Target scope: Families: CEK, DCS

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls
address the same security requirement or capability. A "match" means the CCM
control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Families: CEK, DCS — 39 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Families: CEK, DCS (39 controls)

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

### Datacenter Security
- **DCS-01** | Physical and Environmental Security Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain 
policies and procedures for physical and environmental security. Review and 
update the policies and procedures at least annually, or upon significant changes.
- **DCS-02** | Off-Site Equipment Disposal Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the secure disposal of equipment used outside the
organization's premises. If the equipment is not physically destroyed a data
destruction procedure that renders recovery of information impossible must be
applied. Review and update the policies and procedures at least annually, or upon significant changes.
- **DCS-03** | Off-Site Transfer Authorization Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the relocation or transfer of hardware, software,
or data/information to an offsite or alternate location. The relocation or transfer
request requires the written or cryptographically verifiable authorization.
Review and update the policies and procedures at least annually, or upon significant changes.
- **DCS-04** | Secure Area Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for maintaining a safe and secure working environment
in offices, rooms, and facilities. Review and update the policies and procedures
at least annually, or upon significant changes.
- **DCS-05** | Secure Media Transportation Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for the secure transportation of physical media. Review
and update the policies and procedures at least annually, or upon significant changes.
- **DCS-06** | Assets Classification | Classify and document the physical, and logical assets (e.g., applications)
based on the organizational business risk. Review and update the assets’ classification 
at least annually, or upon significant changes.
- **DCS-07** | Assets Cataloguing and Tracking | Catalogue and track all relevant physical and logical assets located at all of the service provider's sites 
within a secured system. Review and update the catalogue at least annually or upon significant changes.
- **DCS-08** | Controlled Physical Access Points | Design and implement physical security perimeters to safeguard personnel, data,
and information systems.
- **DCS-09** | Equipment Identification | Use equipment identification as a method for connection authentication.
- **DCS-10** | Secure Area Authorization | Allow only authorized personnel access to secure areas, with all
ingress and egress points restricted, documented, and monitored by physical
access control mechanisms. Retain access control records on a periodic basis
as deemed appropriate by the organization.
- **DCS-11** | Surveillance System | Implement, maintain, and operate datacenter surveillance systems
at the external perimeter and at all the ingress and egress points to detect
unauthorized ingress and egress attempts.
- **DCS-12** | Adverse Event Response Training | Train datacenter personnel to safely manage adverse events, including but not limited 
to unauthorized ingress and egress attempts.
- **DCS-13** | Cabling Security | Define, implement and evaluate processes, procedures and technical
measures that ensure a risk-based protection of power and telecommunication
cables from a threat of interception, interference or damage at all facilities,
offices and rooms.
- **DCS-14** | Environmental Systems | Implement and maintain data center environmental control systems
that monitor, maintain and test for continual effectiveness the temperature
and humidity conditions within accepted industry standards.
- **DCS-15** | Secure Utilities | Secure, monitor, maintain, and test utilities services for continual
effectiveness at planned intervals.
- **DCS-16** | Equipment Location | Keep business-critical equipment away from locations subject to high
probability for environmental risk events.
- **DCS-17** | Datacenter Metrics | Establish, monitor and report datacenter security metrics to secure data center assets and services.
- **DCS-18** | Datacenter Operations Resilience | Define, implement and evaluate processes, procedures and technical measures to ensure continuous operations.


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

**Save the output as:** `results/Logging_and_Monitoring_-_LOG_x_CEK_to_DCS_result.json`
