# Batch: [58/72] Logging and Monitoring - LOG × Family: DCS
# Source: SSCF -> Target: CCM
# Controls in this batch: LOG-SaaS-01, LOG-SaaS-02, LOG-SaaS-03, LOG-SaaS-04, LOG-SaaS-05, LOG-SaaS-06, LOG-SaaS-07
# Count: 7
# Target scope: Family: DCS

---

## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** SSCF control listed below, identify which CCM controls address the same security requirement or capability. A "match" means the CCM control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: Only Family: DCS — 18 controls. Other target families are covered in separate batches.

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

### LOG-SaaS-03
**Title**: Programmatic Logs Delivery
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform must support programmatic log delivery via a push or pull mechanism.

### LOG-SaaS-04
**Title**: Logs Retention
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform Logs must be retained and are available to customers.

Logs must be made available to the customer for a minimum of 7 days.

### LOG-SaaS-05
**Title**: Logs Delivery Latency
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform Logs must be delivered without undue delay or latency.

Logs must be made available and deliverable to or by the customer without undue delay, but at most within 24 hours.

### LOG-SaaS-06
**Title**: Log Events Documentation
**Domain**: Logging and Monitoring - LOG
**Description**: The SaaS platform must provide documentation for log events.

Log format, log types, and specific fields provided by the SaaS platform must be documented and accessible by customers.

### LOG-SaaS-07
**Title**: Log Integrity
**Domain**: Logging and Monitoring - LOG
**Description**: If the SaaS platform allows logs to be mutable, it must provide an administrative mechanism for logs to be made immutable.


---

## CCM Controls Reference — Family: DCS (18 controls)

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

**Save the output as:** `results/58_of_72_Logging_and_Monitoring_-_LOG_x_DCS_result.json`
