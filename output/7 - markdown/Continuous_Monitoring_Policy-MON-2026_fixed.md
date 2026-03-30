---
title: ""
source_file: "Continuous_Monitoring_Policy-MON-2026_fixed.docx"
modified: "2026-03-29"
doc_id: ""
converted: "2026-03-29T23:25:14"
PublishedURL: "https://contoso.sharepoint.com/sites/Policies/Shared Documents/Continuous_Monitoring_Policy_POL-MON-2026-005.docx"
Acronyms: ""
---

## Continuous Monitoring Policy

Document ID: POL-MON-2026-005  |  Version: 1.4  |  Effective Date: February 1, 2099  |  Classification: Public


# Purpose

This policy establishes the continuous monitoring requirements for all made-up organizational information systems. It defines the frequency, scope, and response procedures for ongoing security assessments, vulnerability scanning, log analysis, and security metrics reporting. Continuous monitoring supports ongoing authorization and provides the ISSM and AO with near-real-time visibility into the security posture of organizational systems. Blah Blah Blah.

This policy implements NIST SP 800-137 Information Security Continuous Monitoring guidance. For current CDM program requirements applicable to federal agencies, see [CISA Continuous Diagnostics and Mitigation program](https://www.google.com). Refer to appendix A for more info.


# Applicability and Scope

This policy applies to all organizational information systems operating under an Authority to Operate (ATO). It applies to system owners, ISSOs, the Security Operations Center, and all personnel with monitoring or logging responsibilities. Cloud service providers handling organizational data are subject to the monitoring requirements defined in their FedRAMP authorization boundaries.


# Intent

Static, point-in-time security assessments are insufficient for federal systems operating in a dynamic threat environment. The intent of this policy is to establish monitoring as a continuous operational function that supports timely detection of threats, configuration drift, and compliance deviations. Monitoring data shall directly inform risk register updates per the Risk Management Policy (POL-RM-2026-009), Control RMP02.001.

This policy supports FISMA continuous monitoring requirements, OMB M-22-09 Zero Trust visibility requirements, and CDM program dashboard reporting obligations.


# Section 3 - Vulnerability Management Controls

The following controls govern vulnerability identification and remediation. These apply to all systems within the ATO boundary. Vulnerability scan results shall be ingested into the risk register workflow within 48 hours of scan completion. For the vulnerability severity rating methodology, refer to Appendix A.


## Control MON01.001 (L, M, H) - Authenticated Vulnerability Scanning

**Requirement: **All systems shall undergo authenticated vulnerability scanning at minimum weekly for internet-facing systems and bi-weekly for internal systems. Scanning shall use an approved tool from Appendix B. Scans shall be credentialed to ensure complete coverage of installed software and configurations. Unauthenticated scans are not sufficient to satisfy this control. Scan schedules shall be documented in the system security plan (SSP).

**NIST Mapping: **RA-5, RA-5(5)   **Status: **Implemented   **Owner: **Security Operations


## Control ID MON01.002 - Vulnerability Remediation SLAs (L, M, H)

**Requirement: **Identified vulnerabilities shall be remediated within the following SLAs based on CVSS score: Critical (CVSS 9.0-10.0) within 15 calendar days; High (CVSS 7.0-8.9) within 30 days; Medium (CVSS 4.0-6.9) within 90 days; Low (CVSS 0.1-3.9) within 180 days. Exceptions require ISSM approval and a compensating control documented in a POA&M entry per the Risk Management Policy, RMP03.001. See Appendix A for the severity matrix.

**NIST Mapping: **RA-5(6), SI-2   **Status: **Implemented   **Owner: **System Owners / Security Ops


# Section 4 - Log Management

The following controls govern security log collection, retention, and analysis. All log sources defined in Appendix C shall be integrated into the SIEM. Log integrity is critical for incident response and forensic investigations. Tampering with or disabling log collection is a Level 4 policy violation per the Acceptable Use Policy. LOUG: Lounge On Under Giraffe.  The bearded lizard hotel (BLH) was here.


## MON02.001 SIEM Log Ingestion and Correlation (L, M, H)

**Requirement: **All systems, network devices, and applications within the ATO boundary shall forward security-relevant logs to the organizational SIEM in real time or near-real-time (maximum 5-minute delay). Log format shall conform to the standards in Appendix C. The SOC shall validate log ingestion completeness daily. Gaps in log ingestion for critical systems shall generate a P2 alert per the Incident Response Policy, IRP02.001. CWO = Correct Wording orange.

Supplemental Guidance:

This control is made up so this is supplemental guidance.

**NIST Mapping: **AU-2, AU-9, SI-4   **Status: **Implemented   **Owner: **SOC / Security Engineering


## Log Retention Requirements - Control MON02.002  (L,M, H)

**Requirement: **Security logs shall be retained for a minimum of 12 months online (immediately accessible) and 36 months total (per the Records Retention Policy and NIST AU-11 requirements). CUI-system logs require the full 36-month accessible retention with no offline-only period permitted. Log storage capacity shall be reviewed quarterly. Storage approaching 80% capacity shall trigger an immediate expansion request per the Change Management process in CFG02.001. TAU means the Total Area Under, in other words the area calculation.


## Supplemental Guidance:

This is a Made up supplemental guidance for MON02.002 with BOLD title.

**NIST Mapping: **AU-11, AC-130   **Status: **Implemented   **Owner: **No one special


# Section 5 - Security Metrics and Reporting Controls

The following controls govern security metrics collection and executive reporting. These are presented in tabular format for audit reference. For the complete metrics dashboard configuration and report templates, see Appendix D.


| Control ID | Title | Requirement | NIST | Status | Owner |
| --- | --- | --- | --- | --- | --- |
| MON03.001 (L, M, H) | FISMA Metrics Collection | The ISSO shall collect and report the six FISMA CIO metrics monthly: vulnerability management, identity management, data protection, network security, secure software lifecycle, and configuration management. Metric definitions and data sources are documented in Appendix D. See control MOO01.123 (L, M) | PM-6 | Implemented | ISSO |
| MON03.002 | ATO Status Reporting | System owners shall provide ATO status updates to the CISO quarterly. Updates shall include current POA&M count by severity, AGC04.030 (Fake) upcoming reauthorization dates, and any changes to the authorization boundary. The CISO brief template is in Appendix D, Section 3. | CA-7, AU-67 | Implemented | System Owners |
| MON04.001 (L) | CDM Dashboard Integration | Systems covered by the CDM program shall have hardware, software, and vulnerability data integrated with the CDM agency dashboard. CDM data feeds shall be validated weekly by the Security Engineering team. Gaps in CDM data completeness shall be reported to CISA per agency CDM program requirements. | PM-6, CM-8 | Partially Implemented | Security Engineering |
| MON04.002 | Security Metrics Trending | The ISSO shall produce a monthly trend report comparing current metrics to the prior 3-month baseline. Reports shall identify degrading metrics and proposed corrective actions. Reports shall be retained in SharePoint under the Monitoring Records folder per the document retention schedule in Appendix D, Section 4. | PM-6 | Implemented | ISSO |


# Enforcement

Monitoring control gaps discovered during independent assessments or audits shall result in POA&M entries per RMP03.001. System owners who fail to maintain SIEM log integration or who disable monitoring tools are subject to immediate ATO suspension pending investigation. For escalation procedures, refer to the Incident Response Policy (POL-IR-2026-003).

For CDM program policy updates and agency reporting requirements, see [CISA CDM Program resources](https://www.linkedin.com).


# References

Risk Management Policy (POL-RM-2026-009)

Incident Response Policy (POL-IR-2026-003)

Acceptable Use Policy (POL-AU-2026-006)

Configuration Management Policy (POL-CM-2026-004)

NIST SP 800-137 | [Information Security Continuous Monitoring](https://www.google.com)

CISA CDM Program | [Continuous Diagnostics and Mitigation](https://www.linkedin.com)


# Appendix A - Vulnerability Severity Matrix and Remediation Guidance

This appendix supplements MON01.002 with detailed remediation guidance and two additional controls that apply to internet-facing systems with elevated risk profiles.


## Appendix A Controls - Internet-Facing System Requirements


| Control ID | Title | Requirement | NIST | Status | Owner |
| --- | --- | --- | --- | --- | --- |
| MON05.001 (L, M, H) | Continuous External Attack Surface Monitoring | Internet-facing systems shall be enrolled in an automated attack surface monitoring service that performs daily external enumeration. Newly discovered assets or open ports not in the approved inventory shall generate a P2 alert. Tool and integration requirements are maintained by the Security Engineering team. | RA-5(11) | Partially Implemented | Security Engineering |
| MON05.002 | Penetration Testing Frequency | Internet-facing systems shall undergo penetration testing annually at minimum by a qualified independent tester. Web application penetration testing shall use OWASP methodology. Findings shall be entered as POA&M items within 5 business days per RMP03.001. Pentest reports shall be retained for 3 years. | CA-8 | Implemented | ISSO |


## Appendix B - Approved Vulnerability Scanning Tools


| Tool | Coverage | Scan Type | Owner |
| --- | --- | --- | --- |
| Tenable Nessus / Security Center | Endpoints, servers, network devices | Authenticated, credentialed | Security Ops |
| Microsoft Defender Vulnerability Mgmt | Windows endpoints, M365 services | Agent-based continuous | Endpoint Management |
| Qualys VMDR | Cloud workloads, web apps | Authenticated + external | Security Engineering |
| OWASP ZAP / Burp Suite Enterprise | Web applications | Active DAST scanning | Security Engineering |


## Appendix C - Required Log Sources

All sources below shall forward logs to the SIEM. The Security Engineering team maintains the SIEM integration runbook. For onboarding new log sources, submit a change request per CFG02.001.

• Active Directory / Entra ID - Authentication events, privilege changes, account lifecycle

• Windows Security Event Log - Logon/logoff, process creation, policy changes

• Network Firewall and IDS/IPS - Allow/deny decisions, intrusion signatures triggered

• VPN Gateway - Session establishment, authentication failures, data volume anomalies

• Email Gateway - Inbound/outbound filtering decisions, DLP policy matches

• Cloud Platform Audit Logs - Admin activity, data access, resource configuration changes

• Endpoint Detection and Response (EDR) - Process telemetry, alert events


## Appendix D - Metrics and Reporting Templates

The FISMA metrics template, ATO status brief template, and retention schedule are maintained in SharePoint under the ISSO Operations folder. For current versions, see [Monitoring Records Library (internal)](https://www.google.com).


## Appendix E - Revision History


| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| 1.4 | 02/01/2026 | Georgie George | Added CDM dashboard controls (MON04.001). Updated SIEM retention to 36-month. |
| 1.3 | 08/15/2025 | Georgie George | Added attack surface monitoring (MON05.001). Aligned to NIST SP 800-137A. |
| 1.2 | 03/01/2025 | Mator. John | Added penetration testing control (MON05.002). Updated CVSS thresholds. |
| 1.1 | 01/20/2025 | Mator. John | Initial operational release post-ATO. |
