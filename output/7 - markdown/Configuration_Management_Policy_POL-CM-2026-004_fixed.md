---
title: ""
source_file: "Configuration_Management_Policy_POL-CM-2026-004_fixed.docx"
modified: "2026-03-29"
doc_id: "POL-CM-2026-004"
converted: "2026-03-29T23:25:14"
PublishedURL: "https://contoso.sharepoint.com/sites/Policies/Shared Documents/Configuration_Management_Policy_POL-CM-2026-004.docx"
Acronyms: ""
---

# Configuration Management Policy

Document ID: POL-CM-2026-004 | Version: 1.5 | Last Reviewed: February 28, 2026 | Classification: FOUO


# Policy Purpose

This document establishes the configuration management requirements for all information systems and network devices operated by the organization. Configuration management ensures that systems remain in a known, secure state throughout their lifecycle.


# Policy Scope

This policy applies to all servers, workstations, network devices, cloud instances, and mobile devices. Refer to Section 4 of the Asset Management Policy for the complete asset inventory that defines the systems in scope.


# Risk Context and Intent

Configuration drift is one of the leading causes of security incidents in federal environments. The intent of this policy is to prevent unauthorized configuration changes that could introduce vulnerabilities or disrupt operations. As described in the Risk Management Policy, all systems must maintain a documented security baseline.


# Section 2: Controls

The following controls establish the configuration management requirements. Controls are organized by function.

![Picture 1](Configuration_Management_Policy_POL-CM-2026-004_fixed_images/image_1.png)


# 2.1 Baseline Configuration Controls


| Control ID | Title | Description | NIST Mapping | Implementation Status | Responsible Party |
| --- | --- | --- | --- | --- | --- |
| CFG01.001 | Security Baseline Development | The organization shall develop and maintain security configuration baselines for all system types (servers, workstations, network devices) based on CIS Benchmarks or DISA STIGs. | CM-2 | Implemented | Security Engineering |
| CFG01.002 | Baseline Review Cycle | Configuration baselines shall be reviewed and updated at least annually or when significant changes occur to the threat landscape. See the Continuous Monitoring Policy for threat assessment frequency. | CM-2(1) | Implemented | Security Engineering |
| CFG2.001 | Change Control Process | All configuration changes shall be submitted through the change advisory board (CAB) process. Emergency changes require post-implementation review within 48 hours. | CM-3 | Implemented | Change Management |
| CFG02.002 | Change Impact Analysis | Configuration changes shall include a documented security impact analysis prior to approval. Refer to Section 4 of this document for the impact analysis template. | CM-4 | Partially Implemented | Security Engineering |


# 2.2 Configuration Monitoring Controls


| Control ID | Title | Description | NIST Mapping | Implementation Status | Responsible Party |
| --- | --- | --- | --- | --- | --- |
| CFG03.001 | Automated Configuration Scanning | Systems shall be scanned for configuration compliance at least weekly using automated tools. Non-compliant systems shall be flagged for remediation. | CM-6 | Implemented | Security Operations |
| CFG03.002 | Configuration Drift Detection | The organization shall deploy automated drift detection that alerts when system configurations deviate from the approved baseline. | CM-3(5) | Not Implemented | Security Operations |
| CFG04.001 | Software Inventory Management | The organization shall maintain an automated inventory of all installed software. Unauthorized software shall be removed within 72 hours of detection. | CM-7 | Partially Implemented | Endpoint Management |
| CFG04.002 | Application Whitelisting | Critical systems shall implement application whitelisting to prevent execution of unauthorized software. As previously stated, unauthorized software must be removed within 72 hours. | CM-7(5) | Not Implemented | Endpoint Management |


# Section 3: Roles and Responsibilities


| Role | Responsibilities |
| --- | --- |
| CISO | Approves configuration baselines. Authorizes exceptions. Reviews compliance reports quarterly. |
| Security Engineering | Develops and maintains baselines. Conducts security impact analyses. Refer to Section 2.1 for baseline development controls. |
| Change Management | Operates the CAB. Documents change requests. Tracks implementation status. |
| Security Operations | Executes configuration scans. Reports drift. Coordinates remediation with system owners. |
| System Owners | Maintain system compliance with baselines. Submit change requests. Respond to scan findings within SLA. |


# Section 4: Change Impact Analysis Template

All configuration changes must complete the following analysis before CAB submission:


| Analysis Element | Required Information |
| --- | --- |
| Change Description | Detailed technical description of the proposed change. |
| Systems Affected | List all systems, applications, and network segments impacted. |
| Security Impact | Assessment of how the change affects the security posture. Does it alter the baseline? Does it introduce new ports, protocols, or services? |
| Rollback Plan | Documented procedure to reverse the change if issues arise. |
| Testing Results | Evidence from test/staging environment. See the System Development Policy, Section 6 for testing requirements. |


# Appendix - Framework Crosswalk


| Org Control ID | NIST 800-53 | CIS Control | FedRAMP Baseline |
| --- | --- | --- | --- |
| CFG01.001 | CM-2 | CIS 4.1 | CM-2 (Moderate) |
| CFG01.002 | CM-2(1) | CIS 4.2 | CM-2(1) (Moderate) |
| CFG02.001 | CM-3 | CIS 4.8 | CM-3 (Moderate) |
| CFG02.002 | CM-4 | CIS 4.8 | CM-4 (Moderate) |
| CFG03.001 | CM-6 | CIS 4.1 | CM-6 (Moderate) |
| CFG03.002 | CM-3(5) | CIS 4.3 | CM-3(5) (High) |
| CFG04.001 | CM-7 | CIS 2.1 | CM-7 (Moderate) |
| CFG04.002 | CM-7(5) | CIS 2.6 | CM-7(5) (High) |
