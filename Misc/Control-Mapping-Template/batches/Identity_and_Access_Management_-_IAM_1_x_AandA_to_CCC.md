# Batch: Identity & Access Management - IAM (part 1) × Families: A&A, AIS, BCR, CCC
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-01, IAM-SaaS-02, IAM-SaaS-03, IAM-SaaS-04, IAM-SaaS-05, IAM-SaaS-06, IAM-SaaS-07, IAM-SaaS-08
# Count: 8
# Target scope: Families: A&A, AIS, BCR, CCC

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls
address the same security requirement or capability. A "match" means the CCM
control substantively addresses the same security concern, even if scope or language differs.

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

**Save the output as:** `results/Identity_and_Access_Management_-_IAM_1_x_AandA_to_CCC_result.json`
