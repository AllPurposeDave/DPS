# InfoSec Policy Dashboards — Power Apps Build Guide

Complete implementation guide for the two Power Apps canvas dashboards described in Claude.md.
Covers every screen, gallery, formula, and button with exact Power Fx code tied to the
**InfoSec Policy Documents** SharePoint library columns.

Use alongside Claude.md (column schema + lifecycle) and FlowLogic.md (flow expressions).

---

## Prerequisites

| Requirement | Detail |
|---|---|
| SharePoint library | **InfoSec Policy Documents** — all 25 columns created per Phase 1 |
| Power Apps license | Standard (included with M365 GCC) — no premium needed |
| Power Apps portal | `https://make.gov.powerapps.us` (GCC) |
| Permission groups | Created per Claude.md Permission Groups table |
| Flows deployed | Flow 1–4 built and tested (Phases 3b–3e) |

---

## Architecture Decision

Build one canvas app with two screens:

| Screen | Name in App | Purpose |
|---|---|---|
| Screen 1 | `scrPolicyBoard` | Policy Status Board — Kanban view + detail panel |
| Screen 2 | `scrApprovalsQueue` | Approvals Queue — visual work queue for formal reviewers |

One app is easier to embed on the SharePoint hub page and share via a single URL.

---

## Step 1: Create the Canvas App

1. Go to `https://make.gov.powerapps.us`.
2. Click **+ Create** in the left nav.
3. Select **Blank app** → **Blank canvas app**.
4. Name: `InfoSec Policy Dashboard`.
5. Format: **Tablet** (1366 × 768) — best for SharePoint embedding.
6. Click **Create**.

---

## Step 2: Connect the Data Source

1. In the left panel, click the **cylinder icon** (Data).
2. Click **+ Add data**.
3. Search for **SharePoint**.
4. Select the **SharePoint** connector.
5. Enter your GCC SharePoint site URL (e.g., `https://yourtenant.sharepoint.us/sites/InfoSecPolicies`).
6. Select the **InfoSec Policy Documents** library.
7. Click **Connect**.

The data source appears as `'InfoSec Policy Documents'` in all formulas below. If SharePoint returns a different display name, substitute accordingly.

**Also connect the LLM Corpus library** if you want the dashboard to show ingest status:

8. Click **+ Add data** again → SharePoint → same site → select **InfoSec Policy LLM Corpus**.

---

## Step 3: Create App-Level Variables (App.OnStart)

Select **App** in the tree view → set the `OnStart` property:

```
// App.OnStart
Set(varCurrentUser, User());
Set(varCurrentEmail, Lower(User().Email));

// Cache the full document library into a collection for faster filtering
ClearCollect(
    colPolicies,
    AddColumns(
        'InfoSec Policy Documents',
        "DaysInQueue",
        If(
            IsBlank('Last Submitted Date'),
            0,
            DateDiff('Last Submitted Date', Today(), TimeUnit.Days)
        ),
        "IsOverdue",
        If(
            !IsBlank('Review Due Date') && 'Review Due Date' < Today(),
            true,
            false
        )
    )
);

// Status color map — used throughout both screens
Set(
    varStatusColors,
    {
        Draft:                          ColorValue("#9E9E9E"),
        UnderDraftReviewGroup1:         ColorValue("#42A5F5"),
        UnderDraftReviewGroup2:         ColorValue("#1E88E5"),
        SubmittedForStage1Approval:     ColorValue("#FFA726"),
        Stage1Approved:                 ColorValue("#66BB6A"),
        SubmittedForStage2Approval:     ColorValue("#FF7043"),
        RejectedReturnedToDrafter:      ColorValue("#EF5350"),
        ApprovedPublished:              ColorValue("#2E7D32"),
        Superseded:                     ColorValue("#78909C"),
        Archived:                       ColorValue("#546E7A")
    }
);
```

After pasting, click the **three dots on App** → **Run OnStart** to initialize variables.

---

## Step 4: Navigation Header (reusable component)

Add a **Rectangle** across the top of each screen:

| Property | Value |
|---|---|
| X | `0` |
| Y | `0` |
| Width | `Parent.Width` |
| Height | `60` |
| Fill | `ColorValue("#1565C0")` |

Add a **Label** inside this header for the app title:

| Property | Value |
|---|---|
| Text | `"InfoSec Policy Dashboard"` |
| Color | `White` |
| Font | `Font.'Segoe UI'` |
| Size | `18` |
| FontWeight | `FontWeight.Bold` |
| X | `20` |
| Y | `12` |

Add two **Button** controls for screen navigation:

**Button 1 — Policy Board:**

| Property | Value |
|---|---|
| Text | `"Policy Board"` |
| X | `Parent.Width - 340` |
| Y | `10` |
| Width | `160` |
| Height | `40` |
| Fill | `If(App.ActiveScreen = scrPolicyBoard, ColorValue("#0D47A1"), ColorValue("#1976D2"))` |
| Color | `White` |
| OnSelect | `Navigate(scrPolicyBoard, ScreenTransition.Fade)` |

**Button 2 — Approvals Queue:**

| Property | Value |
|---|---|
| Text | `"Approvals Queue"` |
| X | `Parent.Width - 170` |
| Y | `10` |
| Width | `160` |
| Height | `40` |
| Fill | `If(App.ActiveScreen = scrApprovalsQueue, ColorValue("#0D47A1"), ColorValue("#1976D2"))` |
| Color | `White` |
| OnSelect | `Navigate(scrApprovalsQueue, ScreenTransition.Fade)` |

Copy these three controls to both screens to keep navigation consistent.

---

# Screen 1: Policy Status Board (`scrPolicyBoard`)

## Layout Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Nav Header]                                    [Board] [Queue]   │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────────────┤
│Draft │Grp 1 │Grp 2 │Stg 1 │Stg1Ok│Stg 2 │Pub'd │  Detail Panel   │
│      │Review│Review│Submit│      │Submit│      │  (right overlay) │
│ card │ card │ card │ card │ card │ card │ card │                   │
│ card │ card │ card │ card │      │ card │ card │  Metadata         │
│ card │      │      │      │      │      │      │  Action Buttons   │
│      │      │      │      │      │      │      │  PDF/LLM Strip    │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴───────────────────┘
```

---

## Step 5: Status Filter Tabs (Kanban Column Headers)

Create a **horizontal Gallery** for the Kanban column headers.

1. Insert → Gallery → **Blank horizontal gallery**.
2. Name it `galStatusTabs`.

| Property | Value |
|---|---|
| X | `0` |
| Y | `60` |
| Width | `Parent.Width - 400` |
| Height | `40` |
| TemplateSize | `Self.Width / 7` |
| TemplatePadding | `2` |

Set the `Items` property:

```
Table(
    { StatusLabel: "Draft",           StatusValue: "Draft" },
    { StatusLabel: "Group 1",         StatusValue: "Under Draft Review - Group 1" },
    { StatusLabel: "Group 2",         StatusValue: "Under Draft Review - Group 2" },
    { StatusLabel: "Stage 1",         StatusValue: "Submitted for Stage 1 Approval" },
    { StatusLabel: "Stage 1 OK",      StatusValue: "Stage 1 Approved" },
    { StatusLabel: "Stage 2",         StatusValue: "Submitted for Stage 2 Approval" },
    { StatusLabel: "Published",       StatusValue: "Approved/Published" }
)
```

Inside the gallery template, add a **Button** (or Label with OnSelect):

| Property | Value |
|---|---|
| Text | `ThisItem.StatusLabel` |
| Fill | `If(varSelectedStatus = ThisItem.StatusValue, ColorValue("#1565C0"), ColorValue("#E0E0E0"))` |
| Color | `If(varSelectedStatus = ThisItem.StatusValue, White, Black)` |
| OnSelect | `Set(varSelectedStatus, ThisItem.StatusValue)` |
| Width | `Parent.TemplateWidth - 4` |
| Height | `36` |
| FontWeight | `FontWeight.Semibold` |

Initialize `varSelectedStatus` in the screen's `OnVisible`:

```
// scrPolicyBoard.OnVisible
Set(varSelectedStatus, "Draft");
Set(varSelectedItem, Blank());

// Refresh the collection
ClearCollect(
    colPolicies,
    AddColumns(
        'InfoSec Policy Documents',
        "DaysInQueue",
        If(
            IsBlank('Last Submitted Date'),
            0,
            DateDiff('Last Submitted Date', Today(), TimeUnit.Days)
        ),
        "IsOverdue",
        If(
            !IsBlank('Review Due Date') && 'Review Due Date' < Today(),
            true,
            false
        )
    )
);
```

---

## Step 6: Kanban Card Gallery

Insert → Gallery → **Blank vertical gallery**.
Name: `galPolicyCards`.

| Property | Value |
|---|---|
| X | `0` |
| Y | `100` |
| Width | `Parent.Width - 400` |
| Height | `Parent.Height - 100` |
| TemplateSize | `100` |
| TemplatePadding | `4` |

**Items** property — filter by the selected status tab:

```
SortByColumns(
    Filter(
        colPolicies,
        'Document Status'.Value = varSelectedStatus
    ),
    "Modified",
    SortOrder.Descending
)
```

### Card template contents

Inside the gallery template, add these controls:

**1. Color bar (left edge):**

Rectangle:

| Property | Value |
|---|---|
| X | `0` |
| Y | `0` |
| Width | `6` |
| Height | `Parent.TemplateHeight - 8` |
| Fill | See formula below |

Fill formula — maps status to color:

```
Switch(
    ThisItem.'Document Status'.Value,
    "Draft",                              varStatusColors.Draft,
    "Under Draft Review - Group 1",       varStatusColors.UnderDraftReviewGroup1,
    "Under Draft Review - Group 2",       varStatusColors.UnderDraftReviewGroup2,
    "Submitted for Stage 1 Approval",     varStatusColors.SubmittedForStage1Approval,
    "Stage 1 Approved",                   varStatusColors.Stage1Approved,
    "Submitted for Stage 2 Approval",     varStatusColors.SubmittedForStage2Approval,
    "Rejected - Returned to Drafter",     varStatusColors.RejectedReturnedToDrafter,
    "Approved/Published",                 varStatusColors.ApprovedPublished,
    "Superseded",                         varStatusColors.Superseded,
    "Archived",                           varStatusColors.Archived,
    Color.Gray
)
```

**2. Policy Number label:**

| Property | Value |
|---|---|
| Text | `ThisItem.'Policy Number'` |
| X | `14` |
| Y | `6` |
| FontWeight | `FontWeight.Bold` |
| Size | `12` |

**3. Title label:**

| Property | Value |
|---|---|
| Text | `ThisItem.Title` |
| X | `14` |
| Y | `28` |
| Size | `11` |
| Width | `Parent.TemplateWidth - 30` |

**4. Owner + Modified label:**

| Property | Value |
|---|---|
| Text | `ThisItem.'Policy Owner'.DisplayName & " · " & Text(ThisItem.Modified, "mmm d, yyyy")` |
| X | `14` |
| Y | `52` |
| Size | `10` |
| Color | `ColorValue("#757575")` |

**5. Days in Queue badge (right side):**

| Property | Value |
|---|---|
| Text | `Text(ThisItem.DaysInQueue) & "d"` |
| X | `Parent.TemplateWidth - 60` |
| Y | `6` |
| Width | `50` |
| Align | `Align.Right` |
| Color | `If(ThisItem.DaysInQueue > 5, ColorValue("#D32F2F"), ColorValue("#757575"))` |
| FontWeight | `FontWeight.Semibold` |
| Size | `11` |

**6. Card background (entire template):**

| Property | Value |
|---|---|
| OnSelect | `Set(varSelectedItem, ThisItem)` |
| TemplateFill | `If(varSelectedItem.ID = ThisItem.ID, ColorValue("#E3F2FD"), White)` |

---

## Step 7: Detail Panel (Right-Side Overlay)

This panel shows full metadata for the selected policy and renders conditional action buttons.

Add a **Rectangle** as the panel background:

| Property | Value |
|---|---|
| X | `Parent.Width - 400` |
| Y | `60` |
| Width | `400` |
| Height | `Parent.Height - 60` |
| Fill | `ColorValue("#FAFAFA")` |
| Visible | `!IsBlank(varSelectedItem)` |

### Panel header

**Label — document title:**

| Property | Value |
|---|---|
| Text | `varSelectedItem.Title` |
| X | `Parent.Width - 390` |
| Y | `70` |
| Width | `380` |
| FontWeight | `FontWeight.Bold` |
| Size | `14` |

**Close button (X):**

| Property | Value |
|---|---|
| Text | `"✕"` |
| X | `Parent.Width - 40` |
| Y | `65` |
| Width | `30` |
| Height | `30` |
| OnSelect | `Set(varSelectedItem, Blank())` |

### Metadata labels

Add a series of label pairs (field name + value). You can also use an HTML text control for a compact layout.

For a clean approach, use one **HTML text** control:

Name: `htmlDetailMeta`

| Property | Value |
|---|---|
| X | `Parent.Width - 390` |
| Y | `100` |
| Width | `380` |
| Height | `300` |

`HtmlText` property:

```
"<table style='font-family:Segoe UI; font-size:12px; line-height:1.8; width:100%'>
<tr><td style='color:#757575; width:140px'>Policy Number</td><td><b>" & varSelectedItem.'Policy Number' & "</b></td></tr>
<tr><td style='color:#757575'>Category</td><td>" & varSelectedItem.Category.Value & "</td></tr>
<tr><td style='color:#757575'>Sub-Category</td><td>" & varSelectedItem.'Sub-Category'.Value & "</td></tr>
<tr><td style='color:#757575'>Status</td><td><b>" & varSelectedItem.'Document Status'.Value & "</b></td></tr>
<tr><td style='color:#757575'>Policy Owner</td><td>" & varSelectedItem.'Policy Owner'.DisplayName & "</td></tr>
<tr><td style='color:#757575'>Department</td><td>" & varSelectedItem.Department.Value & "</td></tr>
<tr><td style='color:#757575'>Regulatory Ref</td><td>" & varSelectedItem.'Regulatory Reference' & "</td></tr>
<tr><td style='color:#757575'>Stage 1 Reviewer</td><td>" & varSelectedItem.'Stage 1 Reviewer'.DisplayName & "</td></tr>
<tr><td style='color:#757575'>Last Submitted</td><td>" & Text(varSelectedItem.'Last Submitted Date', "mmm d, yyyy") & "</td></tr>
<tr><td style='color:#757575'>Effective Date</td><td>" & Text(varSelectedItem.'Effective Date', "mmm d, yyyy") & "</td></tr>
<tr><td style='color:#757575'>Review Due Date</td><td>" & Text(varSelectedItem.'Review Due Date', "mmm d, yyyy") & "</td></tr>
<tr><td style='color:#757575'>Version</td><td>" & varSelectedItem.'Version Number' & "</td></tr>
<tr><td style='color:#757575'>Notes</td><td>" & varSelectedItem.Notes & "</td></tr>
</table>"
```

---

## Step 8: Conditional Action Buttons

These buttons appear below the metadata panel. Each is visible only when the right user + right status combination is true.

### Helper: Current user role detection

Add these formulas to `scrPolicyBoard.OnVisible` (after the existing lines):

```
// Detect current user's group memberships
// Power Apps cannot query SP groups directly without premium.
// Instead, match by comparing the user's email against the item's columns.

// varIsOwner: true if the current user IS the Policy Owner of the selected doc
// (evaluated per-click via button Visible property, not set here)
```

### Button: "Mark Group 1 Review Done"

| Property | Value |
|---|---|
| Text | `"Mark Group 1 Review Done"` |
| X | `Parent.Width - 390` |
| Y | `410` |
| Width | `380` |
| Height | `40` |
| Fill | `ColorValue("#42A5F5")` |
| Color | `White` |

**Visible:**

```
varSelectedItem.'Document Status'.Value = "Under Draft Review - Group 1"
```

**OnSelect:**

```
Patch(
    'InfoSec Policy Documents',
    LookUp('InfoSec Policy Documents', ID = varSelectedItem.ID),
    {
        'Document Status': {Value: "Under Draft Review - Group 2"}
    }
);

// Refresh the local collection
ClearCollect(
    colPolicies,
    AddColumns(
        'InfoSec Policy Documents',
        "DaysInQueue",
        If(IsBlank('Last Submitted Date'), 0, DateDiff('Last Submitted Date', Today(), TimeUnit.Days)),
        "IsOverdue",
        If(!IsBlank('Review Due Date') && 'Review Due Date' < Today(), true, false)
    )
);

// Clear selection
Set(varSelectedItem, Blank());

Notify("Status updated to Group 2 Review", NotificationType.Success);
```

### Button: "Mark Group 2 Review Done"

| Property | Value |
|---|---|
| Text | `"Mark Group 2 Review Done"` |
| X | `Parent.Width - 390` |
| Y | `410` |
| Width | `380` |
| Height | `40` |
| Fill | `ColorValue("#1E88E5")` |
| Color | `White` |

**Visible:**

```
varSelectedItem.'Document Status'.Value = "Under Draft Review - Group 2"
```

**OnSelect:**

```
Patch(
    'InfoSec Policy Documents',
    LookUp('InfoSec Policy Documents', ID = varSelectedItem.ID),
    {
        'Document Status': {Value: "Submitted for Stage 1 Approval"},
        'Last Submitted Date': Today()
    }
);

ClearCollect(
    colPolicies,
    AddColumns(
        'InfoSec Policy Documents',
        "DaysInQueue",
        If(IsBlank('Last Submitted Date'), 0, DateDiff('Last Submitted Date', Today(), TimeUnit.Days)),
        "IsOverdue",
        If(!IsBlank('Review Due Date') && 'Review Due Date' < Today(), true, false)
    )
);

Set(varSelectedItem, Blank());
Notify("Submitted for Stage 1 Approval", NotificationType.Success);
```

### Button: "Submit for Stage 1"

Visible to the Policy Owner when the doc is Draft or Rejected.

| Property | Value |
|---|---|
| Text | `"Submit for Stage 1"` |
| X | `Parent.Width - 390` |
| Y | `410` |
| Width | `380` |
| Height | `40` |
| Fill | `ColorValue("#FFA726")` |
| Color | `White` |

**Visible:**

```
And(
    Lower(varSelectedItem.'Policy Owner'.Email) = varCurrentEmail,
    varSelectedItem.'Document Status'.Value in ["Draft", "Rejected - Returned to Drafter"]
)
```

**OnSelect:**

```
Patch(
    'InfoSec Policy Documents',
    LookUp('InfoSec Policy Documents', ID = varSelectedItem.ID),
    {
        'Document Status': {Value: "Submitted for Stage 1 Approval"},
        'Last Submitted Date': Today()
    }
);

ClearCollect(
    colPolicies,
    AddColumns(
        'InfoSec Policy Documents',
        "DaysInQueue",
        If(IsBlank('Last Submitted Date'), 0, DateDiff('Last Submitted Date', Today(), TimeUnit.Days)),
        "IsOverdue",
        If(!IsBlank('Review Due Date') && 'Review Due Date' < Today(), true, false)
    )
);

Set(varSelectedItem, Blank());
Notify("Submitted for Stage 1 Approval — Flow 1 will trigger", NotificationType.Success);
```

### Button: "Submit for Stage 2"

Visible to the Policy Owner when Stage 1 is approved.

| Property | Value |
|---|---|
| Text | `"Submit for Stage 2"` |
| X | `Parent.Width - 390` |
| Y | `410` |
| Width | `380` |
| Height | `40` |
| Fill | `ColorValue("#66BB6A")` |
| Color | `White` |

**Visible:**

```
And(
    Lower(varSelectedItem.'Policy Owner'.Email) = varCurrentEmail,
    varSelectedItem.'Document Status'.Value = "Stage 1 Approved"
)
```

**OnSelect:**

```
Patch(
    'InfoSec Policy Documents',
    LookUp('InfoSec Policy Documents', ID = varSelectedItem.ID),
    {
        'Document Status': {Value: "Submitted for Stage 2 Approval"},
        'Last Submitted Date': Today()
    }
);

ClearCollect(
    colPolicies,
    AddColumns(
        'InfoSec Policy Documents',
        "DaysInQueue",
        If(IsBlank('Last Submitted Date'), 0, DateDiff('Last Submitted Date', Today(), TimeUnit.Days)),
        "IsOverdue",
        If(!IsBlank('Review Due Date') && 'Review Due Date' < Today(), true, false)
    )
);

Set(varSelectedItem, Blank());
Notify("Submitted for Stage 2 Approval — Flow 2 will trigger", NotificationType.Success);
```

### Button: "Open Document"

Always visible when an item is selected.

| Property | Value |
|---|---|
| Text | `"Open Document"` |
| X | `Parent.Width - 390` |
| Y | `460` |
| Width | `185` |
| Height | `36` |
| Fill | `ColorValue("#1565C0")` |
| Color | `White` |

**Visible:**

```
!IsBlank(varSelectedItem)
```

**OnSelect:**

```
Launch(
    varSelectedItem.'{Link}'
)
```

If `{Link}` is not available from the data source, construct it:

```
Launch(
    "https://yourtenant.sharepoint.us/sites/InfoSecPolicies/" & varSelectedItem.'{FullPath}'
)
```

---

## Step 9: PDF & LLM Tracking Strip

This strip appears at the bottom of the detail panel only for **Approved/Published** documents.

### Container

Add a **Rectangle**:

| Property | Value |
|---|---|
| X | `Parent.Width - 400` |
| Y | `Parent.Height - 120` |
| Width | `400` |
| Height | `120` |
| Fill | `ColorValue("#F5F5F5")` |
| Visible | `varSelectedItem.'Document Status'.Value = "Approved/Published"` |

### Label — Section Header

| Property | Value |
|---|---|
| Text | `"PDF & LLM Tracking"` |
| X | `Parent.Width - 390` |
| Y | `Parent.Height - 115` |
| FontWeight | `FontWeight.Semibold` |
| Size | `11` |
| Color | `ColorValue("#616161")` |

### Status indicators

**PDF Status label:**

| Property | Value |
|---|---|
| Text | `"PDF: " & varSelectedItem.'PDF Converted'.Value & If(!IsBlank(varSelectedItem.'PDF Conversion Date'), " (" & Text(varSelectedItem.'PDF Conversion Date', "mmm d") & ")", "")` |
| X | `Parent.Width - 390` |
| Y | `Parent.Height - 95` |
| Size | `10` |

**LLM Status label:**

| Property | Value |
|---|---|
| Text | `"LLM Ingest: " & varSelectedItem.'LLM Ingest Ready'.Value & If(!IsBlank(varSelectedItem.'LLM Ingest Date'), " (" & Text(varSelectedItem.'LLM Ingest Date', "mmm d") & ")", "")` |
| X | `Parent.Width - 390` |
| Y | `Parent.Height - 78` |
| Size | `10` |

### Button: "Mark PDF Converted"

| Property | Value |
|---|---|
| Text | `"Mark PDF Converted"` |
| X | `Parent.Width - 390` |
| Y | `Parent.Height - 55` |
| Width | `185` |
| Height | `36` |
| Fill | `ColorValue("#7E57C2")` |
| Color | `White` |

**Visible:**

```
And(
    varSelectedItem.'Document Status'.Value = "Approved/Published",
    varSelectedItem.'PDF Converted'.Value <> "Yes"
)
```

**OnSelect:**

```
Patch(
    'InfoSec Policy Documents',
    LookUp('InfoSec Policy Documents', ID = varSelectedItem.ID),
    {
        'PDF Converted': {Value: "Yes"},
        'PDF Conversion Date': Today()
    }
);

// Refresh selected item to show updated values
Set(
    varSelectedItem,
    LookUp(
        'InfoSec Policy Documents',
        ID = varSelectedItem.ID
    )
);

Notify("PDF Converted marked", NotificationType.Success);
```

### Button: "Mark LLM Ingest Ready"

| Property | Value |
|---|---|
| Text | `"Mark LLM Ready"` |
| X | `Parent.Width - 195` |
| Y | `Parent.Height - 55` |
| Width | `185` |
| Height | `36` |
| Fill | `ColorValue("#00897B")` |
| Color | `White` |

**Visible:**

```
And(
    varSelectedItem.'Document Status'.Value = "Approved/Published",
    varSelectedItem.'LLM Ingest Ready'.Value <> "Yes"
)
```

**OnSelect:**

```
Patch(
    'InfoSec Policy Documents',
    LookUp('InfoSec Policy Documents', ID = varSelectedItem.ID),
    {
        'LLM Ingest Ready': {Value: "Yes"}
    }
);

Set(
    varSelectedItem,
    LookUp(
        'InfoSec Policy Documents',
        ID = varSelectedItem.ID
    )
);

Notify("LLM Ingest Ready set to Yes — Flow 3 will copy to corpus library", NotificationType.Success);
```

---

## Step 10: Count Badges on Status Tabs

Go back to `galStatusTabs` and add a **Label** inside the gallery template that shows the count per status.

| Property | Value |
|---|---|
| Text | `Text(CountRows(Filter(colPolicies, 'Document Status'.Value = ThisItem.StatusValue)))` |
| X | `Parent.TemplateWidth - 35` |
| Y | `2` |
| Width | `30` |
| Height | `20` |
| Align | `Align.Center` |
| Fill | `ColorValue("#E53935")` |
| Color | `White` |
| Size | `9` |
| FontWeight | `FontWeight.Bold` |
| BorderRadius | `10` |
| Visible | `CountRows(Filter(colPolicies, 'Document Status'.Value = ThisItem.StatusValue)) > 0` |

---

# Screen 2: Approvals Queue (`scrApprovalsQueue`)

## Layout Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Nav Header]                                    [Board] [Queue]   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─ Stage 1 — My Pending Approvals ──────────────────────────────┐ │
│  │ Policy# │ Title          │ Category │ Reg Ref │ Days │ Open   │ │
│  │ IS-001  │ Access Control │ AC       │ NIST    │  3d  │ [btn]  │ │
│  │ IS-005  │ Incident Resp  │ IR       │ FISMA   │  7d  │ [btn]  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌─ Stage 2 — Pending Final Approvals ───────────────────────────┐ │
│  │ Policy# │ Title          │ Category │ Reg Ref │ Days │ Open   │ │
│  │ IS-003  │ Data Classif   │ DM       │ CMMC    │  1d  │ [btn]  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [Info banner: Formal approval action happens in Approvals center] │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 11: Screen OnVisible

```
// scrApprovalsQueue.OnVisible
ClearCollect(
    colPolicies,
    AddColumns(
        'InfoSec Policy Documents',
        "DaysInQueue",
        If(IsBlank('Last Submitted Date'), 0, DateDiff('Last Submitted Date', Today(), TimeUnit.Days)),
        "IsOverdue",
        If(!IsBlank('Review Due Date') && 'Review Due Date' < Today(), true, false)
    )
);
```

---

## Step 12: Stage 1 Section Header

**Label:**

| Property | Value |
|---|---|
| Text | `"Stage 1 — My Pending Approvals (" & Text(CountRows(Filter(colPolicies, 'Document Status'.Value = "Submitted for Stage 1 Approval" && Lower('Stage 1 Reviewer'.Email) = varCurrentEmail))) & ")"` |
| X | `20` |
| Y | `70` |
| Width | `Parent.Width - 40` |
| Height | `32` |
| FontWeight | `FontWeight.Bold` |
| Size | `14` |
| Color | `ColorValue("#E65100")` |

---

## Step 13: Stage 1 Gallery

Insert → Gallery → **Blank vertical gallery**.
Name: `galStage1Queue`.

| Property | Value |
|---|---|
| X | `20` |
| Y | `105` |
| Width | `Parent.Width - 40` |
| Height | `200` |
| TemplateSize | `44` |
| TemplatePadding | `2` |

**Items:**

```
SortByColumns(
    Filter(
        colPolicies,
        'Document Status'.Value = "Submitted for Stage 1 Approval"
            && Lower('Stage 1 Reviewer'.Email) = varCurrentEmail
    ),
    "DaysInQueue",
    SortOrder.Descending
)
```

### Gallery template controls

Add labels across the row to create a table layout:

**Policy Number:**

| Property | Value |
|---|---|
| Text | `ThisItem.'Policy Number'` |
| X | `0` |
| Y | `4` |
| Width | `100` |
| FontWeight | `FontWeight.Semibold` |

**Title:**

| Property | Value |
|---|---|
| Text | `ThisItem.Title` |
| X | `110` |
| Y | `4` |
| Width | `250` |

**Category:**

| Property | Value |
|---|---|
| Text | `ThisItem.Category.Value` |
| X | `370` |
| Y | `4` |
| Width | `120` |

**Regulatory Reference:**

| Property | Value |
|---|---|
| Text | `ThisItem.'Regulatory Reference'` |
| X | `500` |
| Y | `4` |
| Width | `150` |

**Days in Queue:**

| Property | Value |
|---|---|
| Text | `Text(ThisItem.DaysInQueue) & "d"` |
| X | `660` |
| Y | `4` |
| Width | `60` |
| Color | `If(ThisItem.DaysInQueue > 5, ColorValue("#D32F2F"), Black)` |
| FontWeight | `FontWeight.Semibold` |

**Open Document button:**

| Property | Value |
|---|---|
| Text | `"Open"` |
| X | `730` |
| Y | `4` |
| Width | `70` |
| Height | `32` |
| Fill | `ColorValue("#1565C0")` |
| Color | `White` |
| OnSelect | `Launch(ThisItem.'{Link}')` |

**Row highlight on overdue:**

| Property | Value |
|---|---|
| TemplateFill | `If(ThisItem.DaysInQueue > 5, ColorValue("#FFF3E0"), Transparent)` |

---

## Step 14: Stage 2 Section

**Section header label:**

| Property | Value |
|---|---|
| Text | `"Stage 2 — Pending Final Approvals (" & Text(CountRows(Filter(colPolicies, 'Document Status'.Value = "Submitted for Stage 2 Approval"))) & ")"` |
| X | `20` |
| Y | `315` |
| Width | `Parent.Width - 40` |
| FontWeight | `FontWeight.Bold` |
| Size | `14` |
| Color | `ColorValue("#BF360C")` |

Insert → Gallery → **Blank vertical gallery**.
Name: `galStage2Queue`.

| Property | Value |
|---|---|
| X | `20` |
| Y | `350` |
| Width | `Parent.Width - 40` |
| Height | `200` |

**Items:**

```
SortByColumns(
    Filter(
        colPolicies,
        'Document Status'.Value = "Submitted for Stage 2 Approval"
    ),
    "DaysInQueue",
    SortOrder.Descending
)
```

Use the same template layout as `galStage1Queue` — duplicate the controls.

**Note on Stage 2 filtering:** Claude.md specifies Stage 2 uses a multi-person approver group. The `Stage 2 Approver Group` column is multi-select Person. Power Apps cannot directly filter multi-person columns with `= User().Email`. To show only items where the current user is in the Stage 2 group, you would need a workaround. Two options:

**Option A (recommended):** Show all Stage 2 items to all Stage 2 group members. The gallery already filters by status. Since Stage 2 users already have permissions, showing all Stage 2 queue items is acceptable for a work queue.

**Option B (advanced):** Create a separate single-line text column `Stage 2 Approver Emails (Text)` that a flow populates with a semicolon-separated email list. Then filter:

```
varCurrentEmail in Split(ThisItem.'Stage 2 Approver Emails Text', ";")
```

---

## Step 15: Info Banner

Add a **Label** at the bottom of `scrApprovalsQueue`:

| Property | Value |
|---|---|
| Text | `"ℹ Formal approval responses are handled in the Approvals action center (email or Teams). This queue is for visibility only."` |
| X | `20` |
| Y | `Parent.Height - 50` |
| Width | `Parent.Width - 40` |
| Height | `40` |
| Fill | `ColorValue("#E3F2FD")` |
| Color | `ColorValue("#1565C0")` |
| PaddingLeft | `12` |
| Size | `11` |

---

# Embedding on SharePoint

## Step 16: Publish the App

1. In Power Apps Studio, click **File → Save**.
2. Click **Publish**.
3. Click **Publish this version**.
4. The app is now live.

## Step 17: Get the App ID or URL

1. Go to `https://make.gov.powerapps.us`.
2. Click **Apps** in the left nav.
3. Find **InfoSec Policy Dashboard**.
4. Click the ellipsis (`...`) → **Details**.
5. Copy the **App URL** or the **App ID** (GUID).

## Step 18: Embed on the SharePoint Hub Page

1. Navigate to your SharePoint site: `https://yourtenant.sharepoint.us/sites/InfoSecPolicies`.
2. Go to the **InfoSec Policy Hub** page (or create it: Site contents → Site pages → New → Blank page → name it "InfoSec Policy Hub").
3. Click **Edit** on the page.
4. Click the **+** icon to add a new web part.
5. Search for **Power Apps**.
6. Select the **Power Apps** web part.
7. In the web part properties panel on the right:
   - Paste the **App URL** or **App ID**.
   - Set the height (recommend `700` pixels minimum).
8. Click **Republish** on the SharePoint page.

Users who visit the hub page now see the dashboard inline without leaving SharePoint.

---

# Sharing and Permissions

## Step 19: Share the Power Apps App

1. In `https://make.gov.powerapps.us` → Apps → find your app.
2. Click the ellipsis → **Share**.
3. Add the SharePoint permission groups as users:
   - **InfoSec Policy Drafters** — can use (User role)
   - **Draft Review Group 1** — can use
   - **Draft Review Group 2** — can use
   - **Stage 1 Formal Reviewers** — can use
   - **Stage 2 Final Approvers** — can use
   - **InfoSec Policy Admins** — can use + co-owner
4. Ensure **Data permissions** include the SharePoint data source. Power Apps prompts you to grant permission to the connected SharePoint site automatically.

**Important:** The SharePoint connector in Power Apps runs as the signed-in user. Users will only see library items their SharePoint permissions allow. This means:
- Drafters with Contribute can read and write items they have access to.
- Formal reviewers with Read can view items but the `Patch()` calls in buttons will fail for them — which is correct because they should not change status directly. Their action buttons are hidden by the `Visible` property formulas.
- If a `Patch()` fails due to permissions, the user sees a delegation warning or error. Add error handling (see below).

---

# Error Handling for Patch Operations

Wrap every `Patch()` call with `IfError()` to catch permission or connectivity failures. Example for the "Mark Group 1 Review Done" button:

```
IfError(
    Patch(
        'InfoSec Policy Documents',
        LookUp('InfoSec Policy Documents', ID = varSelectedItem.ID),
        {
            'Document Status': {Value: "Under Draft Review - Group 2"}
        }
    ),
    // Error branch
    Notify(
        "Update failed: " & FirstError.Message,
        NotificationType.Error
    ),
    // Success branch
    ClearCollect(
        colPolicies,
        AddColumns(
            'InfoSec Policy Documents',
            "DaysInQueue",
            If(IsBlank('Last Submitted Date'), 0, DateDiff('Last Submitted Date', Today(), TimeUnit.Days)),
            "IsOverdue",
            If(!IsBlank('Review Due Date') && 'Review Due Date' < Today(), true, false)
        )
    );
    Set(varSelectedItem, Blank());
    Notify("Status updated to Group 2 Review", NotificationType.Success)
);
```

Apply this pattern to all action buttons. `FirstError.Message` captures the SharePoint/connector error text and shows it to the user.

---

# Performance Optimization

## Delegation

The SharePoint connector supports delegation for `Filter()` on:
- Text equality (`=`)
- Choice columns
- Date comparisons (`<`, `>`, `<=`, `>=`)
- Person columns (`.Email`, `.DisplayName`)

It does NOT support delegation for:
- `in` operator on text columns
- `Search()` function
- Complex nested `Or()` on non-indexed columns

To avoid delegation warnings:
- Filter on `'Document Status'.Value` (Choice — delegable)
- Filter on `'Stage 1 Reviewer'.Email` (Person — delegable)
- Avoid `Search(Title, varSearchText)` on large libraries — use `StartsWith()` instead, which is delegable

## Collection caching

The `ClearCollect(colPolicies, ...)` pattern used above loads all items locally. This is fine for libraries under ~2,000 items. For larger libraries:
- Increase the data row limit in App settings → General → Data row limit (max 2,000).
- Use direct `Filter('InfoSec Policy Documents', ...)` in gallery Items instead of filtering the collection — this delegates to SharePoint.

---

# Testing Checklist

| Test Case | Expected Result |
|---|---|
| Open app as Drafter | See Policy Board with all status tabs; detail panel with Submit for Stage 1 button on Draft items |
| Open app as Group 1 member | See "Mark Group 1 Review Done" on Group 1 items |
| Click "Mark Group 1 Review Done" | Status changes to "Under Draft Review - Group 2"; card moves to Group 2 column |
| Open app as Group 2 member | See "Mark Group 2 Review Done" on Group 2 items |
| Click "Mark Group 2 Review Done" | Status changes to "Submitted for Stage 1 Approval"; Flow 1 triggers |
| Open app as Policy Owner with rejected doc | See "Submit for Stage 1" button |
| Open app as Policy Owner with Stage 1 Approved doc | See "Submit for Stage 2" button |
| Click "Mark PDF Converted" on Approved doc | PDF Converted = Yes, PDF Conversion Date = Today |
| Click "Mark LLM Ready" on Approved doc | LLM Ingest Ready = Yes; Flow 3 triggers and copies to corpus library |
| Open Approvals Queue as Stage 1 reviewer | See only items assigned to me in Stage 1 section |
| Open Approvals Queue as any user | See info banner about Approvals center |
| Click "Open" on queue item | SharePoint document opens in new tab |
| Patch fails (no permission) | Error notification displays; no silent failure |
| Library has 0 items in a status | Count badge hidden; gallery shows empty |

---

# GCC-Specific Notes

- Use the GCC Power Apps portal: `https://make.gov.powerapps.us`. Do not use `make.powerapps.com`.
- SharePoint data source must use the `.sharepoint.us` URL.
- The Power Apps web part for SharePoint is available in GCC/GCC High. Verify in your tenant that the "Power Apps" web part appears in the web part picker.
- Canvas app performance in GCC may differ from commercial. Test load times with realistic data volumes.
- Power Apps does not support the People Picker control connecting to GCC High Exchange in all tenants. If `User().Email` returns an unexpected format, test with `User().EntraObjectId` and match against the Person column's `Claims` property instead.
- All `Launch()` URLs must point to `.sharepoint.us` domains. Hardcoded `.sharepoint.com` links will fail.
- The Power Automate visual in Power BI is not supported on Azure Government tenants including GCC and GCC High, so do not design the dashboard around in-report flow buttons.
- Use approved GCC High service URLs and approved connectors only.

## Source Notes

Research basis:

- Power Automate US Government
- Power Apps US Government
- Power Automate SharePoint workflow overview
- Power Automate approvals guidance
- Power Automate cloud flow sharing guidance
- Power BI dashboard basics