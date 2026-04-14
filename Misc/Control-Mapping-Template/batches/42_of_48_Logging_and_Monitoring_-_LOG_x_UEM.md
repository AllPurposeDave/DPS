# Batch: [42/48] Logging and Monitoring - LOG × Family: UEM
# Source: SSCF -> Target: CCM
# Controls in this batch: LOG-SaaS-01, LOG-SaaS-02, LOG-SaaS-03, LOG-SaaS-04, LOG-SaaS-05, LOG-SaaS-06, LOG-SaaS-07
# Count: 7
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

**Save the output as:** `results/42_of_48_Logging_and_Monitoring_-_LOG_x_UEM_result.json`
