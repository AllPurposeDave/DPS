# InfoSec Policy Document Library — Project Guide

## Goal

SharePoint GCC document library for InfoSec policy document lifecycle management.
Two informal draft review stages (Group 1, Group 2) + two formal approval stages (Stage 1 SME, Stage 2 Final).
Power Apps dashboards embedded on SharePoint intranet page.
LLM Ingest tracking with automatic file copy to a separate LLM Corpus library on ingest readiness.

## Environment

- Platform: Microsoft 365 GCC
- SharePoint document library: **InfoSec Policy Documents**
- LLM Corpus library: **InfoSec Policy LLM Corpus** (separate library, same site)
- Tools: Power Automate (standard connectors only — no premium), Power Apps canvas
- Power Automate portal: `make.gov.powerautomate.us` (verify your tenant routing; may be `flow.microsoft.com`)

---

## Lifecycle

```
Draft
  └─> Under Draft Review - Group 1        [informal: Group 1 changes status; no flow]
        └─> Under Draft Review - Group 2  [informal: Group 2 changes status; no flow]
              └─> Submitted for Stage 1 Approval   <- Flow 1 triggers
                    ├─> Rejected - Returned to Drafter
                    └─> Stage 1 Approved
                          └─> Submitted for Stage 2 Approval  <- Flow 2 triggers
                                ├─> Rejected - Returned to Drafter
                                └─> Approved/Published
                                      └─> Superseded / Archived
```

When `LLM Ingest Ready` is set to "Yes" on any Approved/Published doc -> Flow 3 triggers and copies the file to the LLM Corpus library.

- **Draft review**: Informal. Status change only, no email gate. Group members use Power Apps buttons or edit the column directly.
- **Stage 1**: Formal. Flow 1 triggers a notification email only (non-blocking). Reviewers act in the Power Apps dashboard.
- **Stage 2**: Formal. Flow 2 triggers a notification email only (non-blocking). Approvers act in the Power Apps dashboard.
- **Rejection**: Always returns to "Rejected - Returned to Drafter" regardless of stage.
- **Checkout required**: Enforced at library level. One editor at a time.

---

## Build Phases & Status

- [ ] Phase 1: Library + versioning + all columns + permission groups
- [ ] Phase 2: All views created
- [ ] Phase 3a: LLM Corpus library created
- [ ] Phase 3b: Flow 1 (Stage 1 Approval) built + tested
- [ ] Phase 3c: Flow 2 (Stage 2 Final Approval) built + tested
- [ ] Phase 3d: Flow 3 (LLM Corpus Copy) built + tested
- [ ] Phase 3e: Flow 4 (Weekly Review Due Reminders) built + tested
- [ ] Phase 4a: Power Apps Dashboard 1 (Policy Status Board) built
- [ ] Phase 4b: Power Apps Dashboard 2 (Approvals Queue) built
- [ ] Phase 5: SharePoint "InfoSec Policy Hub" page published + app embedded

---

## Key Columns Quick Reference

| Column | Type | Purpose |
|---|---|---|
| Document Status | Choice | Master state machine -- drives all flows |
| Workflow Run ID | Single line (hidden from all views) | Flow dedup lock; set to guid() at flow start, cleared at branch end |
| Stage 1 Reviewer | Person (single, optional) | Informational only -- any contributor can act on Stage 1 from the dashboard |
| Stage 2 Final Approver | Person (single) | The one designated person whose approval publishes the document |
| PDF Converted | Choice: No / Yes / N/A | Tracks DOCX to PDF conversion for distribution |
| PDF Conversion Date | Date only | Date PDF was created |
| LLM Ingest Ready | Choice: No / Pending Review / Yes | Triggers Flow 3 when set to "Yes" |
| LLM Ingest Date | Date only | Stamped by Flow 3 on copy completion |
| Last Submitted Date | Date only | Updated by flow at each formal submission |
| Effective Date | Date only | Set by Flow 2 on final approval |
| Review Due Date | Date only | Typically Effective Date + 1 year; set manually or auto-calculated |
| Last Revision Date | Date only | Manual entry -- date of last substantive content revision |
| Last Approval Date | Date only | Auto-set by Flow 2 on every final approval (including re-approvals) |
| Modified (built-in) | Date/time | SharePoint auto-maintains; use this as "Last Updated" -- no custom column needed |

Version Label: auto-set by a flow triggered on file check-in (reads SharePoint's built-in _UIVersionString and writes it to this column). Do not use a manual text field. Ask Claude to generate the check-in flow when ready.

Full column schema is in the project plan. Ask Claude to print the full schema for any phase.

---

## Flow Dedup Pattern

Both formal flows (Stage 1 and Stage 2) use this guard to prevent infinite trigger loops:

```
Condition: DocumentStatus = "[target status]" AND WorkflowRunID is empty
  TRUE:
    1. Write guid() to WorkflowRunID FIRST
    2. Proceed with approval logic
    3. At end of EVERY branch: set WorkflowRunID = "" (clear the lock)
  FALSE: Terminate (do nothing)
```

Flow 3 (LLM Copy) guard: LLM Ingest Ready = "Yes" AND PDF Converted = "Yes" AND LLM Ingest Date is empty.
If LLM Ingest Ready = "Yes" but PDF Converted != "Yes": flow sends a warning email back to Policy Owner ("PDF must be converted before LLM ingest") and does not copy. LLM Ingest Ready remains "Yes" so the flow retriggers correctly once PDF is marked done.

---

## Library Settings Summary

| Setting | Value |
|---|---|
| Content Approval | Off (custom workflow handles approval) |
| Version history | Major and minor versions |
| Major versions to keep | 50 |
| Minor drafts to keep | 10 |
| Require Check Out | Yes -- prevents concurrent edits |

---

## Permission Groups Summary

| Group | Permission | Role |
|---|---|---|
| InfoSec Policy Contributors | Contribute | Drafters, Group 1, Group 2, Stage 1 reviewers -- most team members already have this |
| Stage 2 Final Approver | Contribute | Single designated final approver |
| InfoSec Policy Readers | Read | General staff -- see published policies only |
| InfoSec Policy Admins | Full Control | Library admin |

Most team members already have Contribute/Edit access -- no separate reviewer groups needed. Contribute is required because dashboard approval buttons use Patch() to write directly to SharePoint columns. Stage 2 is a single designated person (not a group), and only one approval is needed to publish.

---

## Power Apps Notes

Two dashboards in one canvas app (or split into two apps -- both work):

**Dashboard 1 -- Policy Status Board**
- Kanban-style: one column per lifecycle stage, color-coded (gray/blue/yellow/green)
- Each card: Policy Number, Title, Owner, Last Modified
- Detail panel (right-side overlay): all metadata read-only + conditional action buttons
- Conditional buttons based on CurrentUser() and DocumentStatus:
  - Group 1: "Mark Group 1 Review Done" -> Patch status to "Under Draft Review - Group 2"
  - Group 2: "Mark Group 2 Review Done" -> Patch status to "Submitted for Stage 1 Approval"
  - PolicyOwner on Draft/Rejected: "Submit for Stage 1" -> Patch status
  - PolicyOwner on Stage 1 Approved: "Submit for Stage 2" -> Patch status
- PDF & LLM tracking strip at bottom of detail panel for Approved/Published docs:
  - "Mark PDF Converted" -> Patch PDF_Converted = "Yes", PDF_Conversion_Date = Today()
  - "Mark LLM Ingest Ready" -> Patch LLM_Ingest_Ready = "Yes" (triggers Flow 3)

**Dashboard 2 -- Approvals Queue (primary approval interface)**
- Stage 1 section: Gallery filtered to DocumentStatus = "Submitted for Stage 1 Approval" -- visible to all Contributors (any team member can act)
- Stage 2 section: Gallery filtered to DocumentStatus = "Submitted for Stage 2 Approval"
- Each card shows: Policy Number, Title, Category, Regulatory Ref, Classification, Days in Queue (DateDiff), Policy Owner
- "Open Document" button: Launch("https://[tenant].sharepoint.com" & ThisItem.FileRef) -- opens document in browser/Word Online
- Comment text input box (bound to a local variable per card, e.g., UpdateContext({reviewComment: ""}))
- "Approve" button: Patch(InfoSecPolicyDocuments, ThisItem, {DocumentStatus: "Stage 1 Approved", Stage1Decision: "Approved", Stage1DecisionDate: Today(), Stage1Comments: CommentInput.Text})
- "Send Back" button: Patch(InfoSecPolicyDocuments, ThisItem, {DocumentStatus: "Rejected - Returned to Drafter", Stage1Decision: "Rejected", Stage1DecisionDate: Today(), Stage1Comments: CommentInput.Text})
- Stage 2 uses same layout, targets Stage2Decision / Stage2Comments / Stage2DecisionDate columns
- ARCHITECTURE NOTE: Flows 1 and 2 are notification-only (no "Start and wait for approval"). The dashboard IS the approval interface. Audit trail is in SharePoint columns, not the Microsoft Approvals system.

**Embedding**: SharePoint modern page > Edit > "+" > Power Apps web part > paste app URL/ID. No premium license needed.

---

## Views Summary

| View | Filter | Who |
|---|---|---|
| My Drafts | Owner=[Me] AND Status = Draft or Rejected | Drafters |
| Drafts Awaiting Group Review | Status = Group 1 or Group 2 review | Review groups |
| Awaiting Stage 1 Approval | Status = Submitted for Stage 1 | Stage 1 reviewers |
| Awaiting Stage 2 Approval | Status = Submitted for Stage 2 | Stage 2 approvers |
| All Active Policies | Status = Approved/Published | Everyone (intranet) |
| Policy Status Tracker | Status NOT Archived/Superseded -- grouped by Status | Admins |
| PDF & LLM Tracking | Status = Approved/Published -- shows tracking columns | Admin/Ops |
| Upcoming Reviews | Status = Approved AND ReviewDueDate < [Today]+90 | Admin/Owners |
| Archive | Status = Archived or Superseded | Records |

---

## How Claude Helps You

Each session, tell Claude:
- Which phase/step you are on
- What you just completed (check the box above)
- What you are stuck on or building next

Claude will generate on demand:
- Exact SharePoint column settings (type, required flag, choice values)
- Column default value configurations
- OData filter query syntax for flows: eq, le, ge, and, date expressions
- Power Automate expressions: guid(), utcNow(), addDays(), formatDateTime(), triggerOutputs()
- Notification-only flow configuration (non-blocking email on status change)
- Email body templates with dynamic content tokens
- Power Apps formulas: Patch(), Filter(), If(), Switch(), DateDiff(), User(), Launch()
- SharePoint view filter expressions using [Today], [Me], and offset syntax
- Step-by-step UI navigation for any SharePoint or Power Automate action
- Troubleshooting for flow trigger issues (dedup failures, column update loops)
