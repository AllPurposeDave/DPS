---
title: ""
source_file: "Data_Loss_Prevention_Standard_STD-DLP-2026-011_fixed.docx"
modified: "2026-03-28"
doc_id: "STD-DLP-2026-011"
converted: "2026-03-29T23:25:14"
PublishedURL: "https://contoso.sharepoint.com/sites/Policies/Shared Documents/Data_Loss_Prevention_Standard_STD-DLP-2026-011.docx"
Acronyms: ""
---

## Data Loss Prevention Standard

Document ID: STD-DLP-2026-011  |  Version: 1.3  |  Effective Date: March 1, 2026  |  Classification: CUI


# Purpose

This standard defines the technical and procedural requirements for preventing unauthorized disclosure of controlled unclassified information (CUI) and personally identifiable information (PII). It supplements the Information Security Program Charter and provides implementation guidance for DLP tooling and data handling controls.

For federal data categorization requirements, refer to [NIST SP 800-60 data categorization guidance](https://www.google.com).


# Applicability & Scope

This standard applies to all systems, applications, and data flows that process, transmit, or store CUI or PII. It applies to all personnel including employees, contractors, and third-party service providers. For cloud application scope boundaries, see the Cloud Security Policy.

This standard does not replace the Data Classification Policy or the Privacy Impact Assessment procedures. For data classification requirements, refer to [NIST CUI Registry](https://www.linkedin.com).


# Intent

Data loss events are one of the highest-consequence incident types in federal environments. The intent of this standard is to layer technical controls over the data handling requirements in the Information Security Program Charter, ensuring that policy intent translates to enforceable technical enforcement.

DLP controls support compliance with FISMA, Privacy Act of 1974, OMB Circular A-130, and agency-specific CUI handling requirements.


# Section 1: Controls

Controls are organized by function. For DLP alert response procedures, see DLP03.002 and Appendix E. For the approved DLP tool inventory, see Appendix A.


| Control ID | Title | Requirement | NIST | Status | Owner |
| --- | --- | --- | --- | --- | --- |
| DLP01.001 | DLP Tool Deployment | The organization shall deploy DLP tooling on all endpoints and email gateways to inspect outbound data flows for CUI and PII. See Appendix A for approved DLP tool list. See below for details. | SI-12 | Implemented | Security Ops |
| DLP01.002 | Content Inspection Policy | Outbound email shall be subject to automated content inspection as described in Section 2 control DLP05.1234 of this standard. Policy rules are documented in Appendix B. | SI-12 | Implemented | Security Ops |
| DLP02.001 | Data Classification Tagging | All documents containing CUI shall be tagged with approved sensitivity labels per the Data Classification Policy. See Appendix C for label taxonomy. | MP-3 | Implemented | All Users |
| DLP02.002 | Endpoint DLP Enforcement | DLP agents on endpoints shall enforce block actions for attempted exfiltration of CUI to unapproved destinations. Exceptions require ISSM approval per Appendix D. | SI-3 | Partially Implemented | Endpoint Mgmt |
| DLP03.001 | Cloud Application Controls | Sanctioned cloud applications shall be configured with DLP policies restricting upload of sensitive data. Unsanctioned apps shall be blocked per the Network Security Policy. | SC-7 | Implemented | Cloud Security |
| DLP03.002 | DLP Alert Response SLA | DLP alerts classified as High or Critical shall be investigated within 2 hours by the SOC. Alert triage procedures are in Appendix E. | IR-5 | Implemented | SOC |
| DLP04.001 | Removable Media Enforcement | DLP tooling shall enforce encryption requirements for all data written to removable media per the Encryption Policy, Section 2.1. | MP-7 | Implemented | Endpoint Mgmt |
| DLP04.002 | Print and Fax Controls | Printing of CUI documents shall be logged. Fax transmission of CUI is prohibited unless using an approved secure fax solution per Appendix F. | MP-2 | Not Implemented | Facilities |


# Enforcement

Violations of this standard are addressed per the disciplinary framework in Section 6 of the Acceptable Use Policy (POL-AU-2026-006). Intentional data exfiltration constitutes a Level 4 violation. DLP exceptions not pre-approved via Appendix D procedures constitute a Level 3 violation.

For external reporting obligations following a confirmed data loss event, refer to the Incident Response Policy (POL-IR-2026-003), Section IRP03.001.


# References

Acceptable Use Policy (POL-AU-2026-006)

Access Control Policy (POL-AC-2026-001)

Incident Response Policy (POL-IR-2026-003)

Encryption Policy (POL-ENC-2026-008)

NIST SP 800-53 Rev 5 SI-12, MP-3, MP-7 | [NIST Control Catalog](https://www.google.com)

CUI Registry and Handling Requirements | [National Archives CUI Program](https://www.linkedin.com)


# Appendix A - Approved DLP Tool Inventory

The following DLP tools are approved for use within the organization. Deployment of unapproved DLP tools requires ISSM authorization.


| Tool | Coverage | Owner | Review Date |
| --- | --- | --- | --- |
| Microsoft Purview DLP | Email, SharePoint, OneDrive, Endpoints | Security Ops | Quarterly |
| Defender for Endpoint | Endpoint file operations, USB | Endpoint Mgmt | Quarterly |
| Network DLP (Proxy) | Web uploads, cloud app traffic | Network Ops | Semi-annual |


# Appendix B - Email Content Inspection Rules

Email DLP policy rules are configured in Microsoft Purview and reviewed quarterly by the Security Ops team. Current active rules include: CUI keyword detection (per CUI category list), SSN/PII pattern matching (regex), credit card number detection, and attachment classification scanning.

For rule modification requests, submit a change request per the Configuration Management Policy (POL-CM-2026-004), Control CFG02.001.


# Appendix C - Sensitivity Label Taxonomy

The organization uses Microsoft Purview sensitivity labels aligned to the CUI Registry. Labels and handling requirements:


| Label | Category | Handling Requirement |
| --- | --- | --- |
| UNCLASSIFIED | Public / Internal | No restrictions beyond standard acceptable use. |
| CUI | Controlled Unclassified | Encrypt at rest and in transit. Restrict sharing to need-to-know. |
| CUI//SP-CTI | Cyber Threat Intel | Additional access restrictions per CUI SP handling requirements. |
| FOUO | For Official Use Only | Legacy label. Map to CUI for new documents. |


# Appendix D - DLP Exception Request Process

Exceptions to DLP enforcement controls require documented justification and ISSM approval. Exceptions are valid for a maximum of 90 days and must be re-evaluated at expiration.

Submit exception requests via the IT Service Portal. For the request form and approval workflow, see [DLP Exception Request (internal portal)](https://www.google.com).


# Appendix E - DLP Alert Triage Procedures

SOC personnel shall follow this triage sequence for DLP alerts: (1) Classify alert severity per the matrix in IRP02.001. (2) Identify the triggering user and data. (3) Determine if data movement was authorized. (4) If unauthorized: contain immediately, preserve logs, escalate to IR team per IRP01.002. (5) Document in case management system within 1 hour.


# Appendix F - Secure Fax Authorization

CUI transmission via fax is prohibited except using GSA-approved secure fax solutions. Organizations requiring secure fax capability must submit a system authorization request to the ISSM. Approved secure fax solutions are listed in the approved technology register maintained by IT Operations.


# Appendix G - Revision History


| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| 1.3 | 03/01/2026 | A. Patel, Security Ops | Added cloud application controls (DLP03.001) |
| 1.2 | 09/15/2025 | A. Patel, Security Ops | Updated Purview label taxonomy in Appendix C |
| 1.1 | 03/10/2025 | M. Johnson | Added endpoint DLP controls, Appendix D exception process |
| 1.0 | 01/15/2025 | M. Johnson | Initial release |
