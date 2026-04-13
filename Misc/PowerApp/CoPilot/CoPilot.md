# GCC High SharePoint + Power Automate Document Process

This note is a practical build guide for a GCC High document approval process using SharePoint Online and Power Automate.

## Current Microsoft References Used

- Power Automate US Government: https://learn.microsoft.com/en-us/power-automate/us-govt
- Power Apps US Government: https://learn.microsoft.com/en-us/power-platform/admin/powerapps-us-government
- Use SharePoint and Power Automate to build workflows: https://learn.microsoft.com/en-us/power-automate/sharepoint-overview
- Create and test an approval workflow with Power Automate: https://learn.microsoft.com/en-us/power-automate/modern-approvals
- Share a cloud flow: https://learn.microsoft.com/en-us/power-automate/create-team-flows
- Microsoft 365 GCC High endpoints: https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-u-s-government-gcc-high-endpoints?view=o365-worldwide

## GCC High Basics

- GCC High maker portal for Power Automate: https://make.high.powerautomate.us
- GCC High flow portal: https://high.flow.microsoft.us
- GCC High Power Platform admin center: https://high.admin.powerplatform.microsoft.us
- GCC High Power Apps maker portal: https://make.high.powerapps.us
- GCC High SharePoint endpoints use `*.sharepoint.us`
- GCC High identity uses Microsoft Entra Government, not commercial public Entra ID

## Before You Build

1. Confirm the tenant is actually provisioned for GCC High Power Automate and GCC High SharePoint.
2. Verify users can sign in to GCC High URLs, especially:
	- `https://make.high.powerautomate.us`
	- `https://high.flow.microsoft.us`
	- SharePoint tenant URLs ending in `.sharepoint.us`
3. Confirm network allowlists include the required GCC High Microsoft 365 and Power Platform endpoints.
4. Confirm Conditional Access policies target SharePoint and Microsoft Flow Service consistently. If policies differ, users can hit authentication failures when launching flows from SharePoint.
5. Confirm the document library owners, approvers, and service accounts are known before flow design starts.
6. Review connector usage. Third-party connectors may process data outside the government boundary, so only use connectors your compliance team approves.

## Recommended Architecture

Use this baseline pattern:

1. SharePoint document library stores the files.
2. SharePoint columns store workflow metadata.
3. Power Automate triggers on file creation or metadata change.
4. Approvals action handles human decisioning.
5. Flow writes decision, comments, dates, and approver details back to SharePoint.
6. Approved files move to an approved folder or retain a final approved status.
7. Rejected files remain visible for correction and resubmission.
8. Optional dashboard layer surfaces status for requesters, approvers, and admins.

## SharePoint Library Setup

Create a document library for incoming documents. Add metadata columns before building the flow.

Recommended columns:

- `Document ID` as single line of text
- `Document Type` as choice
- `Requestor` as person or group
- `Department` as choice or managed metadata
- `Submission Date` as date/time
- `Approval Status` as choice
  - Draft
  - Submitted
  - In Review
  - Approved
  - Rejected
  - Cancelled
- `Current Approver` as person or group
- `Approver Comments` as multiple lines of text
- `Decision Date` as date/time
- `Due Date` as date/time
- `Resubmission Required` as yes/no
- `Workflow Instance ID` as single line of text

Optional but useful:

- `Approval Level` as number
- `Final Approver` as person or group
- `Business Area` as choice
- `Sensitivity` as choice

## Folder Structure

Use a simple folder model to reduce confusion:

- `Incoming`
- `In Review`
- `Approved`
- `Rejected`
- `Archive`

If your records policy does not want physical moves, keep one library and use metadata only. That is usually easier for reporting and retention.

## Step-by-Step: Build the Flow

### Option A: Trigger on new file submission

Use this when users upload a document and that upload should immediately start review.

1. Go to `https://make.high.powerautomate.us`.
2. Select `My flows`.
3. Select `New flow` > `Automated cloud flow`.
4. Name it something explicit, such as `GCCH - Document Approval - Initial Submission`.
5. Use a SharePoint trigger such as:
	- `When a file is created (properties only)`, or
	- `When an item is created`
6. Point the trigger to the GCC High SharePoint site and the target document library.
7. Add an initialization/update step that sets:
	- `Approval Status = Submitted`
	- `Submission Date = utcNow()`
	- `Requestor` from created by if needed
8. Add any lookup logic needed to determine the approver:
	- manager lookup
	- department routing table
	- fixed approver list
9. Update the item to set:
	- `Current Approver`
	- `Approval Status = In Review`
	- `Due Date`
10. Add `Start and wait for an approval`.
11. Set approval type based on process need:
	- first to respond
	- everyone must approve
	- sequential logic if multiple levels are required
12. Build the title and details from document metadata.
13. Include a direct SharePoint link to the file in the approval details.
14. Add a condition on the approval outcome.
15. If approved:
	- update SharePoint metadata
	- stamp approver comments
	- stamp decision date
	- set `Approval Status = Approved`
	- optionally move file to `Approved`
16. If rejected:
	- update SharePoint metadata
	- stamp approver comments
	- stamp decision date
	- set `Approval Status = Rejected`
	- set `Resubmission Required = Yes`
	- optionally move file to `Rejected`
17. Send notification to the requestor.
18. Save and test with a sample file.

### Option B: Trigger only after metadata is complete

Use this when users first upload a file, then complete metadata, then explicitly submit.

1. Add a Yes/No or choice column named `Ready for Approval` or `Submission Status`.
2. Build the flow with trigger `When a file is created or modified (properties only)`.
3. Add a trigger condition or an early condition block so the flow only proceeds when:
	- required metadata is present
	- `Ready for Approval = Yes`, or
	- `Submission Status = Submitted`
4. Prevent duplicate re-runs by also checking that `Approval Status` is not already `In Review` or `Approved`.
5. Continue with the same approval pattern as Option A.

This is usually the better design for real document processes.

## Recommended Approval Logic

### Single approver

Use for low-risk documents.

### Sequential approvers

Use for controlled review chains such as:

1. Team lead
2. Compliance
3. Final authority

### Parallel approvers

Use when two groups can review at the same time and both decisions are required.

## Practical Build Details

- Keep the flow inside a solution if this is a production process.
- Prefer metadata updates over repeated file moves unless the business process truly needs folders.
- Store approval comments back into SharePoint so reporting does not depend only on run history.
- Add a unique workflow ID so rework and audit trails are easier.
- Use explicit status values and do not overload one field with multiple meanings.
- If the approval may run longer than 30 days, use the long-running approval pattern with Dataverse and split the process across two flows.
- Keep action count under control. Power Automate supports up to 500 actions in one flow definition; use child flows if the process grows.

## GCC High-Specific Cautions

- Do not assume commercial URLs will work. Use the GCC High maker and admin URLs only.
- Review DLP policies before adding non-Microsoft or HTTP connectors.
- GCC High and DoD do not support adding a SharePoint list as a co-owner of a cloud flow. Use named owners or groups instead.
- If the flow is launched from SharePoint, Conditional Access must be aligned between SharePoint and Microsoft Flow Service.
- Flow runs over 30 days time out. Design escalations and reminders accordingly.
- If using on-premises SharePoint or SQL, configure the on-premises data gateway.

## Suggested Notifications

Send these messages at minimum:

1. Submission confirmation to requester.
2. Approval request to current approver.
3. Reminder before due date.
4. Escalation after due date.
5. Final decision to requester.
6. Optional digest to admins for stuck items.

## Minimal Testing Plan

1. Submit a document with complete metadata.
2. Approve it and confirm SharePoint metadata updates correctly.
3. Reject it and confirm rejection comments are written back.
4. Verify the file link in the approval email opens the GCC High SharePoint file.
5. Test with a non-owner approver.
6. Test Conditional Access and MFA path from SharePoint into Power Automate.
7. Test overdue reminder and escalation logic.
8. Test resubmission after rejection.

## Recommended First Version

Build version 1 with this scope:

1. One document library
2. One submission trigger
3. One approver or one sequential chain
4. One approval status field
5. Approval comments written to SharePoint
6. Approved and rejected email notifications
7. Basic dashboard for requester, approver, and admin views

After that is stable, add:

1. escalation logic
2. SLA timers
3. resubmission logic
4. delegated approvers
5. reporting and dashboards

## Notes on Ownership and Support

- Use at least two named co-owners for business continuity.
- If this is production, prefer solution-aware cloud flows.
- If an owner leaves, embedded connections may fail until credentials are replaced.
- Use run-only access for users who only need to start flows, not co-ownership.

## Short Build Checklist

- SharePoint library created
- Metadata columns created
- GCC High URLs verified
- Conditional Access reviewed
- Approver routing defined
- Flow created and named clearly
- Approval action configured
- SharePoint status updates configured
- Notifications configured
- Test cases executed
- Owners and support model assigned
