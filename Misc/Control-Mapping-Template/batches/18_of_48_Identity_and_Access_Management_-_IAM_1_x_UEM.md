# Batch: [18/48] Identity & Access Management - IAM (part 1) × Family: UEM
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-01, IAM-SaaS-02, IAM-SaaS-03, IAM-SaaS-04, IAM-SaaS-05, IAM-SaaS-06, IAM-SaaS-07, IAM-SaaS-08
# Count: 8
# Target scope: Family: UEM

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Family: UEM — 14 controls. Other target families are covered in separate batches.

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

## CCM Controls Reference — Family: UEM (14 controls)

### Universal Endpoint Management
- **UEM-01** | Endpoint Devices Policy and Procedures | Establish, document, approve, communicate, apply, evaluate and maintain
policies and procedures for all endpoints. Review and update the policies and
procedures at least annually, or upon significant changes.
- **UEM-02** | Application and Service Approval | Define, document, apply and evaluate a list of approved services,
applications and sources of applications (stores) acceptable for use by endpoints
when accessing or storing organization-managed data.
- **UEM-03** | Compatibility | Define and implement a process for the validation of the endpoint
device's compatibility with operating systems and applications.
- **UEM-04** | Endpoint Inventory | Maintain an inventory of all endpoints used to store, access and process company
data.
- **UEM-05** | Endpoint Management | Define, implement and evaluate processes, procedures and technical
measures to enforce policies and controls for all endpoints permitted to access
systems and/or store, transmit, or process organizational data.
- **UEM-06** | Automatic Lock Screen | Configure all relevant interactive-use endpoints to require an automatic
lock screen.
- **UEM-07** | Operating Systems | Manage changes to endpoint operating systems, patch levels, and/or
applications through the company's change management processes.
- **UEM-08** | Storage Encryption | Protect information from unauthorized disclosure on managed endpoint
devices with storage encryption.
- **UEM-09** | Anti-Malware Detection and Prevention | Configure managed endpoints with anti-malware detection and prevention
technology and services.
- **UEM-10** | Software Firewall | Configure managed endpoints with properly configured software firewalls.
- **UEM-11** | Data Loss Prevention | Configure managed endpoints with Data Loss Prevention (DLP) technologies
and rules in accordance with a risk assessment.
- **UEM-12** | Remote Locate | Enable remote geo-location capabilities for all managed mobile endpoints, according 
to all applicable laws and regulations.
- **UEM-13** | Remote Wipe | Define, implement and evaluate processes, procedures and technical
measures to enable the deletion of company data remotely on managed endpoint
devices.
- **UEM-14** | Third-Party Endpoint Security Posture | Define, implement and evaluate processes, procedures and technical
and/or contractual measures to maintain proper security of third-party endpoints
with access to organizational assets.


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

**Save the output as:** `results/18_of_48_Identity_and_Access_Management_-_IAM_1_x_UEM_result.json`
