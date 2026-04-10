# Batch: Change Control and Configuration Management - CCC × Families: CEK, DCS
# Source: SSCF -> Target: CCM
# Controls in this batch: CCC-SaaS-01, CCC-SaaS-02, CCC-SaaS-03, CCC-SaaS-04
# Count: 4
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

**Save the output as:** `results/Change_Control_and_Configuration_Managem_x_CEK_to_DCS_result.json`
