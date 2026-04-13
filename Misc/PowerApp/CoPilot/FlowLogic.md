# Power Automate Flow Logic — Action-by-Action Implementation Guide

Implementation guide for the four Power Automate flows in the **InfoSec Policy Document Library** project.
Flows are **notification-only** — no "Start and wait for approval." The Power Apps dashboard is the
approval interface. Use alongside Claude.md (lifecycle + columns) and VisualDash.md (dashboard formulas).

## References

- Expression function reference: https://learn.microsoft.com/en-us/azure/logic-apps/workflow-definition-language-functions-reference
- SharePoint connector triggers/actions: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/sharepoint-connector-actions-triggers
- Approvals markdown support: https://learn.microsoft.com/en-us/power-automate/approvals-markdown-support
- SharePoint REST via flow: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/working-with-send-sp-http-request
- Conditions and expressions: https://learn.microsoft.com/en-us/power-automate/use-expressions-in-conditions

---

## Architecture Summary

| Flow | Trigger | Purpose | Phase |
|---|---|---|---|
| Flow 1 | Document Status → "Submitted for Stage 1 Approval" | Notification email to Stage 1 Reviewer + stamp metadata | 3b |
| Flow 2 | Document Status → "Submitted for Stage 2 Approval" | Notification email to Stage 2 Final Approver + stamp metadata | 3c |
| Flow 3 | LLM Ingest Ready → "Yes" | Copy file to LLM Corpus library | 3d |
| Flow 4 | Recurrence (weekly) | Reminder emails for upcoming review due dates | 3e |

**Key architecture decision:** Flows 1 and 2 do NOT use "Start and wait for an approval." They send a notification email and exit. Approval/rejection happens in the Power Apps Approvals Queue dashboard via `Patch()`. This avoids the 30-day flow timeout and keeps audit trail in SharePoint columns.

---

## Pre-Build Setup

### Create the flows inside a solution

Go to `https://make.gov.powerautomate.us`, select **Solutions**, then create or open a solution.

Suggested solution name:
```
GCC-InfoSec-PolicyWorkflows
```

Creating flows inside a solution makes them portable, allows environment variables, and separates them from personal flows.

### Naming convention

```
InfoSec - Flow 1 - Stage 1 Notification v1
InfoSec - Flow 2 - Stage 2 Notification v1
InfoSec - Flow 3 - LLM Corpus Copy v1
InfoSec - Flow 4 - Weekly Review Reminders v1
```

### Common configuration

All flows that use the SharePoint connector share these values:

| Field | Value |
|---|---|
| Site Address | `https://yourtenant.sharepoint.us/sites/InfoSecPolicies` |
| Library Name | `InfoSec Policy Documents` |

Replace the site URL with your actual GCC SharePoint site. The domain must be `.sharepoint.us` (GCC), not `.sharepoint.com`.

### Document library action note

For document libraries, use **`Update file properties`** (not `Update item`). `Update item` is for lists. `Update file properties` is the correct action for libraries and maps to the `PatchFileItem` operation.

---

## Flow Dedup Pattern (Used by Flow 1 and Flow 2)

Both formal notification flows use this guard to prevent infinite trigger loops. When the flow updates SharePoint columns (e.g., `Last Submitted Date`), the trigger fires again. The dedup lock prevents reprocessing.

```
Trigger: When a file is created or modified (properties only)
  └─ Condition: DocumentStatus = "[target]" AND WorkflowRunID is empty
      ├─ TRUE:
      │   1. Update file properties: set WorkflowRunID = guid()  ← FIRST action
      │   2. Proceed with notification logic
      │   3. At end of EVERY branch: set WorkflowRunID = ""  ← clear the lock
      └─ FALSE:
          └─ Terminate (Cancelled) — do nothing
```

**Trigger condition (add in trigger settings → gear icon → Trigger conditions):**

Flow 1:
```
@and(equals(triggerOutputs()?['body/Document_x0020_Status/Value'], 'Submitted for Stage 1 Approval'), empty(triggerOutputs()?['body/WorkflowRunID']))
```

Flow 2:
```
@and(equals(triggerOutputs()?['body/Document_x0020_Status/Value'], 'Submitted for Stage 2 Approval'), empty(triggerOutputs()?['body/WorkflowRunID']))
```

Adding trigger conditions prevents unnecessary flow runs and saves against the daily run quota. The Condition action inside the flow is a backup guard if trigger conditions are not supported in your environment.

**Trigger concurrency:** Set to `1` in trigger settings (Concurrency Control → On → Degree of Parallelism = 1). This prevents parallel runs on the same document update.

---

## Flow 1: Stage 1 Approval Notification (Phase 3b)

**Purpose:** When a document enters "Submitted for Stage 1 Approval," send a notification email to the Stage 1 Reviewer, stamp metadata, and exit. Reviewers act in the Power Apps dashboard.

---

### Action 1: Trigger — When a file is created or modified (properties only)

**Connector:** SharePoint

| Field | Value |
|---|---|
| Site Address | `https://yourtenant.sharepoint.us/sites/InfoSecPolicies` |
| Library Name | `InfoSec Policy Documents` |

**Trigger condition (gear icon → Trigger conditions → + Add):**
```
@and(equals(triggerOutputs()?['body/Document_x0020_Status/Value'], 'Submitted for Stage 1 Approval'), empty(triggerOutputs()?['body/WorkflowRunID']))
```

**Concurrency control:** On → Degree of Parallelism = 1

---

### Action 2: Condition — Dedup guard

**Name:** `Dedup Guard`

Even with the trigger condition, add this as a safety net:

| Left value | Operator | Right value |
|---|---|---|
| `triggerOutputs()?['body/Document_x0020_Status/Value']` | is equal to | `Submitted for Stage 1 Approval` |

AND

| Left value | Operator | Right value |
|---|---|---|
| `triggerOutputs()?['body/WorkflowRunID']` | is equal to | _(leave blank — checks for empty)_ |

**False branch → Terminate:**

| Field | Value |
|---|---|
| Status | Cancelled |
| Code | `DEDUP_SKIP` |
| Message | `Flow already running or status mismatch. Skipping.` |

---

### Action 3 (True branch): Update file properties — Set dedup lock

**Connector:** SharePoint  
**Action:** `Update file properties`  
**Name:** `Set Dedup Lock`

| Field | Value |
|---|---|
| Site Address | Site URL |
| Library Name | `InfoSec Policy Documents` |
| Id | `triggerOutputs()?['body/ID']` |
| Workflow Run ID | `@{guid()}` |
| Last Submitted Date | `@{formatDateTime(utcNow(), 'yyyy-MM-dd')}` |

This writes the dedup lock **first** and stamps the submission date.

---

### Action 4: Get user profile — Policy Owner

**Connector:** Office 365 Users  
**Action:** `Get user profile (V2)`  
**Name:** `Get Policy Owner Profile`

| Field | Value |
|---|---|
| User (UPN) | `triggerOutputs()?['body/PolicyOwner/Email']` |

Resolves the Policy Owner's full name and email for the notification.

---

### Action 5: Compose — Build email body

**Action:** Compose  
**Name:** `Build Stage 1 Notification Body`

Use HTML for formatting:

```html
<h2>InfoSec Policy — Stage 1 Review Required</h2>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
  <tr><td><b>Policy Number</b></td><td>@{triggerOutputs()?['body/PolicyNumber']}</td></tr>
  <tr><td><b>Title</b></td><td>@{triggerOutputs()?['body/Title']}</td></tr>
  <tr><td><b>Category</b></td><td>@{triggerOutputs()?['body/Category/Value']}</td></tr>
  <tr><td><b>Classification</b></td><td>@{triggerOutputs()?['body/Classification/Value']}</td></tr>
  <tr><td><b>Policy Owner</b></td><td>@{outputs('Get_Policy_Owner_Profile')?['body/displayName']}</td></tr>
  <tr><td><b>Regulatory Reference</b></td><td>@{triggerOutputs()?['body/RegulatoryReference']}</td></tr>
  <tr><td><b>Submitted</b></td><td>@{convertTimeZone(utcNow(), 'UTC', 'Eastern Standard Time', 'MMMM d, yyyy h:mm tt')}</td></tr>
</table>
<br/>
<p>This policy has been submitted for <b>Stage 1 SME review</b>.</p>
<p>Please review in the <b>InfoSec Policy Dashboard</b> and use the Approve or Send Back buttons.</p>
<p><a href="https://yourtenant.sharepoint.us/sites/InfoSecPolicies/@{triggerOutputs()?['body/{FileDirRef}']}/@{triggerOutputs()?['body/FileLeafRef']}">Open Document in SharePoint</a></p>
```

---

### Action 6: Condition — Stage 1 Reviewer assigned?

Check whether the `Stage 1 Reviewer` Person column has a value. If yes, send to that person. If no, send to the InfoSec Policy Admins group or a default alias.

| Left value | Operator | Right value |
|---|---|---|
| `triggerOutputs()?['body/Stage_x0020_1_x0020_Reviewer/Email']` | is not equal to | _(leave blank)_ |

**True branch:** Send to the assigned Stage 1 Reviewer.  
**False branch:** Send to a default alias (e.g., `infosec-admins@youragency.gov`).

---

### Action 7 (True): Send email — To Stage 1 Reviewer

**Connector:** Office 365 Outlook  
**Action:** `Send an email (V2)`  
**Name:** `Email Stage 1 Reviewer`

| Field | Value |
|---|---|
| To | `triggerOutputs()?['body/Stage_x0020_1_x0020_Reviewer/Email']` |
| Subject | `Stage 1 Review Required: @{triggerOutputs()?['body/PolicyNumber']} — @{triggerOutputs()?['body/Title']}` |
| Body | `@{outputs('Build_Stage_1_Notification_Body')}` |
| Is HTML | Yes |

---

### Action 7b (False): Send email — To default admin alias

Same as Action 7 but:

| Field | Value |
|---|---|
| To | `infosec-admins@youragency.gov` |
| Subject | `Stage 1 Review Required (no reviewer assigned): @{triggerOutputs()?['body/PolicyNumber']}` |

---

### Action 8: Update file properties — Clear dedup lock

**Connector:** SharePoint  
**Action:** `Update file properties`  
**Name:** `Clear Dedup Lock`

This action must run at the end of **every** branch (True and False):

| Field | Value |
|---|---|
| Site Address | Site URL |
| Library Name | `InfoSec Policy Documents` |
| Id | `triggerOutputs()?['body/ID']` |
| Workflow Run ID | _(set to empty string — clear the field)_ |

**Important:** To set a text column to empty in Power Automate, type a single space then delete it, or use the expression `''` (two single quotes). Some versions of the designer require you to use the expression editor to explicitly pass an empty string.

---

### Error Handling for Flow 1

Wrap Actions 3 through 8 in a **Scope** named `Stage 1 Notification Scope`.

After the scope, add an error handler with **Run after** set to `has failed`:

**Action:** Send an email (V2)  
**Name:** `Error Handler - Stage 1`

| Field | Value |
|---|---|
| To | `infosec-admins@youragency.gov` |
| Subject | `FLOW ERROR: Stage 1 Notification — @{triggerOutputs()?['body/PolicyNumber']}` |
| Body | See below |

```html
<p>An error occurred in the Stage 1 notification flow.</p>
<p><b>Policy:</b> @{triggerOutputs()?['body/PolicyNumber']} — @{triggerOutputs()?['body/Title']}</p>
<p><b>Error:</b> @{result('Stage_1_Notification_Scope')?[0]?['error']?['message']}</p>
<p><b>Flow Run:</b> @{workflow()['run']['name']}</p>
<p><b>Flow:</b> @{workflow()?['tags']['flowDisplayName']}</p>
```

After the error handler, add another `Update file properties` to clear the WorkflowRunID even on failure:

| Field | Value |
|---|---|
| Id | `triggerOutputs()?['body/ID']` |
| Workflow Run ID | `''` |

Set this action's **Run after** to: `has failed`, `has timed out`, `is skipped`.

---

## Flow 2: Stage 2 Final Approval Notification (Phase 3c)

**Purpose:** When a document enters "Submitted for Stage 2 Approval," send a notification email to the Stage 2 Final Approver and exit. The approver acts in the Power Apps dashboard.

Flow 2 follows the same structure as Flow 1 with these differences:

---

### Action 1: Trigger

Same connector and library. Different trigger condition:

```
@and(equals(triggerOutputs()?['body/Document_x0020_Status/Value'], 'Submitted for Stage 2 Approval'), empty(triggerOutputs()?['body/WorkflowRunID']))
```

---

### Action 2: Dedup Guard

Same pattern — check for `Submitted for Stage 2 Approval` and empty `WorkflowRunID`.

---

### Action 3: Set Dedup Lock + Stamp Metadata

**Action:** `Update file properties`

| Field | Value |
|---|---|
| Id | `triggerOutputs()?['body/ID']` |
| Workflow Run ID | `@{guid()}` |
| Last Submitted Date | `@{formatDateTime(utcNow(), 'yyyy-MM-dd')}` |

---

### Action 4: Get Policy Owner Profile

Same as Flow 1 — resolve `PolicyOwner/Email`.

---

### Action 5: Compose — Build Stage 2 email body

```html
<h2>InfoSec Policy — Final Approval Required</h2>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
  <tr><td><b>Policy Number</b></td><td>@{triggerOutputs()?['body/PolicyNumber']}</td></tr>
  <tr><td><b>Title</b></td><td>@{triggerOutputs()?['body/Title']}</td></tr>
  <tr><td><b>Category</b></td><td>@{triggerOutputs()?['body/Category/Value']}</td></tr>
  <tr><td><b>Sub-Category</b></td><td>@{triggerOutputs()?['body/Sub_x002d_Category/Value']}</td></tr>
  <tr><td><b>Classification</b></td><td>@{triggerOutputs()?['body/Classification/Value']}</td></tr>
  <tr><td><b>Policy Owner</b></td><td>@{outputs('Get_Policy_Owner_Profile')?['body/displayName']}</td></tr>
  <tr><td><b>Regulatory Reference</b></td><td>@{triggerOutputs()?['body/RegulatoryReference']}</td></tr>
  <tr><td><b>Stage 1 Decision</b></td><td>@{triggerOutputs()?['body/Stage1Decision/Value']}</td></tr>
  <tr><td><b>Stage 1 Comments</b></td><td>@{triggerOutputs()?['body/Stage1Comments']}</td></tr>
  <tr><td><b>Submitted</b></td><td>@{convertTimeZone(utcNow(), 'UTC', 'Eastern Standard Time', 'MMMM d, yyyy h:mm tt')}</td></tr>
</table>
<br/>
<p>This policy has passed Stage 1 SME review and requires your <b>final approval</b> to publish.</p>
<p>Please review in the <b>InfoSec Policy Dashboard — Approvals Queue</b> and use the Approve or Send Back buttons.</p>
<p><a href="https://yourtenant.sharepoint.us/sites/InfoSecPolicies/@{triggerOutputs()?['body/{FileDirRef}']}/@{triggerOutputs()?['body/FileLeafRef']}">Open Document in SharePoint</a></p>
```

---

### Action 6: Send email — To Stage 2 Final Approver

**Connector:** Office 365 Outlook

| Field | Value |
|---|---|
| To | `triggerOutputs()?['body/Stage_x0020_2_x0020_Final_x0020_Approver/Email']` |
| Subject | `FINAL APPROVAL REQUIRED: @{triggerOutputs()?['body/PolicyNumber']} — @{triggerOutputs()?['body/Title']}` |
| Body | `@{outputs('Build_Stage_2_Notification_Body')}` |
| Is HTML | Yes |

**Note:** Stage 2 Final Approver is a required Person column, so no fallback branch is needed (unlike Flow 1's optional Stage 1 Reviewer).

---

### Action 7: Clear Dedup Lock

Same pattern — update `WorkflowRunID` to empty.

---

### Error Handling for Flow 2

Same Scope + error handler pattern as Flow 1. Change the subject to `FLOW ERROR: Stage 2 Notification`.

---

## Flow 3: LLM Corpus Copy (Phase 3d)

**Purpose:** When `LLM Ingest Ready` is set to "Yes" on an Approved/Published document, copy the file to the **InfoSec Policy LLM Corpus** library and stamp the ingest date.

---

### Action 1: Trigger

**Connector:** SharePoint  
**Action:** `When a file is created or modified (properties only)`

Same site and library. Trigger condition:

```
@and(equals(triggerOutputs()?['body/LLMIngestReady/Value'], 'Yes'), empty(triggerOutputs()?['body/LLMIngestDate']))
```

This fires only when `LLM Ingest Ready = Yes` AND `LLM Ingest Date` is empty (prevents re-copy).

---

### Action 2: Condition — PDF Converted check

**Name:** `Check PDF Converted`

| Left value | Operator | Right value |
|---|---|---|
| `triggerOutputs()?['body/PDFConverted/Value']` | is equal to | `Yes` |

---

### Action 3 (True branch): Copy file to LLM Corpus

**Connector:** SharePoint  
**Action:** `Copy file`

| Field | Value |
|---|---|
| Current Site Address | `https://yourtenant.sharepoint.us/sites/InfoSecPolicies` |
| File to Copy | `triggerOutputs()?['body/{Identifier}']` |
| Destination Site Address | `https://yourtenant.sharepoint.us/sites/InfoSecPolicies` |
| Destination Folder | `/InfoSec Policy LLM Corpus` |
| If another file is already there | Replace |

**Returns:** `ItemId`, `Id`, `Name`, `Path` of the copied file.

---

### Action 4 (True branch): Update file properties — Stamp ingest date

**Connector:** SharePoint

| Field | Value |
|---|---|
| Site Address | Site URL |
| Library Name | `InfoSec Policy Documents` |
| Id | `triggerOutputs()?['body/ID']` |
| LLM Ingest Date | `@{formatDateTime(utcNow(), 'yyyy-MM-dd')}` |

---

### Action 5 (True branch): Send confirmation email

**Connector:** Office 365 Outlook

| Field | Value |
|---|---|
| To | `triggerOutputs()?['body/PolicyOwner/Email']` |
| Subject | `LLM Corpus Updated: @{triggerOutputs()?['body/PolicyNumber']} — @{triggerOutputs()?['body/Title']}` |
| Body | See below |

```html
<p>The following policy has been copied to the LLM Corpus library:</p>
<p><b>Policy:</b> @{triggerOutputs()?['body/PolicyNumber']} — @{triggerOutputs()?['body/Title']}</p>
<p><b>Ingest Date:</b> @{convertTimeZone(utcNow(), 'UTC', 'Eastern Standard Time', 'MMMM d, yyyy')}</p>
<p>No further action is required.</p>
```

---

### Action 6 (False branch): Send warning email — PDF not ready

When `LLM Ingest Ready = Yes` but `PDF Converted ≠ Yes`, the flow does NOT copy. It sends a warning to the Policy Owner instead. The `LLM Ingest Ready` flag remains "Yes" so the flow retriggers correctly once PDF is marked done.

**Connector:** Office 365 Outlook

| Field | Value |
|---|---|
| To | `triggerOutputs()?['body/PolicyOwner/Email']` |
| Subject | `ACTION REQUIRED: PDF must be converted before LLM ingest — @{triggerOutputs()?['body/PolicyNumber']}` |
| Body | See below |

```html
<p>You marked <b>@{triggerOutputs()?['body/PolicyNumber']} — @{triggerOutputs()?['body/Title']}</b> as LLM Ingest Ready, but the PDF has not been converted yet.</p>
<p><b>Current PDF status:</b> @{triggerOutputs()?['body/PDFConverted/Value']}</p>
<p>Please convert the document to PDF, then mark <b>PDF Converted = Yes</b> in the InfoSec Policy Dashboard. The LLM ingest will process automatically once the PDF is ready.</p>
```

**Note:** Do NOT set `LLM Ingest Ready` back to "No" or clear it. Leaving it as "Yes" ensures the flow retriggers when `PDF Converted` changes to "Yes" (because the file properties change fires the trigger again, and this time the PDF check passes).

---

### Error Handling for Flow 3

Wrap Actions 3-5 inside a Scope. Error handler sends to admin alias with file details.

---

## Flow 4: Weekly Review Due Reminders (Phase 3e)

**Purpose:** Once per week, find all Approved/Published policies with `Review Due Date` in the next 90 days and send reminder emails to their Policy Owners.

---

### Action 1: Trigger — Recurrence

**Connector:** Schedule

| Field | Value |
|---|---|
| Frequency | Week |
| Interval | 1 |
| On these days | Monday |
| At these hours | 8 |
| Time zone | Eastern Standard Time |

---

### Action 2: Get files — Upcoming reviews

**Connector:** SharePoint  
**Action:** `Get files (properties only)`

| Field | Value |
|---|---|
| Site Address | Site URL |
| Library Name | `InfoSec Policy Documents` |
| Filter Query | `Document_x0020_Status eq 'Approved/Published' and Review_x0020_Due_x0020_Date le '@{addDays(utcNow(), 90, 'yyyy-MM-dd')}' and Review_x0020_Due_x0020_Date ge '@{formatDateTime(utcNow(), 'yyyy-MM-dd')}'` |

**OData filter breakdown:**
- `Document_x0020_Status eq 'Approved/Published'` — only published policies
- `Review_x0020_Due_x0020_Date le '@{addDays(utcNow(), 90, 'yyyy-MM-dd')}'` — due within 90 days
- `Review_x0020_Due_x0020_Date ge '@{formatDateTime(utcNow(), 'yyyy-MM-dd')}'` — not already overdue (separate logic below)

**Note:** Internal column names with spaces use `_x0020_` encoding. Verify exact internal names from your library's column settings URL or a test flow run.

---

### Action 3: Get files — Overdue reviews

**Action:** `Get files (properties only)`

| Field | Value |
|---|---|
| Filter Query | `Document_x0020_Status eq 'Approved/Published' and Review_x0020_Due_x0020_Date lt '@{formatDateTime(utcNow(), 'yyyy-MM-dd')}'` |

---

### Action 4: Apply to each — Upcoming reminders

Loop over the results from Action 2.

Inside the loop:

#### 4a: Send email — Upcoming review reminder

| Field | Value |
|---|---|
| To | `items('Apply_to_each')?['PolicyOwner/Email']` |
| Subject | `Policy Review Coming Due: @{items('Apply_to_each')?['PolicyNumber']} — @{items('Apply_to_each')?['Title']}` |
| Body | See below |

```html
<p>The following policy is due for review within the next 90 days:</p>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
  <tr><td><b>Policy Number</b></td><td>@{items('Apply_to_each')?['PolicyNumber']}</td></tr>
  <tr><td><b>Title</b></td><td>@{items('Apply_to_each')?['Title']}</td></tr>
  <tr><td><b>Review Due Date</b></td><td>@{formatDateTime(items('Apply_to_each')?['Review_x0020_Due_x0020_Date'], 'MMMM d, yyyy')}</td></tr>
  <tr><td><b>Last Approval Date</b></td><td>@{formatDateTime(items('Apply_to_each')?['LastApprovalDate'], 'MMMM d, yyyy')}</td></tr>
  <tr><td><b>Effective Date</b></td><td>@{formatDateTime(items('Apply_to_each')?['EffectiveDate'], 'MMMM d, yyyy')}</td></tr>
</table>
<br/>
<p>Please begin the review process. When ready, check out the document, make revisions, check it back in, and update the status to <b>Draft</b> in the InfoSec Policy Dashboard.</p>
```

---

### Action 5: Apply to each — Overdue reminders

Loop over the results from Action 3.

#### 5a: Send email — Overdue review warning

| Field | Value |
|---|---|
| To | `items('Apply_to_each_-_Overdue')?['PolicyOwner/Email']` |
| CC | `infosec-admins@youragency.gov` |
| Subject | `⚠ OVERDUE Policy Review: @{items('Apply_to_each_-_Overdue')?['PolicyNumber']} — @{items('Apply_to_each_-_Overdue')?['Title']}` |
| Importance | High |
| Body | See below |

```html
<p style="color:red;"><b>This policy review is overdue.</b></p>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
  <tr><td><b>Policy Number</b></td><td>@{items('Apply_to_each_-_Overdue')?['PolicyNumber']}</td></tr>
  <tr><td><b>Title</b></td><td>@{items('Apply_to_each_-_Overdue')?['Title']}</td></tr>
  <tr><td><b>Review Due Date</b></td><td>@{formatDateTime(items('Apply_to_each_-_Overdue')?['Review_x0020_Due_x0020_Date'], 'MMMM d, yyyy')}</td></tr>
  <tr><td><b>Days Overdue</b></td><td>@{div(sub(ticks(utcNow()), ticks(items('Apply_to_each_-_Overdue')?['Review_x0020_Due_x0020_Date'])), 864000000000)}</td></tr>
</table>
<br/>
<p>Please begin the review process immediately.</p>
```

**Days Overdue calculation:** `div(sub(ticks(utcNow()), ticks(ReviewDueDate)), 864000000000)` converts the tick difference to days (1 day = 864,000,000,000 ticks).

---

## Version Label Flow (Bonus — triggered on check-in)

**Purpose:** Auto-populate the `Version Label` column with SharePoint's built-in version string on every file check-in.

**Trigger:** `When a file is created or modified (properties only)` (same library, no filter — fires on every change)

**Logic:**

### Action 1: Get file metadata

**Action:** `Get file metadata`

| Field | Value |
|---|---|
| Site Address | Site URL |
| File Identifier | `triggerOutputs()?['body/{Identifier}']` |

### Action 2: Condition — Version changed?

Compare the current `Version Label` column value to `_UIVersionString`:

| Left value | Operator | Right value |
|---|---|---|
| `triggerOutputs()?['body/VersionLabel']` | is not equal to | `triggerOutputs()?['body/{VersionNumber}']` |

### Action 3 (True): Update file properties

| Field | Value |
|---|---|
| Id | `triggerOutputs()?['body/ID']` |
| Version Label | `triggerOutputs()?['body/{VersionNumber}']` |

**Dedup note:** This flow writes to `Version Label` which triggers the flow again, but the condition in Action 2 will be False on the re-trigger (label already matches), so it terminates cleanly. No GUID-based dedup needed for this flow.

---

## Check-In / Check-Out Interaction

The library has `Require Check Out = Yes`. This affects flows that update file properties:

**Scenario 1 — Normal workflow (no issue):**
1. User checks out → edits document → checks in
2. User changes `Document Status` in Power Apps dashboard (Patch)
3. The Patch creates a new minor version (auto check-in/check-out by SharePoint)
4. Flow triggers on the status change
5. Flow updates additional metadata (e.g., `Last Submitted Date`, `WorkflowRunID`)
6. This creates another minor version — no conflict because the user's checkout is already complete

**Scenario 2 — File is checked out during flow run:**
If somebody has the file checked out when the flow tries to update file properties, the update **fails**.

**Mitigation:** Wrap `Update file properties` actions in the Scope error handler. On failure, the error handler email tells the admin: "Flow could not update [PolicyNumber] — file is currently checked out."

---

## Key Expressions Reference

### Date and time

| Purpose | Expression |
|---|---|
| Current UTC timestamp | `utcNow()` |
| Current date formatted | `formatDateTime(utcNow(), 'yyyy-MM-dd')` |
| Add 90 days to now | `addDays(utcNow(), 90, 'yyyy-MM-dd')` |
| Add 1 year to date | `addDays(triggerOutputs()?['body/EffectiveDate'], 365, 'yyyy-MM-dd')` |
| Format a SP date column | `formatDateTime(triggerOutputs()?['body/EffectiveDate'], 'MMMM d, yyyy')` |
| Convert to Eastern Time | `convertTimeZone(utcNow(), 'UTC', 'Eastern Standard Time', 'MMM d, yyyy h:mm tt')` |
| Subtract 1 day | `subtractFromTime(utcNow(), 1, 'Day')` |
| Days between two dates | `div(sub(ticks(utcNow()), ticks(triggerOutputs()?['body/EffectiveDate'])), 864000000000)` |

### String operations

| Purpose | Expression |
|---|---|
| Combine policy number + title | `concat(triggerOutputs()?['body/PolicyNumber'], ' — ', triggerOutputs()?['body/Title'])` |
| Trim whitespace | `trim(triggerOutputs()?['body/Title'])` |
| Generate unique ID | `guid()` |

### Logical / conditional

| Purpose | Expression |
|---|---|
| Check Document Status | `equals(triggerOutputs()?['body/Document_x0020_Status/Value'], 'Submitted for Stage 1 Approval')` |
| Check field is empty | `empty(triggerOutputs()?['body/WorkflowRunID'])` |
| Check field is not empty | `not(empty(triggerOutputs()?['body/PolicyNumber']))` |
| Combined dedup check | `and(equals(triggerOutputs()?['body/Document_x0020_Status/Value'], 'Submitted for Stage 1 Approval'), empty(triggerOutputs()?['body/WorkflowRunID']))` |
| Check date is overdue | `less(triggerOutputs()?['body/Review_x0020_Due_x0020_Date'], utcNow())` |
| Ternary-style | `if(empty(triggerOutputs()?['body/Stage_x0020_1_x0020_Reviewer/Email']), 'infosec-admins@youragency.gov', triggerOutputs()?['body/Stage_x0020_1_x0020_Reviewer/Email'])` |

### Flow runtime

| Purpose | Expression |
|---|---|
| Flow run name (for logging) | `workflow()['run']['name']` |
| Flow display name | `workflow()['tags']['flowDisplayName']` |

---

## Dynamic Content Reference — SharePoint Trigger

Fields available from the `When a file is created or modified (properties only)` trigger on the **InfoSec Policy Documents** library.

**Access pattern:** `triggerOutputs()?['body/INTERNAL_NAME']`

### Core fields

| Internal Name | Display Name | Type | Notes |
|---|---|---|---|
| `ID` | Item ID | Integer | Use for Update file properties |
| `FileLeafRef` | File name with extension | Text | |
| `{FileDirRef}` | Folder path | Text | Server-relative path to folder |
| `{Identifier}` | File identifier | Text | Use for Copy file, Get file content |
| `{VersionNumber}` | Version number | Text | SharePoint's built-in version string |
| `Title` | Title | Text | |
| `Author/Email` | Created by (email) | Text | |
| `Editor/Email` | Modified by (email) | Text | |
| `Created` | Created date | DateTime | ISO 8601 |
| `Modified` | Modified date | DateTime | ISO 8601 |

### InfoSec project columns

| Internal Name | Display Name | Type | Access Pattern |
|---|---|---|---|
| `Document_x0020_Status` | Document Status | Choice | Append `/Value` for text |
| `WorkflowRunID` | Workflow Run ID | Text | Direct |
| `PolicyNumber` | Policy Number | Text | Direct |
| `PolicyOwner` | Policy Owner | Person | Append `/Email` or `/DisplayName` |
| `Category` | Category | Choice | Append `/Value` |
| `Sub_x002d_Category` | Sub-Category | Choice | Append `/Value` |
| `Department` | Department | Choice | Append `/Value` |
| `Classification` | Classification | Choice | Append `/Value` |
| `RegulatoryReference` | Regulatory Reference | Text | Direct |
| `Stage_x0020_1_x0020_Reviewer` | Stage 1 Reviewer | Person | Append `/Email` or `/DisplayName` |
| `Stage_x0020_2_x0020_Final_x0020_Approver` | Stage 2 Final Approver | Person | Append `/Email` or `/DisplayName` |
| `Stage1Decision` | Stage 1 Decision | Choice | Append `/Value` |
| `Stage1DecisionDate` | Stage 1 Decision Date | Date | Direct |
| `Stage1Comments` | Stage 1 Comments | Text | Direct |
| `Stage2Decision` | Stage 2 Decision | Choice | Append `/Value` |
| `Stage2DecisionDate` | Stage 2 Decision Date | Date | Direct |
| `Stage2Comments` | Stage 2 Comments | Text | Direct |
| `PDFConverted` | PDF Converted | Choice | Append `/Value` |
| `PDFConversionDate` | PDF Conversion Date | Date | Direct |
| `LLMIngestReady` | LLM Ingest Ready | Choice | Append `/Value` |
| `LLMIngestDate` | LLM Ingest Date | Date | Direct |
| `LastSubmittedDate` | Last Submitted Date | Date | Direct |
| `EffectiveDate` | Effective Date | Date | Direct |
| `Review_x0020_Due_x0020_Date` | Review Due Date | Date | Direct |
| `LastRevisionDate` | Last Revision Date | Date | Direct |
| `LastApprovalDate` | Last Approval Date | Date | Direct |
| `VersionLabel` | Version Label | Text | Direct |
| `Notes` | Notes | Multi-line text | Direct |

**Important:** Internal names with spaces use `_x0020_` encoding. Names with hyphens use `_x002d_`. Short single-word names have no encoding. **Verify** the exact internal names in your library — they are set when the column is first created and cannot be changed. Check by going to Library Settings → click the column name → look at the `Field=` parameter in the URL.

---

## OData Filter Query Reference

OData filters are used in `Get files (properties only)` actions and trigger conditions.

| Purpose | OData Filter |
|---|---|
| Stage 1 pending | `Document_x0020_Status eq 'Submitted for Stage 1 Approval'` |
| Stage 2 pending | `Document_x0020_Status eq 'Submitted for Stage 2 Approval'` |
| All published | `Document_x0020_Status eq 'Approved/Published'` |
| Published + review due in 90 days | `Document_x0020_Status eq 'Approved/Published' and Review_x0020_Due_x0020_Date le '@{addDays(utcNow(), 90, 'yyyy-MM-dd')}'` |
| Overdue reviews | `Document_x0020_Status eq 'Approved/Published' and Review_x0020_Due_x0020_Date lt '@{formatDateTime(utcNow(), 'yyyy-MM-dd')}'` |
| LLM ready but not ingested | `LLMIngestReady eq 'Yes' and LLMIngestDate eq null` |
| Drafts by specific owner | `Document_x0020_Status eq 'Draft' and PolicyOwner/EMail eq 'user@agency.gov'` |
| Not archived | `Document_x0020_Status ne 'Archived' and Document_x0020_Status ne 'Superseded'` |

**OData tips:**
- String values use single quotes: `'Submitted for Stage 1 Approval'`
- Date comparisons use ISO format in single quotes: `'2026-04-10'`
- Dynamic dates use expression syntax inside `'@{...}'`
- Person fields filter by `/EMail` (note capital M): `PolicyOwner/EMail eq 'user@agency.gov'`
- Null check: `FieldName eq null`
- Combine with `and` / `or` (lowercase)
- Max 12 lookup columns in `Get files` output — use "Limit Columns by View" if needed

---

## Testing Checklist

### Flow 1 — Stage 1 Notification

1. Change a document's `Document Status` to "Submitted for Stage 1 Approval" in the Power Apps dashboard. Confirm:
   - Flow triggers within 1-5 minutes
   - `Workflow Run ID` is populated briefly, then cleared
   - `Last Submitted Date` is stamped with today's date
   - Stage 1 Reviewer receives the notification email
   - Email contains correct policy number, title, category, classification, owner, link
   - Link opens the document in SharePoint/Word Online

2. Change the same document's status again (e.g., back to Draft, then to Submitted for Stage 1 again). Confirm:
   - The flow fires only once per status change (dedup works)
   - `Last Submitted Date` updates to the new date

3. Test with no Stage 1 Reviewer assigned. Confirm:
   - The fallback email goes to the admin alias
   - Subject indicates "no reviewer assigned"

4. Test error state: Temporarily make the library connection invalid. Confirm:
   - Error handler email is sent to admins
   - `Workflow Run ID` is cleared even on failure

### Flow 2 — Stage 2 Notification

5. Set a document to "Submitted for Stage 2 Approval." Confirm:
   - Stage 2 Final Approver receives the email
   - Email includes Stage 1 decision and comments
   - `Last Submitted Date` is updated

### Flow 3 — LLM Corpus Copy

6. On an Approved/Published doc, set `PDF Converted = Yes`, then set `LLM Ingest Ready = Yes`. Confirm:
   - File appears in the **InfoSec Policy LLM Corpus** library
   - `LLM Ingest Date` is stamped on the source document
   - Policy Owner receives a confirmation email

7. Set `LLM Ingest Ready = Yes` when `PDF Converted = No`. Confirm:
   - File is NOT copied
   - Policy Owner receives the "PDF must be converted" warning email
   - `LLM Ingest Ready` remains "Yes" (not reset)

8. After step 7, set `PDF Converted = Yes`. Confirm:
   - Flow retriggers automatically
   - File is now copied to LLM Corpus
   - Ingest Date is stamped

### Flow 4 — Weekly Reminders

9. Manually set a `Review Due Date` to 30 days from now on an Approved/Published doc. Run Flow 4 manually. Confirm:
   - Policy Owner receives the upcoming review reminder email
   - Email shows correct due date and policy details

10. Set a `Review Due Date` to yesterday. Run Flow 4 manually. Confirm:
    - Policy Owner receives the OVERDUE warning (high importance)
    - Admin alias is CC'd
    - Days Overdue count is correct

### Version Label Flow

11. Check out a document, check it back in. Confirm:
    - `Version Label` column auto-updates to match the SharePoint version string

### General

12. Confirm all flows appear inside the solution in `make.gov.powerautomate.us`
13. Confirm no flows use premium connectors (Approvals is standard, SharePoint is standard, Office 365 Outlook is standard, Schedule is standard)
14. Confirm all SharePoint connections use `.sharepoint.us` URLs

---

## GCC Cautions

- Use `https://make.gov.powerautomate.us` for all flow editing. Do not use commercial `make.powerautomate.com` URLs.
- All SharePoint connections must use `.sharepoint.us` domains. Commercial `.sharepoint.com` will not work.
- Conditional Access must cover both SharePoint and "Microsoft Flow Service" / "Power Automate." If policies diverge, flows may fail silently.
- HTTP connector requests to external services may violate DLP policy. This project uses only standard connectors — no HTTP calls needed.
- Approval emails show timestamps in UTC by default. All email templates above use `convertTimeZone()` to display Eastern Time.
- The first time you use the Approvals connector in a new environment, it provisions a Dataverse database. The user who runs it needs the Environment Admin or System Administrator security role.
- US Government plans cannot assign approvals to users outside the environment. All reviewers and approvers must be internal.
- SharePoint connector throttling: 600 API calls per connection per 60 seconds. For libraries under 2,000 documents, this is not a concern.
- Flow run frequency: SharePoint triggers poll for changes. Expect 1-5 minute delay between the dashboard `Patch()` and the flow trigger.
