# Power BI — DAX Measures, Page Wireframes, and Security Model

This document covers the complete Power BI implementation for the GCC High document approval dashboard. Sections cover data source connection, data model setup, every DAX measure needed per role, visual and filter recommendations per page, and the row-level security model with step-by-step configuration.

Use this alongside VisualDash.md (audience and UX design) and Claude.md (SharePoint column schema).

## References

- SharePoint Online List connector: https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-sharepoint-online-list
- Row-Level Security (RLS): https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security
- RLS guidance and best practices: https://learn.microsoft.com/en-us/power-bi/guidance/rls-guidance
- DAX function reference: https://learn.microsoft.com/en-us/dax/dax-function-reference

---

## Part 1: Data Source Connection

### Connect Power BI Desktop to GCC High SharePoint

1. Open Power BI Desktop.
2. Select `Get data` from the Home ribbon.
3. Choose `More...` to open the full connector list.
4. Under `Online Services`, select `SharePoint Online List`.
5. Enter your GCC High SharePoint site URL.  
   Example: `https://contoso.sharepoint.us/sites/DocumentApproval`
6. Leave the implementation as `2.0` (recommended — faster and more compatible).
7. Click `OK`.
8. Authenticate using `Microsoft Account` and sign in with your GCC High credentials.  
   Use the government sign-in endpoint. If prompted for environment, select the government or GCC High option.
9. In the Navigator pane, select your document library or list.
10. Click `Transform Data` to open Power Query. Do not click `Load` directly — you need to clean the data first.

### Authentication note for GCC High

If the credential prompt loops or fails, clear cached credentials in Power BI Desktop under `File → Options and settings → Data source settings`. Remove any existing SharePoint credentials and re-authenticate.

---

## Part 2: Power Query Data Preparation

Apply these transformations in Power Query before loading to the model. Each step is listed in order.

### Remove system columns

Remove SharePoint system columns that have no reporting value. Use `Remove Columns` and select columns starting with `odata.etag`, `odata.id`, all underscore-prefixed columns like `_UIVersionString`, and any column named `ContentTypeId`, `GUID`, `ComplianceAssetId`.

### Keep only the columns needed for reporting

Use `Choose Columns` and keep the following:

| Power Query Column | SharePoint Source Column |
|---|---|
| `DocumentID` | `Document_ID` or `DocumentID` |
| `Title` | `FileLeafRef` (file name) or `Title` |
| `DocumentType` | `DocumentType` → `.Value` expanded |
| `Requestor_Email` | `Author` → `.Email` expanded |
| `Requestor_Name` | `Author` → `.DisplayName` expanded |
| `Department` | `Department` → `.Value` expanded |
| `SubmissionDate` | `Submission_Date` |
| `ApprovalStatus` | `ApprovalStatus` → `.Value` expanded |
| `CurrentApprover_Email` | `CurrentApprover` → `.Email` expanded |
| `CurrentApprover_Name` | `CurrentApprover` → `.DisplayName` expanded |
| `ApproverComments` | `Approver_Comments` |
| `DecisionDate` | `Decision_Date` |
| `DueDate` | `Due_Date` |
| `ResubmissionRequired` | `Resubmission_Required` → `.Value` expanded |
| `WorkflowInstanceID` | `Workflow_Instance_ID` |

For person columns (like Author and CurrentApprover), SharePoint returns a Record type. Expand them by clicking the expand icon on the column header and selecting the sub-fields you need (`Email`, `DisplayName`). Rename each expanded field with the naming convention above.

For choice columns (like ApprovalStatus, Department, DocumentType), expand the `Value` sub-field only.

### Set correct data types

After expanding and renaming, set these data types explicitly:

| Column | Type |
|---|---|
| `DocumentID` | Text |
| `Title` | Text |
| `DocumentType` | Text |
| `Requestor_Email` | Text |
| `Requestor_Name` | Text |
| `Department` | Text |
| `SubmissionDate` | Date/Time |
| `ApprovalStatus` | Text |
| `CurrentApprover_Email` | Text |
| `CurrentApprover_Name` | Text |
| `ApproverComments` | Text |
| `DecisionDate` | Date/Time |
| `DueDate` | Date/Time |
| `ResubmissionRequired` | Text |
| `WorkflowInstanceID` | Text |

### Add a calculated column in Power Query: Cycle Time Days

In Power Query, add a custom column:

```
= if [DecisionDate] = null then null
  else Duration.TotalDays([DecisionDate] - [SubmissionDate])
```

Name it `CycleTimeDays`. This gives you raw cycle time without requiring DAX for simple visuals.

### Add a calculated column: IsOverdue

```
= if [ApprovalStatus] = "In Review" and [DueDate] < DateTime.LocalNow() then "Yes" else "No"
```

Name it `IsOverdue`.

### Date table

Create a separate date table for time intelligence. Add a blank query with this M code:

```
let
    StartDate = #date(2024, 1, 1),
    EndDate = Date.From(DateTime.LocalNow()),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    Source = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    AsTable = Table.FromList(Source, Splitter.SplitByNothing(), {"Date"}),
    TypedDate = Table.TransformColumnTypes(AsTable, {{"Date", type date}}),
    Year = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    Month = Table.AddColumn(Year, "Month", each Date.Month([Date]), Int64.Type),
    MonthName = Table.AddColumn(Month, "MonthName", each Date.ToText([Date], "MMMM"), type text),
    Quarter = Table.AddColumn(MonthName, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    YearMonth = Table.AddColumn(Quarter, "YearMonth", each Text.From(Date.Year([Date])) & "-" & Text.PadStart(Text.From(Date.Month([Date])), 2, "0"), type text)
in
    YearMonth
```

Name this query `DateTable`. In the model view, mark it as a date table using the `Date` column.

Create a relationship from `DateTable[Date]` to your documents table on `SubmissionDate` (many-to-one, single direction). You may also create an inactive relationship to `DecisionDate` and activate it with `USERELATIONSHIP()` in DAX measures.

---

## Part 3: Data Model

The data model is intentionally simple for this use case.

**Tables:**

- `Documents` — main fact table from SharePoint
- `DateTable` — date dimension for time intelligence

**Relationships:**

| From | To | Cardinality | Direction | Active |
|---|---|---|---|---|
| `Documents[SubmissionDate]` | `DateTable[Date]` | Many-to-one | Single | Yes |
| `Documents[DecisionDate]` | `DateTable[Date]` | Many-to-one | Single | No (inactive) |

Do not create relationships on person email columns. RLS filters using DAX expressions directly against those columns.

---

## Part 4: DAX Measures

All measures are created in the `Documents` table unless noted. Create a dedicated Measures table (an empty calculated table named `_Measures`) to keep measures organized and separate from raw data columns.

To create the measures table: `New table` → `_Measures = DATATABLE("Placeholder", STRING, {{"x"}})`. Then create all measures in that table.

---

### Global / All-Audience Measures

These measures are used across pages and are not role-filtered.

```dax
Total Documents = 
COUNTROWS(Documents)
```

```dax
Total Submitted = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[ApprovalStatus] <> "Draft"
)
```

```dax
Total In Review = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[ApprovalStatus] = "In Review"
)
```

```dax
Total Approved = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[ApprovalStatus] = "Approved"
)
```

```dax
Total Rejected = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[ApprovalStatus] = "Rejected"
)
```

```dax
Total Overdue = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[ApprovalStatus] = "In Review",
    Documents[DueDate] < TODAY()
)
```

```dax
Approval Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(Documents), Documents[ApprovalStatus] = "Approved"),
    CALCULATE(COUNTROWS(Documents), Documents[ApprovalStatus] IN {"Approved", "Rejected"}),
    BLANK()
)
```

Format as percentage, 1 decimal place.

```dax
Rejection Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(Documents), Documents[ApprovalStatus] = "Rejected"),
    CALCULATE(COUNTROWS(Documents), Documents[ApprovalStatus] IN {"Approved", "Rejected"}),
    BLANK()
)
```

```dax
Avg Cycle Time Days = 
AVERAGEX(
    FILTER(
        Documents,
        NOT(ISBLANK(Documents[DecisionDate])) && NOT(ISBLANK(Documents[SubmissionDate]))
    ),
    DATEDIFF(Documents[SubmissionDate], Documents[DecisionDate], DAY)
)
```

```dax
Max Cycle Time Days = 
MAXX(
    FILTER(
        Documents,
        NOT(ISBLANK(Documents[DecisionDate])) && NOT(ISBLANK(Documents[SubmissionDate]))
    ),
    DATEDIFF(Documents[SubmissionDate], Documents[DecisionDate], DAY)
)
```

```dax
SLA Met % = 
DIVIDE(
    CALCULATE(
        COUNTROWS(Documents),
        Documents[ApprovalStatus] IN {"Approved", "Rejected"},
        Documents[DecisionDate] <= Documents[DueDate]
    ),
    CALCULATE(
        COUNTROWS(Documents),
        Documents[ApprovalStatus] IN {"Approved", "Rejected"},
        NOT(ISBLANK(Documents[DecisionDate]))
    ),
    BLANK()
)
```

Format as percentage.

```dax
Avg Days Pending = 
AVERAGEX(
    FILTER(
        Documents,
        Documents[ApprovalStatus] = "In Review" && NOT(ISBLANK(Documents[SubmissionDate]))
    ),
    DATEDIFF(Documents[SubmissionDate], TODAY(), DAY)
)
```

```dax
Volume This Month = 
CALCULATE(
    COUNTROWS(Documents),
    DATESMTD(DateTable[Date])
)
```

```dax
Volume Last Month = 
CALCULATE(
    COUNTROWS(Documents),
    PREVIOUSMONTH(DateTable[Date])
)
```

```dax
MOM Change = 
[Volume This Month] - [Volume Last Month]
```

```dax
MOM Change % = 
DIVIDE([MOM Change], [Volume Last Month], BLANK())
```

---

### Requester Page Measures (Personal View)

These measures filter to the current user's own documents. They rely on `USERPRINCIPALNAME()` which returns the signed-in user's UPN in the Power BI service. Validate that the UPN format matches the email stored in `Requestor_Email` (both should be `user@agency.gov` format in GCC High).

```dax
My Pending = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[Requestor_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "In Review"
)
```

```dax
My Approved = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[Requestor_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "Approved"
)
```

```dax
My Rejected = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[Requestor_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "Rejected"
)
```

```dax
My Overdue = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[Requestor_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "In Review",
    Documents[DueDate] < TODAY()
)
```

```dax
My Avg Cycle Time = 
AVERAGEX(
    FILTER(
        Documents,
        Documents[Requestor_Email] = USERPRINCIPALNAME()
            && NOT(ISBLANK(Documents[DecisionDate]))
            && NOT(ISBLANK(Documents[SubmissionDate]))
    ),
    DATEDIFF(Documents[SubmissionDate], Documents[DecisionDate], DAY)
)
```

```dax
My Resubmissions Needed = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[Requestor_Email] = USERPRINCIPALNAME(),
    Documents[ResubmissionRequired] = "Yes"
)
```

```dax
My Total Submitted = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[Requestor_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] <> "Draft"
)
```

---

### Approver Page Measures (Queue View)

These measures filter to the current user's assigned approval queue.

```dax
Pending My Review = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[CurrentApprover_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "In Review"
)
```

```dax
Overdue My Queue = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[CurrentApprover_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "In Review",
    Documents[DueDate] < TODAY()
)
```

```dax
Due Today My Queue = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[CurrentApprover_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "In Review",
    Documents[DueDate] = TODAY()
)
```

```dax
My Oldest Pending Days = 
MAXX(
    FILTER(
        Documents,
        Documents[CurrentApprover_Email] = USERPRINCIPALNAME()
            && Documents[ApprovalStatus] = "In Review"
            && NOT(ISBLANK(Documents[SubmissionDate]))
    ),
    DATEDIFF(Documents[SubmissionDate], TODAY(), DAY)
)
```

```dax
My Approved Total = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[CurrentApprover_Email] = USERPRINCIPALNAME(),
    Documents[ApprovalStatus] = "Approved"
)
```

```dax
My Avg Decision Time = 
AVERAGEX(
    FILTER(
        Documents,
        Documents[CurrentApprover_Email] = USERPRINCIPALNAME()
            && NOT(ISBLANK(Documents[DecisionDate]))
    ),
    DATEDIFF(Documents[SubmissionDate], Documents[DecisionDate], DAY)
)
```

---

### Admin / Executive Page Measures (Unfiltered Org-Wide)

These measures span all documents and are used on admin and executive pages. They should only be visible to users with Admin or Executive roles who see all data.

These are the global measures already defined above. No additional filtering needed. Repeat here for clarity:

- `Total Submitted`
- `Total In Review`
- `Total Approved`
- `Total Rejected`
- `Total Overdue`
- `Approval Rate`
- `Rejection Rate`
- `Avg Cycle Time Days`
- `SLA Met %`
- `Volume This Month`
- `MOM Change %`

```dax
Stuck Items (Over 10 Days) = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[ApprovalStatus] = "In Review",
    DATEDIFF(Documents[SubmissionDate], TODAY(), DAY) > 10
)
```

```dax
Resubmission Total = 
CALCULATE(
    COUNTROWS(Documents),
    Documents[ResubmissionRequired] = "Yes"
)
```

```dax
Volume by Dept — Label = 
VAR SelDept = SELECTEDVALUE(Documents[Department])
RETURN
IF(ISBLANK(SelDept), "All Departments", SelDept)
```

---

## Part 5: Page Wireframes

Each page corresponds to one audience from VisualDash.md. Role-based visibility is enforced by RLS.

---

### Page 1: My Submissions (Requester View)

**Purpose:** Requestors see only their own documents. They cannot see documents from other users.

**Filter panel (right side or top):**

- `ApprovalStatus` slicer (multi-select): Draft / Submitted / In Review / Approved / Rejected
- `DocumentType` slicer
- `Submission Date` date range picker
- Default filter pre-applied: `Requestor_Email = USERPRINCIPALNAME()` (enforced by RLS — not a visible slicer)

**Visuals (top row — KPI cards):**

| Visual | Measure | Format |
|---|---|---|
| Card | `My Pending` | Count, bold |
| Card | `My Approved` | Count |
| Card | `My Rejected` | Count |
| Card | `My Overdue` | Count, red if > 0 |
| Card | `My Avg Cycle Time` | "X days" suffix |
| Card | `My Resubmissions Needed` | Count, amber if > 0 |

**Visuals (middle row):**

| Visual | X-axis | Y-axis / Legend | Notes |
|---|---|---|---|
| Stacked bar | `Department` | `ApprovalStatus` count | Shows distribution of their docs by status |
| Line chart | `DateTable[YearMonth]` | `My Total Submitted` | Submission volume over time |

**Visuals (bottom — table):**

| Column | Source |
|---|---|
| Document Name | `Title` |
| Type | `DocumentType` |
| Submitted | `SubmissionDate` (formatted date) |
| Status | `ApprovalStatus` |
| Due Date | `DueDate` |
| Current Approver | `CurrentApprover_Name` |
| Approver Comments | `ApproverComments` |

Enable conditional formatting on the `Status` column: Approved = green, Rejected = red, In Review = blue, Overdue = orange.

---

### Page 2: My Approval Queue (Approver View)

**Purpose:** Approvers see documents waiting for their decision and their historical decisions.

**Filter panel:**

- `IsOverdue` slicer: All / Yes / No
- `DocumentType` slicer
- `ApprovalStatus` slicer
- `Due Date` date range picker

**Visuals (top row — KPI cards):**

| Visual | Measure |
|---|---|
| Card | `Pending My Review` |
| Card | `Overdue My Queue` |
| Card | `Due Today My Queue` |
| Card | `My Oldest Pending Days` |
| Card | `My Avg Decision Time` |

**Visuals (middle row):**

| Visual | Description |
|---|---|
| Donut chart | Pending by `DocumentType` — shows which types are most common in queue |
| Bar chart | `Requestor_Name` by count of documents in queue — who is submitting most to this approver |

**Visuals (bottom — action table):**

This is the primary working tool for approvers. Include a direct link to each document.

| Column | Source |
|---|---|
| Document Name | `Title` — link to SharePoint if supported |
| Type | `DocumentType` |
| Submitted By | `Requestor_Name` |
| Submission Date | `SubmissionDate` |
| Due Date | `DueDate` |
| Days Waiting | `CycleTimeDays` (calculated column) or DAX measure |
| Status | `ApprovalStatus` |
| Overdue | `IsOverdue` |

Sort the default view by `Due Date` ascending so most urgent items appear first. Use conditional formatting to flag `IsOverdue = Yes` rows in orange or red.

---

### Page 3: Operations Dashboard (Admin View)

**Purpose:** Admins see all documents across all users. This page provides operational visibility into queue health, SLA compliance, and bottlenecks.

**Filter panel:**

- `ApprovalStatus` slicer
- `Department` slicer
- `DocumentType` slicer
- `CurrentApprover_Name` slicer (to drill into a specific approver's queue)
- `SubmissionDate` date range picker

**Visuals (top row — KPI cards):**

| Visual | Measure |
|---|---|
| Card | `Total In Review` |
| Card | `Total Overdue` |
| Card | `SLA Met %` |
| Card | `Avg Cycle Time Days` |
| Card | `Stuck Items (Over 10 Days)` |
| Card | `Resubmission Total` |

**Visuals (second row):**

| Visual | Description |
|---|---|
| Stacked bar (horizontal) | `CurrentApprover_Name` vs count of In Review items — identifies overloaded approvers |
| Bar chart | `Department` vs count by `ApprovalStatus` — shows which departments have most pending |

**Visuals (third row):**

| Visual | Description |
|---|---|
| Line chart | Submissions per month (`Volume This Month`) over `DateTable[YearMonth]` — trend line |
| Gauge or KPI visual | `SLA Met %` vs target (e.g., 95%) — shows whether SLA is being met |

**Visuals (bottom — drillable table):**

Same columns as Page 2 but showing all documents across all requestors and approvers. Add a `Requestor_Name` column. Sort by `DueDate` ascending by default.

---

### Page 4: Executive Summary

**Purpose:** Senior leadership sees high-level metrics without operational detail. No personally identifiable submitter data. Focus on trends, rates, and aggregate health.

**Filter panel:**

- `Department` slicer (light — just for drill-down on demand)
- `Date` quarter slicer or year filter

**Visuals (top row — large KPI cards):**

| Visual | Measure | Visual size |
|---|---|---|
| Large KPI card | `Total Submitted` | Full-width header |
| KPI visual | `Approval Rate` vs prior period | With trend arrow |
| KPI visual | `SLA Met %` vs target (95%) | With status indicator |
| KPI visual | `Avg Cycle Time Days` vs target | With trend arrow |

**Visuals (second row):**

| Visual | Description |
|---|---|
| Area chart | Total submitted by month (line) and total approved (area fill) — shows throughput trend |
| Donut chart | Current status distribution — Draft / In Review / Approved / Rejected proportion |

**Visuals (third row):**

| Visual | Description |
|---|---|
| Bar chart | `Approval Rate` by `Department` — which departments have highest approval rates |
| Bar chart | `Avg Cycle Time Days` by `DocumentType` — which document types take longest |

No detailed tables. No individual names. This page is for trends and health only.

---

## Part 6: Row-Level Security (RLS) Implementation

### Overview

RLS restricts what rows a user sees in the semantic model. It is defined in Power BI Desktop and enforced in the Power BI service after publishing.

**Role design for this project:**

| Role Name | Filter Rule | Who Gets This Role |
|---|---|---|
| `Requester_Role` | User sees only their own documents | All document submitters |
| `Approver_Role` | User sees documents assigned to them for review | All approvers |
| `Admin_Role` | No filter — sees all rows | Operations staff, DLP/compliance admins |
| `Executive_Role` | No filter — sees all rows | Senior leadership |

**Important:** RLS does not apply to workspace Admin, Member, or Contributor roles. Only workspace Viewers are filtered by RLS. If you give an operations admin the workspace Member role, they bypass RLS entirely. Assign end users as workspace Viewers unless they need to edit the report.

---

### Step 1: Define roles in Power BI Desktop

1. Open Power BI Desktop with the published `.pbix` file.
2. Go to the `Modeling` tab.
3. Select `Manage roles`.
4. Click `New` to create the first role.

**Requester_Role:**

1. Name: `Requester_Role`
2. Select the `Documents` table.
3. Switch to DAX editor.
4. Enter:

```dax
[Requestor_Email] = USERPRINCIPALNAME()
```

This filters the Documents table so the user only sees rows where their UPN matches the `Requestor_Email` column.

**Approver_Role:**

1. Name: `Approver_Role`
2. Select the `Documents` table.
3. Enter:

```dax
[CurrentApprover_Email] = USERPRINCIPALNAME()
```

This filters the Documents table to documents currently assigned to this user for review.

**Admin_Role:**

1. Name: `Admin_Role`
2. Select the `Documents` table.
3. Enter:

```dax
TRUE()
```

`TRUE()` allows all rows — no filtering. Admins see everything.

**Executive_Role:**

1. Name: `Executive_Role`
2. Select the `Documents` table.
3. Enter:

```dax
TRUE()
```

Same as Admin_Role — no row filtering. Executives see all rows. You can add a future filter here if needed such as limiting to certain departments.

---

### Step 2: Validate roles in Power BI Desktop before publishing

1. Go to the `Modeling` tab.
2. Select `View as`.
3. Select a role to enter `View As` mode.
4. The report refreshes to show only data that role can see.
5. Navigate to each page and confirm the data is filtered correctly.
6. Use `Other User` input and enter a test UPN to simulate a specific user's view.
7. Confirm that a requestor only sees their own documents.
8. Confirm that an approver only sees documents in their queue.
9. Select `Stop viewing` to exit View As mode.

---

### Step 3: Publish to Power BI Service

1. Save the `.pbix` file.
2. Select `Publish` in Power BI Desktop.
3. Select your GCC High Power BI workspace.
4. After publishing, open the workspace in the GCC High Power BI service.

GCC High Power BI service URL: `https://app.high.powerapps.us/` or `https://app.powerbigov.us/` — confirm the correct GCC High tenant endpoint with your admin.

---

### Step 4: Assign members to roles in the Power BI service

1. Open the workspace in the Power BI service.
2. Find the semantic model (dataset) for your report.
3. Click the ellipsis (`...`) next to the semantic model.
4. Select `Security`.
5. The `Row-Level Security` pane opens, listing all defined roles.
6. Click the role name (e.g., `Requester_Role`).
7. In the Members field, enter the email address or Entra Security Group to add members.
8. Click `Add`.
9. Repeat for each role.

**Important:** Use Entra Security Groups, not Microsoft 365 Groups. M365 Groups are not supported for RLS role assignment. Create Entra Security Groups for each role and add users to those groups in Entra ID. Then assign the security group to the Power BI RLS role. This makes user management easier — adding or removing a user from the Entra group automatically affects their Power BI access without touching the report.

---

### Step 5: Validate roles in the Power BI service

1. Open the semantic model.
2. Click ellipsis → `Security`.
3. Click `Test as role` next to a role.
4. The report opens in View As mode for that role.
5. Verify that the report shows only the expected data.
6. For dynamic roles (`Requester_Role`, `Approver_Role`), click `Test as role` → enter a specific user email to simulate their view.

---

### RLS Considerations

**Additive roles:** If a user belongs to both `Requester_Role` and `Approver_Role`, they see the union of rows from both filters. This means they see their own submitted documents AND documents assigned to them for review. This is expected behavior for approvers who also submit documents.

**Admin and Executive users do not need both Admin_Role and Requester_Role.** Because `Admin_Role` returns `TRUE()`, the union already includes all rows. Assign admins only to `Admin_Role`.

**Test before go-live.** Common RLS failures include:
- UPN format mismatch (user@contoso.us vs user@contoso.com) — check the actual UPN format used in `Requestor_Email`
- User not in any role — sees no data (blank report)
- User in a workspace role higher than Viewer — bypasses RLS entirely

**RLS does not protect the underlying data source.** RLS only filters what Power BI shows. If a user has direct SharePoint access, they may still see documents outside their RLS audience. Manage SharePoint permissions separately.

---

## Part 7: Publish, Workspace, and Refresh

### Workspace setup

Create a dedicated workspace for this report. Suggested name: `GCCH-DocApproval-Reporting`.

Assign workspace roles:
- Flow owners and report editors: `Contributor`
- Operations admins who need to see the admin page: `Viewer` (and add them to Admin_Role in RLS)
- All other end users: `Viewer` (and add them to the appropriate RLS role)
- Do not assign end users to `Member` or `Contributor` unless they need to edit reports — those roles bypass RLS

### Scheduled refresh

1. In the workspace, click the ellipsis on the semantic model.
2. Select `Settings`.
3. Expand `Scheduled refresh`.
4. Enable refresh.
5. Set the refresh frequency based on your SLA and reporting needs. For a daily process, once per hour during business hours is a reasonable starting point.
6. Add a recipient for refresh failure notifications.

**GCC High refresh note:** The SharePoint Online List connector in GCC High uses OAuth through Microsoft Entra Government. The credential stored in the scheduled refresh must belong to a user with read access to the SharePoint library. Use a service account with non-expiring credentials if possible, or set a reminder for credential renewal.

---

## Part 8: GCC High-Specific Notes

- The Power Automate visual (which can embed a flow button in a report) is not supported in GCC High. Do not plan for Power Automate integration inside Power BI visuals.
- Use GCC High SharePoint URLs (`*.sharepoint.us`) for the data source connection. The standard `*.sharepoint.com` URLs will not authenticate correctly.
- Power BI semantic model refresh through the SharePoint Online List connector works in GCC High but requires a valid credential stored in the service.
- Power BI data gateways are supported in GCC High if you have hybrid or on-premises SharePoint. Configure the on-premises data gateway using the GCC High endpoint.
- If you use row-level security with Entra Security Groups, confirm those groups exist in the GCC High Entra tenant, not a commercial Entra tenant.
- Validate every `USERPRINCIPALNAME()` filter against the actual UPN format in your tenant. GCC High UPNs typically follow `user@agency.gov` but confirm this with your identity team.
