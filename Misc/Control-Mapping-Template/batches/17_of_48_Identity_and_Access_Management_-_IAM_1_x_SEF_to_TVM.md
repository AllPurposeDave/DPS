# Batch: [17/48] Identity & Access Management - IAM (part 1) × Families: SEF, STA, TVM
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-01, IAM-SaaS-02, IAM-SaaS-03, IAM-SaaS-04, IAM-SaaS-05, IAM-SaaS-06, IAM-SaaS-07, IAM-SaaS-08
# Count: 8
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

### IAM-SaaS-01
**Title**: User Access Visibility
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must have a user management service that allows administrators to identify users via both UI and programmatic means, as well as their authentication mechanisms.
**Details**: (Intentionally Left Blank)
**Guidelines**: The SaaS platform should include details like:
1. User login mechanisms
2. Last login
3. Last activity

### IAM-SaaS-02
**Title**: User Permissions Enumeration
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS Platform must support enumeration and programmatic querying of all assigned user entitlements.

The platform must provide information about: 
1. Access Permissions
2. Roles
3. Groups
4. Application-specific entitlements
5. Data access entitlements
6. All entitlements for security configuration access.
**Details**: The platform should provide information about: 
-Permissions
-Roles
-Groups
-Application specific entitlements
-Data access entitlements
All security configurations must be readable via API.
**Guidelines**: User permissions enumeration is SaaS platform-specific, and vendor discretion is advised on entitlements implementation.

The SaaS platform should allow SaaS administrators to see the entitlements assigned to each user.

### IAM-SaaS-03
**Title**: Network Access Restriction
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support restricting logins/access from outside a SaaS customer's network.

The SaaS platform must offer a minimum of two distinct access rule sets, enabling customers to assign specific user groups to more stringent restrictions (e.g., to further limit administrator-level users to a narrower range of networks).
**Details**: (Intentionally Left Blank)
**Guidelines**: The SaaS platform should allow for IP restrictions to be separately applied for user logins and integrations, or other non-human connections, including APIs.

Ex. supports IP allowlisting for a SaaS customer instance or the use of a customer-assigned domain.

### IAM-SaaS-04
**Title**: Single Sign-On Support
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support federated authentication using the most current version of an industry-standard protocol, such as SAML or OIDC.

If SAML is used, then SSO support for SAML must include IdP-initiated and SP-initiated flows.
**Details**: If SAML is used then SSO support for SAML must include IDP and SPIF flows
**Guidelines**: This cell intentionally left blank

### IAM-SaaS-05
**Title**: Single Sign-On Enforcement
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support the option of disabling alternative login methods if federated authentication is enabled for users.

The SaaS platform must be able to disable specific users from this enforcement.
**Details**: Ability to disable specific users from this enforcement
**Guidelines**: The SaaS platform should allow Administrators to set up break-glass accounts with alternative login methods, such as username and password, or sign in with an enterprise account.

### IAM-SaaS-06
**Title**: NHI governance
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support the identification of Non-Human Identities (NHIs) in UI and via programmatic means.

The SaaS platform must identify NHIs, their type, source/target counterparties, NHI issuance date and expiration (if any, and entitlements.
**Details**: Platform identifies NHIs, their type, source/target counterparties, and entitlements
**Guidelines**: The SaaS platform should be able to differentiate between non-human identity types (e.g., service accounts), such as third-party integrations, AI agents, marketplace integrations, or custom integrations.

The SaaS platform should provide programmatic access to additional attributes that affect the lifecycles of NHIs, for example:
1. Creation dates of the NHI
2 If applicable, the identity it is delegated from.
3. Access Expiration 
4. Authentication type (secret key, certificate, username and password, etc.)

This would also include application connections, such as users’ tokens on mobile devices.

The SaaS platform should show all entitlements assigned to NHIs (including actions they can take)

NHI accounts should have UI access disabled by default.

### IAM-SaaS-07
**Title**: NHI Revocation
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support manual and programmatic revocation of Non-Human Identities (NHIs) by SaaS platform administrators and authorized SaaS platform users.
**Details**: Separate options to specifically manage NHIs
**Guidelines**: NHI revocation should ensure that session invalidation propagates across all access tokens, refresh tokens, and active sessions for the NHIs.

An example of an authorized user would be users who created the credential.

### IAM-SaaS-08
**Title**: User Credentials Management
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support administrative control of all credentials issued to SaaS platform users.

Administrative control refers to the ability to view, remove, and reset all authentication factors associated with users and user-provisioned credentials.
**Details**: (Intentionally Left Blank)
**Guidelines**: Examples of such credentials are:
User credentials: password, authenticator apps, application credentials issued in the context of users, passkeys, SMS based factor phone numbers

User-provisioned credentials examples: SSH keys, OAuth refresh tokens, api keys, api tokens, OIDC.

Change in credentials should terminate all active sessions for the user and force re-authentication. Change in permissions should take effect immediately.

SaaS platform administrators access to the private credentials (private keys, Passwords, Tokens, or similar) should not be possible.


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
  "IAM-SaaS-01": {
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

**Save the output as:** `results/17_of_48_Identity_and_Access_Management_-_IAM_1_x_SEF_to_TVM_result.json`
