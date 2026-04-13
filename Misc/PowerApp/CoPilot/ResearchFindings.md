# Web Research Findings — Document Approval Workflow Patterns

Compiled from Microsoft Learn documentation and official Power Platform guidance.
Use these patterns alongside Claude.md, FlowLogic.md, and VisualDash.md to validate
and enhance the InfoSec Policy Document Library build.

---

## 1. Approval Types Available (Standard Connector)

Power Automate's Approvals connector (standard — no premium) offers five built-in types:

| Type | Behavior | Use In This Project |
|---|---|---|
| **Approve/Reject – First to respond** | Flow resumes as soon as any one assigned person responds | **Flow 1 (Stage 1)** — single SME reviewer |
| **Approve/Reject – Everyone must approve** | Flow waits for all assigned people to respond; outcome is "Approve" only if every person approves | **Flow 2 (Stage 2)** — all Stage 2 approvers must agree |
| **Custom Responses – Wait for all responses** | Custom buttons (up to 5 in Outlook); waits for all | Future enhancement if "Need More Info" is added |
| **Custom Responses – Wait for one response** | Custom buttons; resumes on first response | Alternative for Stage 1 with Approve/Need More Info/Reject |
| **Sequential Approval** | Built-in sequential chain; each person approves before the next is notified | Could replace the manual two-stage pattern |

**GCC Government limitation:** Cannot assign approvals to users outside the environment.

**Dataverse prerequisite:** The very first approval flow run in a new environment provisions a Dataverse database. The user who runs it needs the Environment Admin or System Administrator security role. Subsequent users don't need elevated permissions.

---

## 2. Sequential Approval Pattern (Microsoft Reference)

**Source:** Microsoft Learn — Sequential Modern Approvals

The official pattern for a two-stage approval:

```
Trigger: When a file is created or modified (properties only)
  └─ Get manager (V2) — resolve pre-approver
      └─ Start and wait for approval — Pre-approval
          ├─ Condition: response = "Approve" (case-sensitive!)
          │   ├─ TRUE: Email pre-approve confirmation
          │   │   └─ Update SharePoint item
          │   │       └─ Get pre-approver's manager (V2) — resolve final approver
          │   │           └─ Start and wait for approval — Final approval
          │   │               ├─ TRUE: Email final approve + Update SP
          │   │               └─ FALSE: Email reject + Update SP
          │   └─ FALSE: Email reject + Update SP
```

**Key takeaways for this project:**
- The `approverResponse` value is **case-sensitive** — always compare against `"Approve"` not `"approve"` or `"Approved"`
- Use `outputs('action_name')?['body/outcome']` for the overall outcome and `outputs('action_name')?['body/responses'][0]?['approverResponse']` for individual responses
- Each approval action in the flow produces its own output — reference by action name (e.g., `Start_and_wait_for_an_approval_2`)

### Mapping to InfoSec Project

| Microsoft Pattern Step | InfoSec Equivalent |
|---|---|
| Pre-approver = manager | Stage 1 Reviewer (from `Stage 1 Reviewer` Person column) |
| Final approver = manager's manager | Stage 2 Approver Group (multi-select Person column) |
| Pre-approval | Flow 1 — notification only (dashboard-based approval) |
| Final approval | Flow 2 — notification only (dashboard-based approval) |

**Architecture difference:** The InfoSec project uses **notification-only flows** (no "Start and wait for approval"). The Power Apps dashboard IS the approval interface. This avoids the 30-day flow timeout issue entirely.

---

## 3. Parallel Approval Pattern (Multiple Reviewers)

**Source:** Microsoft Learn — Parallel Modern Approvals

Official pattern for parallel branches:

```
Trigger
  └─ Get manager
      ├─ Branch 1: Start approval (Manager) → Condition → Email + SP update
      ├─ Branch 2: Start approval (Sales Team) → Condition → Email + SP update
      └─ Branch 3: Start approval (HR Team) → Condition → Email + SP update
          └─ (All converge) → Send summary email
```

**How to add parallel branches:** Click the "+" between action cards → "Add a parallel branch." Steps placed after all branches converge via the "+New step" at the bottom.

**Simpler alternative (used in this project):** Set `Assigned to` in a single approval action to multiple users separated by semicolons:
```
approver1@agency.gov; approver2@agency.gov; approver3@agency.gov
```
With "Everyone must approve" type, the flow waits for all. This is recommended for Stage 2 over manual parallel branches.

---

## 4. Custom Response Options

**Source:** Microsoft Learn — Create approval response options

Instead of simple Approve/Reject, you can add custom buttons:

| Response Option | When to use |
|---|---|
| Accept | Standard approval |
| Need More Info | Reviewer wants clarification without rejecting |
| Reject | Return to drafter |

**Type:** `Custom Responses – Wait for one response`

**Configuration in Power Automate:**
1. Add "Start and wait for an approval" action
2. Set Approval type to "Custom Responses – Wait for one response"
3. Add items: "Accept", "Need More Info", "Reject"
4. Use a **Switch** action (not Condition) on the `Outcome` output
5. Each case handles the response differently

**Limitation:** Max 5 custom responses in Outlook actionable messages.

### Potential Enhancement for InfoSec Project

Flow 1 could use custom responses instead of Approve/Reject:
- **Approve** → Set `Stage1Decision = "Approved"`, advance to Stage 1 Approved
- **Need More Info** → Set `Document Status = "Rejected - Returned to Drafter"`, set `Stage1Comments = "Needs additional information: [comments]"`
- **Reject** → Set `Document Status = "Rejected - Returned to Drafter"`, set `Stage1Decision = "Rejected"`

**Note:** Since the InfoSec project uses dashboard-based approval (not flow-based "Start and wait"), this pattern would only apply if you add email-based response as a secondary approval channel.

---

## 5. Markdown in Approval Details

**Source:** Microsoft Learn — Approvals Markdown Support

The Details field in approval requests supports Markdown:

| Element | Support in Outlook | Support in Teams |
|---|---|---|
| Headers (#, ##) | Yes | No |
| Numbered lists | Yes | Yes |
| Tables | Yes | No |
| Bold/italic/strikethrough | Yes | No |
| Links | Yes | Yes |

**Recommended Details template for InfoSec notification emails:**

```markdown
## Policy Review Required

**Policy Number:** @{triggerOutputs()?['body/PolicyNumber']}
**Policy Title:** @{triggerOutputs()?['body/Title']}
**Category:** @{triggerOutputs()?['body/Category/Value']}
**Policy Owner:** @{triggerOutputs()?['body/PolicyOwner/DisplayName']}
**Submitted:** @{formatDateTime(utcNow(), 'MMMM d, yyyy')}
**Regulatory Reference:** @{triggerOutputs()?['body/RegulatoryReference']}

| Field | Value |
|---|---|
| Classification | @{triggerOutputs()?['body/Classification/Value']} |
| Department | @{triggerOutputs()?['body/Department/Value']} |
| Version | @{triggerOutputs()?['body/VersionNumber']} |

Please review this policy in the [InfoSec Policy Dashboard](link-to-dashboard).
```

**Important:** Markdown is NOT supported in the Teams Approvals app. Teams renders plain text only for the Details field. Test in both Outlook and Teams.

---

## 6. Timezone Conversion for Dates

Approval details and email notifications show UTC by default. Convert for display:

```
convertTimeZone(utcNow(), 'UTC', 'Eastern Standard Time', 'MMM d, yyyy h:mm tt')
```

Use this in:
- Flow notification email bodies
- Approval Details field
- Any date stamp written to SharePoint if users expect local time

---

## 7. SharePoint Connector — Triggers for Document Libraries

**Source:** Microsoft Learn — SharePoint Connector Actions and Triggers

### Recommended trigger for all InfoSec flows:

**"When a file is created or modified (properties only)"**

| Setting | Value for InfoSec |
|---|---|
| Site Address | `https://yourtenant.sharepoint.us/sites/InfoSecPolicies` |
| Library Name | `InfoSec Policy Documents` |
| Folder | _(leave blank — monitor entire library)_ |
| Limit Columns by View | Optional: use a tracking view to reduce payload |

**Why this trigger:** It fires on property changes (column updates), which is exactly what happens when the Power Apps dashboard uses `Patch()` to change `Document Status`. It does NOT fire on file content changes unless properties also change.

### "When an item or a file is modified" trigger (alternative)

This trigger fires ONLY on modifications (not creation). Use with the **"Get changes for an item or a file"** action to detect exactly which columns changed. This is more precise but requires versioning enabled (already configured per Claude.md).

### Key limitations:

- **Max 12 lookup columns** in trigger output — if more, the flow fails. Use "Limit Columns by View" to reduce below 12.
- **Flow run frequency:** Changes are polled, not instant. Expect 1-5 minute delay.
- **Move files don't re-trigger:** Moving a file between libraries does NOT fire the trigger in the destination library.
- **Throttling:** 600 API calls per connection per 60 seconds.

---

## 8. SharePoint Actions for InfoSec Flows

### Copy file (for Flow 3 — LLM Corpus)

**Operation:** `Copy file` (CopyFileAsync — NOT the deprecated version)

| Parameter | Value for Flow 3 |
|---|---|
| Current Site Address | Same site URL |
| File to Copy | `triggerOutputs()?['body/{Identifier}']` (File Identifier from trigger) |
| Destination Site Address | Same site URL |
| Destination Folder | `/InfoSec Policy LLM Corpus` |
| If another file is already there | Replace (or Fail — depends on your dedup preference) |

**Returns:** `ItemId`, `Id`, `Name`, `Path`, `LastModified`, `Size` of the new file.

### Update file properties (for all flows)

**Operation:** `Update file properties` (PatchFileItem)

| Parameter | Notes |
|---|---|
| Id | Integer — the item ID from trigger: `triggerOutputs()?['body/ID']` |
| Item | Dynamic — shows all library columns |

**Important for document libraries vs. lists:** Use `Update file properties` NOT `Update item`. The latter is for lists. For document libraries, the correct action is `Update file properties`.

### Check in / Check out

Since the InfoSec library has **Require Check Out = Yes**, flows that update file properties may need to:

1. **Check out file** before updating
2. **Update file properties**
3. **Check in file** with a comment

**Or:** Configure the flow connection to use a service account that has Contribute+ permissions, and handle check-in/check-out around the property update. If the doc is already checked out by a user, the flow's `Check out file` action will fail — add error handling for this.

**Check in parameters:**
| Field | Value |
|---|---|
| Site Address | Site URL |
| Library Name | `InfoSec Policy Documents` |
| Id | Item ID |
| Comments | `"Updated by Power Automate flow"` |
| Check in type | `0` = Minor, `1` = Major, `2` = Overwrite |

---

## 9. Flow Dedup Pattern — Validated

The project's dedup guard (from Claude.md) is a correct and common pattern:

```
Condition: DocumentStatus = "[target]" AND WorkflowRunID is empty
  TRUE:
    1. Write guid() to WorkflowRunID FIRST ← prevents re-trigger
    2. Proceed with logic
    3. Clear WorkflowRunID at end of EVERY branch
  FALSE: Terminate
```

**Additional recommendations:**
- Add a **Trigger condition** in the trigger settings to pre-filter before the flow even runs:
  ```
  @and(
    equals(triggerOutputs()?['body/DocumentStatus/Value'], 'Submitted for Stage 1 Approval'),
    empty(triggerOutputs()?['body/WorkflowRunID'])
  )
  ```
  This prevents unnecessary flow runs (saves against the daily run quota).
- Use **Concurrency control** on the trigger (set to 1) to prevent parallel runs on the same item.

---

## 10. Power Apps Delegation Rules — Confirmed

**Source:** Microsoft Learn — SharePoint Online Connector Delegation

### Delegable to SharePoint:

| Function/Operator | Delegable? |
|---|---|
| `Filter` | Yes |
| `LookUp` | Yes |
| `Sort` / `SortByColumns` | Yes |
| `=` (equals) | Yes — all data types |
| `<>` (not equal) | Yes — most types |
| `<`, `>`, `<=`, `>=` | Yes — Number, Date, Currency |
| `StartsWith` | Yes — Text/Single-line only |
| `And` / `Or` | Yes |
| `Not` | **NO — does NOT delegate** |
| `IsBlank` | **NO — does NOT delegate** |
| `Search` | **NO** |
| `In` | **NO** |

### Person column delegation:
- **Only `Email` and `DisplayName` subfields delegate**
- Cannot filter by Person.Id, Person.Department, etc.
- This is why VisualDash.md uses `Lower('Stage 1 Reviewer'.Email) = varCurrentEmail`

### SharePoint ID field:
- In Power Apps, ID is treated as **Text type**, not Number
- Only the `=` operator delegates on ID
- `<`, `>` do NOT delegate on ID

### System fields that do NOT delegate:
ContentType, FilenameWithExtension, FullPath, Identifier, IsCheckedOut, IsFolder, Link, Name, Path, ModerationComment, ModerationStatus, Thumbnail, VersionNumber

### Practical implication for InfoSec dashboards:
The `ClearCollect` pattern in VisualDash.md (cache entire library to collection) avoids all delegation issues. For libraries up to ~2,000 docs this is fine. If the library grows past the delegation limit (default 500, configurable to 2,000), you'll need server-side filtering with delegable expressions.

---

## 11. Check-In/Check-Out Interaction with Flows

The InfoSec library has **Require Check Out = Yes** (per Claude.md). This creates an important interaction:

**Problem:** If a user has a document checked out, and a Power Automate flow tries to update file properties, the update will **fail** because the file is locked by the user's checkout.

**Solutions:**
1. **Flow uses Check out → Update → Check in sequence** — but this fails if someone else already has it checked out
2. **Use "Send an HTTP request to SharePoint"** with elevated permissions to bypass check-out (not recommended for audit trail)
3. **Best practice:** Design the workflow so flows only update properties **after** the user checks the file back in. Since the trigger fires on property changes (which happen after check-in), this is naturally handled if:
   - Users check out → edit → check in → then change status in Power Apps
   - Power Apps `Patch()` triggers the flow, which updates additional metadata columns
   - The flow's property update creates a new minor version (auto-checked-in)

**If the flow must update a checked-out file:** Wrap the update in a Scope with error handling. On failure, send a notification: "Cannot update — file is checked out by [user]. Please check in and retry."

---

## 12. 30-Day Flow Timeout — Mitigated

Classic "Start and wait for an approval" flows have a 30-day maximum lifespan. The InfoSec project's architecture **avoids this entirely** because:

- Flows 1 and 2 are **notification-only** (send email, update a few columns, exit)
- The Power Apps dashboard is the approval interface
- No "Start and wait for an approval" action means no long-running flow

This is a significant architectural advantage over the traditional pattern.

---

## 13. Reassign and Cancel Approvals

If "Start and wait for approval" is used in the future:

- **Reassign:** Approvers can reassign from the Approvals center (three dots → Reassign)
- **Cancel:** Flow owners can cancel pending approvals from the Sent tab in the Approvals center
- **Programmatic cancel:** Use "Cancel an approval" action in a separate flow

---

## 14. SharePoint REST API via Flow

**Action:** "Send an HTTP request to SharePoint"

For operations not covered by standard actions:

**Example — Get all versions of a document:**
```
Method: GET
Uri: _api/web/lists/getbytitle('InfoSec Policy Documents')/items(@{triggerOutputs()?['body/ID']})/versions
Headers: {
  "Accept": "application/json; odata=nometadata"
}
```

**Example — Break inheritance on a specific item:**
```
Method: POST
Uri: _api/web/lists/getbytitle('InfoSec Policy Documents')/items(@{triggerOutputs()?['body/ID']})/breakroleinheritance(copyRoleAssignments=true, clearSubscopes=true)
```

**Parsing response:**
- Single value: `body('Send_an_HTTP_request_to_SharePoint')['Id']`
- Array: `body('Send_an_HTTP_request_to_SharePoint')['value']`
- Loop items: `items('Apply_to_each')['Title']`

---

## 15. GCC-Specific Notes

| Item | Detail |
|---|---|
| Power Automate portal | `https://make.gov.powerautomate.us` |
| Power Apps portal | `https://make.gov.powerapps.us` |
| SharePoint domain | `.sharepoint.us` (not `.sharepoint.com`) |
| Approvals connector | Standard (no premium) |
| US Gov limitation | Cannot assign approvals to users outside the environment |
| Dataverse provisioning | First approval run needs admin role |
| DLP policies | Review connector policies — HTTP connector may be blocked |
| Conditional Access | Must cover both SharePoint and "Microsoft Flow Service" |

---

## 16. Actionable Enhancements for InfoSec Project

Based on research, the following enhancements could be applied:

### High Priority
1. **Add trigger conditions to all flows** — Pre-filter with `@and(equals(...), empty(...))` in trigger settings to avoid unnecessary runs
2. **Rewrite FlowLogic.md** — Current version uses GCC High column names and generic "ApprovalStatus". Needs full rewrite to match Claude.md's 25 columns and InfoSec lifecycle
3. **Add check-in/check-out handling in flows** — Required since library enforces checkout
4. **Use `Update file properties` not `Update item`** — Document library requires the file-specific action

### Medium Priority
5. **Add Markdown to notification emails** — Use tables and bold formatting in Flow 1/2 notification bodies
6. **Add timezone conversion** — Use `convertTimeZone()` for all date displays in emails
7. **Set trigger concurrency to 1** — Prevent parallel processing of the same document update
8. **Add "Limit Columns by View" to triggers** — Avoid the 12-lookup-column limit

### Lower Priority (Future)
9. **Custom responses** — Add "Need More Info" to Stage 1 if email-based approval is added later
10. **SP HTTP request for version history** — Display version count in dashboard detail panel
11. **Auto-approve pattern** — Skip Stage 1 if the policy owner IS the Stage 1 reviewer
12. **Flow 4 enhancement** — Use OData date filter `Review_x0020_Due_x0020_Date le '@{addDays(utcNow(), 90)}'` for the upcoming reviews reminder

---

## Source URLs

1. Sequential Modern Approvals: https://learn.microsoft.com/en-us/power-automate/sequential-modern-approvals
2. Custom Response Options: https://learn.microsoft.com/en-us/power-automate/create-approval-response-options
3. SP HTTP Request: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/working-with-send-sp-http-request
4. SharePoint Form Integration: https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/sharepoint-form-integration
5. Approvals How-To: https://learn.microsoft.com/en-us/power-automate/approvals-howto
6. Get Started Approvals: https://learn.microsoft.com/en-us/power-automate/get-started-approvals
7. Customize Page Approvals: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/customize-page-approvals
8. Parallel Modern Approvals: https://learn.microsoft.com/en-us/power-automate/parallel-modern-approvals
9. Power Apps SP Connector: https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-sharepoint-online
10. SP Connector Actions/Triggers: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/sharepoint-connector-actions-triggers
11. Approvals Markdown Support: https://learn.microsoft.com/en-us/power-automate/approvals-markdown-support
12. SP Connector Reference: https://learn.microsoft.com/en-us/connectors/sharepointonline/
13. Migrate Classic Workflows: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/migrate-from-classic-workflows-to-power-automate-flows
