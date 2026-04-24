# Batch: [20/72] Identity & Access Management - IAM (part 1) × Family: CCC
# Source: SSCF -> Target: CCM
# Controls in this batch: IAM-SaaS-01, IAM-SaaS-02, IAM-SaaS-03, IAM-SaaS-04, IAM-SaaS-05, IAM-SaaS-06, IAM-SaaS-07, IAM-SaaS-08
# Count: 8
# Target scope: Family: CCC

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Family: CCC — 9 controls. Other target families are covered in separate batches.

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

### IAM-SaaS-03
**Title**: Network Access Restriction
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support restricting logins/access from outside a SaaS customer's network.

The SaaS platform must offer a minimum of two distinct access rule sets, enabling customers to assign specific user groups to more stringent restrictions (e.g., to further limit administrator-level users to a narrower range of networks).

### IAM-SaaS-04
**Title**: Single Sign-On Support
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support federated authentication using the most current version of an industry-standard protocol, such as SAML or OIDC.

If SAML is used, then SSO support for SAML must include IdP-initiated and SP-initiated flows.

### IAM-SaaS-05
**Title**: Single Sign-On Enforcement
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support the option of disabling alternative login methods if federated authentication is enabled for users.

The SaaS platform must be able to disable specific users from this enforcement.

### IAM-SaaS-06
**Title**: NHI governance
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support the identification of Non-Human Identities (NHIs) in UI and via programmatic means.

The SaaS platform must identify NHIs, their type, source/target counterparties, NHI issuance date and expiration (if any, and entitlements.

### IAM-SaaS-07
**Title**: NHI Revocation
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support manual and programmatic revocation of Non-Human Identities (NHIs) by SaaS platform administrators and authorized SaaS platform users.

### IAM-SaaS-08
**Title**: User Credentials Management
**Domain**: Identity & Access Management - IAM
**Description**: The SaaS platform must support administrative control of all credentials issued to SaaS platform users.

Administrative control refers to the ability to view, remove, and reset all authentication factors associated with users and user-provisioned credentials.


---

## CCM Controls Reference — Family: CCC (9 controls)

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

**Save the output as:** `results/20_of_72_Identity_and_Access_Management_-_IAM_1_x_CCC_result.json`
