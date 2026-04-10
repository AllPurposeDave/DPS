Attribute VB_Name = "xlsx2docx_macro"
'===============================================================================
' xlsx2docx VBA Macro — Convert active Excel sheet to a formatted Word document.
'
' PURPOSE:
'   Reads the active sheet as a controls matrix. One column (the "heading column")
'   becomes Word headings; all other columns render as labeled key-value content
'   beneath each heading. Produces a .docx in the same folder as the workbook.
'
' HOW TO USE:
'   1. Open your workbook in Excel.
'   2. Press Alt+F11 to open the VBA editor.
'   3. File > Import File > select this .bas file (or paste code into a Module).
'   4. Close the VBA editor.
'   5. Go to Developer > Macros > "GenerateDocx" > Run.
'      (Or press Alt+F8, select GenerateDocx, click Run.)
'
' CONFIGURATION:
'   Option A (recommended): Add a "Config" sheet to your workbook.
'     - Column A = Setting name, Column B = Value.
'     - Use the companion xlsx2docx_config.xlsx as a template.
'     - Copy the "Config" sheet into any workbook you want to convert.
'
'   Option B: If no "Config" sheet is found, the macro uses built-in defaults
'     defined in the DEFAULT_* constants below.
'
' REQUIREMENTS:
'   - Microsoft Word must be installed (uses Word Object Model via late binding).
'   - The workbook must be saved to disk before running (for output path).
'
' OUTPUT:
'   MyWorkbook.xlsx  -->  MyWorkbook.docx  (same folder)
'===============================================================================
Option Explicit

'===============================================================================
' BUILT-IN DEFAULTS — Used when no "Config" sheet is present.
' These match the defaults in xlsx2docx_config.yaml.
'===============================================================================

' --- Data Layout ---
Private Const DEFAULT_HEADING_COLUMN As String = "Control ID"
Private Const DEFAULT_HEADING_LEVEL As Long = 2
Private Const DEFAULT_HEADER_ROW As Long = 1
Private Const DEFAULT_DATA_START_ROW As Long = 2
Private Const DEFAULT_SKIP_EMPTY_HEADING As Boolean = True
Private Const DEFAULT_EXCLUDE_COLUMNS As String = ""
Private Const DEFAULT_INCLUDE_COLUMNS As String = ""
Private Const DEFAULT_RENAME_COLUMNS As String = ""

' --- Document Identity ---
Private Const DEFAULT_DOCUMENT_TITLE As String = ""
Private Const DEFAULT_ORGANIZATION_NAME As String = ""
Private Const DEFAULT_CLASSIFICATION As String = ""
Private Const DEFAULT_AUTHOR As String = ""
Private Const DEFAULT_VERSION As String = "1.0"
Private Const DEFAULT_DATE As String = ""

' --- Page Layout ---
Private Const DEFAULT_PAGE_SIZE As String = "Letter"
Private Const DEFAULT_ORIENTATION As String = "Portrait"
Private Const DEFAULT_MARGIN_TOP As Double = 1#
Private Const DEFAULT_MARGIN_BOTTOM As Double = 1#
Private Const DEFAULT_MARGIN_LEFT As Double = 1.25
Private Const DEFAULT_MARGIN_RIGHT As Double = 1.25

' --- Body Text ---
Private Const DEFAULT_BODY_FONT As String = "Calibri"
Private Const DEFAULT_BODY_SIZE As Long = 11
Private Const DEFAULT_BODY_LINE_SPACING As Double = 1.15

' --- Heading Style ---
Private Const DEFAULT_HEADING_FONT As String = "Calibri"
Private Const DEFAULT_HEADING_SIZE As Long = 14
Private Const DEFAULT_HEADING_BOLD As Boolean = True
Private Const DEFAULT_HEADING_COLOR As String = "2F5496"

' --- Key-Value Label Style ---
Private Const DEFAULT_LABEL_FONT As String = "Calibri"
Private Const DEFAULT_LABEL_SIZE As Long = 11
Private Const DEFAULT_LABEL_BOLD As Boolean = True
Private Const DEFAULT_LABEL_COLOR As String = "2F5496"

' --- Header ---
Private Const DEFAULT_HEADER_LEFT As String = "{organization_name}"
Private Const DEFAULT_HEADER_CENTER As String = ""
Private Const DEFAULT_HEADER_RIGHT As String = "{document_title}"
Private Const DEFAULT_HEADER_FONT As String = "Arial"
Private Const DEFAULT_HEADER_SIZE As Long = 8
Private Const DEFAULT_HEADER_COLOR As String = "666666"

' --- Footer ---
Private Const DEFAULT_FOOTER_LEFT As String = "{classification}"
Private Const DEFAULT_FOOTER_CENTER As String = "Page {page} of {pages}"
Private Const DEFAULT_FOOTER_RIGHT As String = "{date}"
Private Const DEFAULT_FOOTER_FONT As String = "Arial"
Private Const DEFAULT_FOOTER_SIZE As Long = 8
Private Const DEFAULT_FOOTER_COLOR As String = "666666"

' --- Section Heading ---
Private Const DEFAULT_ADD_SHEET_HEADING As Boolean = False


'===============================================================================
' CONFIG READER — Reads settings from the "Config" sheet if present.
'===============================================================================

' Module-level config dictionary, populated once per run.
Private cfg As Object


'--- Load config from the "Config" sheet (columns A/B). Falls back to defaults. ---
Private Sub LoadConfig()
    Set cfg = CreateObject("Scripting.Dictionary")

    ' Try to find a "Config" sheet in the active workbook
    Dim ws As Worksheet
    Dim found As Boolean: found = False
    For Each ws In ActiveWorkbook.Worksheets
        If LCase(Trim(ws.Name)) = "config" Then
            found = True
            Exit For
        End If
    Next ws

    If Not found Then Exit Sub  ' No Config sheet — all reads will use defaults

    ' Read key-value pairs from columns A and B
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row

    Dim r As Long
    For r = 1 To lastRow
        Dim key As String
        key = LCase(Trim(CStr(ws.Cells(r, 1).Value & "")))

        ' Skip blank keys and section headers (rows with no value column)
        If Len(key) = 0 Then GoTo NextConfigRow

        ' Skip rows that look like section headers (start with "[" or "---")
        If Left(key, 1) = "[" Or Left(key, 3) = "---" Then GoTo NextConfigRow

        Dim val As String
        val = Trim(CStr(ws.Cells(r, 2).Value & ""))

        ' Store the value (overwrite if duplicate key)
        If cfg.Exists(key) Then
            cfg(key) = val
        Else
            cfg.Add key, val
        End If
NextConfigRow:
    Next r
End Sub


'--- Get a string config value by key (case-insensitive). ---
Private Function CfgStr(key As String, defaultVal As String) As String
    Dim lk As String: lk = LCase(Trim(key))
    If cfg.Exists(lk) Then
        CfgStr = cfg(lk)
    Else
        CfgStr = defaultVal
    End If
End Function


'--- Get a Long config value. ---
Private Function CfgLong(key As String, defaultVal As Long) As Long
    Dim s As String: s = CfgStr(key, "")
    If Len(s) > 0 And IsNumeric(s) Then
        CfgLong = CLng(s)
    Else
        CfgLong = defaultVal
    End If
End Function


'--- Get a Double config value. ---
Private Function CfgDbl(key As String, defaultVal As Double) As Double
    Dim s As String: s = CfgStr(key, "")
    If Len(s) > 0 And IsNumeric(s) Then
        CfgDbl = CDbl(s)
    Else
        CfgDbl = defaultVal
    End If
End Function


'--- Get a Boolean config value (accepts TRUE/FALSE/YES/NO/1/0). ---
Private Function CfgBool(key As String, defaultVal As Boolean) As Boolean
    Dim s As String: s = LCase(CfgStr(key, ""))
    Select Case s
        Case "true", "yes", "1"
            CfgBool = True
        Case "false", "no", "0"
            CfgBool = False
        Case Else
            CfgBool = defaultVal
    End Select
End Function


'===============================================================================
' MAIN ENTRY POINT — Run this macro from Developer > Macros.
'===============================================================================
Public Sub GenerateDocx()
    On Error GoTo ErrHandler

    ' --- Validate workbook state ---
    If ActiveWorkbook Is Nothing Then
        MsgBox "No workbook is open.", vbExclamation, "xlsx2docx"
        Exit Sub
    End If
    If Len(ActiveWorkbook.Path) = 0 Then
        MsgBox "Please save the workbook before running this macro." & vbCrLf & _
               "(The .docx will be saved in the same folder.)", vbExclamation, "xlsx2docx"
        Exit Sub
    End If

    ' --- Load configuration ---
    LoadConfig

    ' --- Read config values (with defaults) ---
    Dim sHeadingColumn As String:   sHeadingColumn = CfgStr("heading_column", DEFAULT_HEADING_COLUMN)
    Dim nHeadingLevel As Long:      nHeadingLevel = CfgLong("heading_level", DEFAULT_HEADING_LEVEL)
    Dim nHeaderRow As Long:         nHeaderRow = CfgLong("header_row", DEFAULT_HEADER_ROW)
    Dim nDataStartRow As Long:      nDataStartRow = CfgLong("data_start_row", DEFAULT_DATA_START_ROW)
    Dim bSkipEmptyHeading As Boolean: bSkipEmptyHeading = CfgBool("skip_empty_heading", DEFAULT_SKIP_EMPTY_HEADING)
    Dim sExcludeColumns As String:  sExcludeColumns = CfgStr("exclude_columns", DEFAULT_EXCLUDE_COLUMNS)
    Dim sIncludeColumns As String:  sIncludeColumns = CfgStr("include_columns", DEFAULT_INCLUDE_COLUMNS)
    Dim sRenameColumns As String:   sRenameColumns = CfgStr("rename_columns", DEFAULT_RENAME_COLUMNS)

    Dim sDocTitle As String:        sDocTitle = CfgStr("document_title", DEFAULT_DOCUMENT_TITLE)
    Dim sOrgName As String:         sOrgName = CfgStr("organization_name", DEFAULT_ORGANIZATION_NAME)
    Dim sClassification As String:  sClassification = CfgStr("classification", DEFAULT_CLASSIFICATION)
    Dim sAuthor As String:          sAuthor = CfgStr("author", DEFAULT_AUTHOR)
    Dim sVersion As String:         sVersion = CfgStr("version", DEFAULT_VERSION)
    Dim sDate As String:            sDate = CfgStr("date", DEFAULT_DATE)

    Dim sPageSize As String:        sPageSize = CfgStr("page_size", DEFAULT_PAGE_SIZE)
    Dim sOrientation As String:     sOrientation = CfgStr("orientation", DEFAULT_ORIENTATION)
    Dim dMarginTop As Double:       dMarginTop = CfgDbl("margin_top", DEFAULT_MARGIN_TOP)
    Dim dMarginBottom As Double:    dMarginBottom = CfgDbl("margin_bottom", DEFAULT_MARGIN_BOTTOM)
    Dim dMarginLeft As Double:      dMarginLeft = CfgDbl("margin_left", DEFAULT_MARGIN_LEFT)
    Dim dMarginRight As Double:     dMarginRight = CfgDbl("margin_right", DEFAULT_MARGIN_RIGHT)

    Dim sBodyFont As String:        sBodyFont = CfgStr("body_font", DEFAULT_BODY_FONT)
    Dim nBodySize As Long:          nBodySize = CfgLong("body_size", DEFAULT_BODY_SIZE)
    Dim dBodySpacing As Double:     dBodySpacing = CfgDbl("body_line_spacing", DEFAULT_BODY_LINE_SPACING)

    Dim sHeadingFont As String:     sHeadingFont = CfgStr("heading_font", DEFAULT_HEADING_FONT)
    Dim nHeadingSize As Long:       nHeadingSize = CfgLong("heading_size", DEFAULT_HEADING_SIZE)
    Dim bHeadingBold As Boolean:    bHeadingBold = CfgBool("heading_bold", DEFAULT_HEADING_BOLD)
    Dim sHeadingColor As String:    sHeadingColor = CfgStr("heading_color", DEFAULT_HEADING_COLOR)

    Dim sLabelFont As String:       sLabelFont = CfgStr("label_font", DEFAULT_LABEL_FONT)
    Dim nLabelSize As Long:         nLabelSize = CfgLong("label_size", DEFAULT_LABEL_SIZE)
    Dim bLabelBold As Boolean:      bLabelBold = CfgBool("label_bold", DEFAULT_LABEL_BOLD)
    Dim sLabelColor As String:      sLabelColor = CfgStr("label_color", DEFAULT_LABEL_COLOR)

    Dim sHeaderLeft As String:      sHeaderLeft = CfgStr("header_left", DEFAULT_HEADER_LEFT)
    Dim sHeaderCenter As String:    sHeaderCenter = CfgStr("header_center", DEFAULT_HEADER_CENTER)
    Dim sHeaderRight As String:     sHeaderRight = CfgStr("header_right", DEFAULT_HEADER_RIGHT)
    Dim sHeaderFont As String:      sHeaderFont = CfgStr("header_font", DEFAULT_HEADER_FONT)
    Dim nHeaderSize As Long:        nHeaderSize = CfgLong("header_size", DEFAULT_HEADER_SIZE)
    Dim sHeaderColor As String:     sHeaderColor = CfgStr("header_color", DEFAULT_HEADER_COLOR)

    Dim sFooterLeft As String:      sFooterLeft = CfgStr("footer_left", DEFAULT_FOOTER_LEFT)
    Dim sFooterCenter As String:    sFooterCenter = CfgStr("footer_center", DEFAULT_FOOTER_CENTER)
    Dim sFooterRight As String:     sFooterRight = CfgStr("footer_right", DEFAULT_FOOTER_RIGHT)
    Dim sFooterFont As String:      sFooterFont = CfgStr("footer_font", DEFAULT_FOOTER_FONT)
    Dim nFooterSize As Long:        nFooterSize = CfgLong("footer_size", DEFAULT_FOOTER_SIZE)
    Dim sFooterColor As String:     sFooterColor = CfgStr("footer_color", DEFAULT_FOOTER_COLOR)

    Dim bAddSheetHeading As Boolean: bAddSheetHeading = CfgBool("add_sheet_heading", DEFAULT_ADD_SHEET_HEADING)

    Dim ws As Worksheet
    Set ws = ActiveSheet

    ' --- Build output path ---
    Dim stem As String
    stem = Left(ActiveWorkbook.Name, InStrRev(ActiveWorkbook.Name, ".") - 1)
    Dim outputPath As String
    outputPath = ActiveWorkbook.Path & Application.PathSeparator & stem & ".docx"

    ' --- Find heading column ---
    Dim headingCol As Long
    headingCol = FindColumnByName(ws, sHeadingColumn, nHeaderRow)
    If headingCol = 0 Then
        MsgBox "Heading column '" & sHeadingColumn & "' not found in row " & _
               nHeaderRow & " of sheet '" & ws.Name & "'.", vbExclamation, "xlsx2docx"
        Exit Sub
    End If

    ' --- Build column map ---
    Dim lastCol As Long
    lastCol = ws.Cells(nHeaderRow, ws.Columns.Count).End(xlToLeft).Column
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, headingCol).End(xlUp).Row

    If lastRow < nDataStartRow Then
        MsgBox "No data rows found (data starts at row " & nDataStartRow & _
               ", last row = " & lastRow & ").", vbExclamation, "xlsx2docx"
        Exit Sub
    End If

    ' --- Build exclude/include/rename maps ---
    Dim excludeSet As Object: Set excludeSet = ParseCsvToDict(sExcludeColumns)
    Dim includeSet As Object: Set includeSet = ParseCsvToDict(sIncludeColumns)
    Dim renameMap As Object:  Set renameMap = ParseRenameMap(sRenameColumns)

    ' --- Build token map ---
    Dim tokens As Object: Set tokens = CreateObject("Scripting.Dictionary")
    Dim dateVal As String
    If Len(Trim(sDate)) > 0 Then
        dateVal = sDate
    Else
        dateVal = Format(Date, "yyyy-mm-dd")
    End If
    tokens.Add "{document_title}", sDocTitle
    tokens.Add "{organization_name}", sOrgName
    tokens.Add "{classification}", sClassification
    tokens.Add "{author}", sAuthor
    tokens.Add "{version}", sVersion
    tokens.Add "{date}", dateVal

    ' --- Create Word document (late binding — no reference needed) ---
    Application.StatusBar = "xlsx2docx: Creating Word document..."
    Dim wdApp As Object
    Set wdApp = CreateObject("Word.Application")
    wdApp.Visible = False

    Dim doc As Object
    Set doc = wdApp.Documents.Add

    ' --- Apply page layout ---
    ApplyPageLayout doc, wdApp, sPageSize, sOrientation, dMarginTop, dMarginBottom, dMarginLeft, dMarginRight

    ' --- Apply body style ---
    ApplyBodyStyle doc, sBodyFont, nBodySize, dBodySpacing

    ' --- Apply heading style ---
    ApplyHeadingStyle doc, nHeadingLevel, sHeadingFont, nHeadingSize, bHeadingBold, sHeadingColor

    ' --- Apply header/footer ---
    ApplyHeaderFooter doc, tokens, _
        sHeaderLeft, sHeaderCenter, sHeaderRight, sHeaderFont, nHeaderSize, sHeaderColor, _
        sFooterLeft, sFooterCenter, sFooterRight, sFooterFont, nFooterSize, sFooterColor

    ' --- Sheet heading ---
    If bAddSheetHeading Then
        Dim sheetHeadingPara As Object
        Set sheetHeadingPara = doc.Content.Paragraphs(doc.Content.Paragraphs.Count).Range
        sheetHeadingPara.InsertAfter ws.Name
        sheetHeadingPara.Style = doc.Styles("Heading 1")
        doc.Content.InsertParagraphAfter
    End If

    ' --- Remove the default empty paragraph at the start ---
    ' Word always starts with one empty paragraph; we'll write into it.
    Dim rng As Object
    Set rng = doc.Content
    rng.Collapse 0  ' wdCollapseEnd

    ' --- Process rows ---
    Dim r As Long
    Dim controlCount As Long: controlCount = 0

    For r = nDataStartRow To lastRow
        Dim headingText As String
        headingText = Trim(CStr(ws.Cells(r, headingCol).Value & ""))

        ' Skip empty headings
        If bSkipEmptyHeading And Len(headingText) = 0 Then GoTo NextRow

        ' --- Insert heading ---
        If Len(headingText) > 0 Then
            Set rng = doc.Content
            rng.Collapse 0  ' wdCollapseEnd
            rng.InsertAfter headingText
            rng.Style = doc.Styles("Heading " & nHeadingLevel)
            rng.InsertParagraphAfter
        End If

        ' --- Insert key-value content for other columns ---
        Dim c As Long
        For c = 1 To lastCol
            If c = headingCol Then GoTo NextCol

            Dim colName As String
            colName = Trim(CStr(ws.Cells(nHeaderRow, c).Value & ""))
            If Len(colName) = 0 Then GoTo NextCol

            ' Check include/exclude
            If includeSet.Count > 0 Then
                If Not includeSet.Exists(LCase(colName)) Then GoTo NextCol
            End If
            If excludeSet.Count > 0 Then
                If excludeSet.Exists(LCase(colName)) Then GoTo NextCol
            End If

            ' Get cell value
            Dim cellVal As String
            cellVal = Trim(CStr(ws.Cells(r, c).Value & ""))
            If Len(cellVal) = 0 Then GoTo NextCol

            ' Apply rename
            Dim displayLabel As String
            If renameMap.Exists(LCase(colName)) Then
                displayLabel = renameMap(LCase(colName))
            Else
                displayLabel = colName
            End If

            ' Insert label: value paragraph
            Set rng = doc.Content
            rng.Collapse 0  ' wdCollapseEnd

            ' Add label run (bold, colored)
            rng.InsertAfter displayLabel & ": "
            Dim labelRange As Object
            Set labelRange = doc.Content
            labelRange.Start = labelRange.End - Len(displayLabel & ": ")
            labelRange.End = labelRange.Start + Len(displayLabel & ": ")
            With labelRange.Font
                .Name = sLabelFont
                .Size = nLabelSize
                .Bold = bLabelBold
                .Color = HexToRGB(sLabelColor)
            End With

            ' Handle multi-line cell values
            ' Chr(10) = newline in Excel, Chr(11) = vertical tab = Word soft return
            ' Using Chr(11) keeps multi-line values within the same paragraph,
            ' preserving formatting and spacing (unlike vbCr which creates new paragraphs).
            Dim valueText As String
            valueText = Replace(cellVal, Chr(10), Chr(11))

            ' Add value run (normal body style)
            Set rng = doc.Content
            rng.Collapse 0
            rng.InsertAfter valueText
            Dim valueRange As Object
            Set valueRange = doc.Content
            valueRange.Start = valueRange.End - Len(valueText)
            valueRange.End = valueRange.Start + Len(valueText)
            With valueRange.Font
                .Name = sBodyFont
                .Size = nBodySize
                .Bold = False
                .Color = RGB(0, 0, 0)
            End With

            ' End paragraph
            Set rng = doc.Content
            rng.Collapse 0
            rng.InsertParagraphAfter

NextCol:
        Next c

        controlCount = controlCount + 1

        ' Progress update every 25 rows
        If controlCount Mod 25 = 0 Then
            Application.StatusBar = "xlsx2docx: Processing row " & r & " of " & lastRow & "..."
        End If

NextRow:
    Next r

    ' --- Remove trailing empty paragraph ---
    If doc.Content.Paragraphs.Count > 1 Then
        Dim lastPara As Object
        Set lastPara = doc.Content.Paragraphs(doc.Content.Paragraphs.Count)
        If Len(Trim(lastPara.Range.Text)) <= 1 Then  ' vbCr = 1 char
            lastPara.Range.Delete
        End If
    End If

    ' --- Save document ---
    Application.StatusBar = "xlsx2docx: Saving " & outputPath & "..."
    doc.SaveAs2 FileName:=outputPath, FileFormat:=12  ' wdFormatXMLDocument = 12 (.docx)
    doc.Close False
    wdApp.Quit False

    Set doc = Nothing
    Set wdApp = Nothing

    Application.StatusBar = False

    ' --- Build status message ---
    Dim configSource As String
    If cfg.Count > 0 Then
        configSource = "Config sheet (" & cfg.Count & " settings loaded)"
    Else
        configSource = "Built-in defaults (no Config sheet found)"
    End If

    MsgBox "Document created successfully!" & vbCrLf & vbCrLf & _
           "Controls processed: " & controlCount & vbCrLf & _
           "Configuration: " & configSource & vbCrLf & _
           "Output: " & outputPath, vbInformation, "xlsx2docx"

    Exit Sub

ErrHandler:
    Application.StatusBar = False
    Dim errMsg As String
    errMsg = "Error " & Err.Number & ": " & Err.Description

    ' Clean up Word if it's still running
    On Error Resume Next
    If Not doc Is Nothing Then doc.Close False
    If Not wdApp Is Nothing Then wdApp.Quit False
    Set doc = Nothing
    Set wdApp = Nothing
    On Error GoTo 0

    MsgBox errMsg, vbCritical, "xlsx2docx Error"
End Sub


'===============================================================================
' HELPER FUNCTIONS
'===============================================================================

'--- Find a column by header name (case-insensitive). Returns 0 if not found. ---
Private Function FindColumnByName(ws As Worksheet, colName As String, headerRow As Long) As Long
    Dim lastCol As Long
    lastCol = ws.Cells(headerRow, ws.Columns.Count).End(xlToLeft).Column

    Dim c As Long
    Dim target As String: target = LCase(Trim(colName))

    For c = 1 To lastCol
        If LCase(Trim(CStr(ws.Cells(headerRow, c).Value & ""))) = target Then
            FindColumnByName = c
            Exit Function
        End If
    Next c

    FindColumnByName = 0
End Function


'--- Parse comma-separated string into a Dictionary (lowercase keys). ---
Private Function ParseCsvToDict(csv As String) As Object
    Dim d As Object: Set d = CreateObject("Scripting.Dictionary")
    If Len(Trim(csv)) = 0 Then
        Set ParseCsvToDict = d
        Exit Function
    End If

    Dim parts() As String: parts = Split(csv, ",")
    Dim i As Long
    For i = LBound(parts) To UBound(parts)
        Dim key As String: key = LCase(Trim(parts(i)))
        If Len(key) > 0 And Not d.Exists(key) Then
            d.Add key, True
        End If
    Next i
    Set ParseCsvToDict = d
End Function


'--- Parse rename map from "OldName=NewLabel,..." format. ---
Private Function ParseRenameMap(renameStr As String) As Object
    Dim d As Object: Set d = CreateObject("Scripting.Dictionary")
    If Len(Trim(renameStr)) = 0 Then
        Set ParseRenameMap = d
        Exit Function
    End If

    Dim pairs() As String: pairs = Split(renameStr, ",")
    Dim i As Long
    For i = LBound(pairs) To UBound(pairs)
        Dim eqPos As Long: eqPos = InStr(pairs(i), "=")
        If eqPos > 1 Then
            Dim oldName As String: oldName = LCase(Trim(Left(pairs(i), eqPos - 1)))
            Dim newLabel As String: newLabel = Trim(Mid(pairs(i), eqPos + 1))
            If Len(oldName) > 0 And Len(newLabel) > 0 And Not d.Exists(oldName) Then
                d.Add oldName, newLabel
            End If
        End If
    Next i
    Set ParseRenameMap = d
End Function


'--- Resolve tokens in a string (replaces {token} with values). ---
Private Function ResolveTokens(text As String, tokens As Object) As String
    Dim result As String: result = text
    Dim k As Variant
    For Each k In tokens.Keys
        result = Replace(result, CStr(k), CStr(tokens(k)))
    Next k
    ResolveTokens = result
End Function


'--- Convert 6-digit hex color string to Long (RGB for Word). ---
Private Function HexToRGB(hexStr As String) As Long
    Dim s As String: s = Replace(Trim(hexStr), "#", "")
    If Len(s) < 6 Then s = "2F5496"  ' fallback to DPS blue

    On Error GoTo Fallback
    Dim r As Long: r = CLng("&H" & Mid(s, 1, 2))
    Dim g As Long: g = CLng("&H" & Mid(s, 3, 2))
    Dim b As Long: b = CLng("&H" & Mid(s, 5, 2))
    HexToRGB = RGB(r, g, b)
    Exit Function

Fallback:
    HexToRGB = RGB(&H2F, &H54, &H96)
End Function


'--- Apply page size, orientation, and margins. ---
Private Sub ApplyPageLayout(doc As Object, wdApp As Object, _
    sPageSize As String, sOrientation As String, _
    dTop As Double, dBottom As Double, dLeft As Double, dRight As Double)

    Dim sec As Object: Set sec = doc.Sections(1)

    With sec.PageSetup
        ' Margins (in points: 1 inch = 72 points)
        .TopMargin = dTop * 72
        .BottomMargin = dBottom * 72
        .LeftMargin = dLeft * 72
        .RightMargin = dRight * 72

        ' Page size
        If UCase(Trim(sPageSize)) = "A4" Then
            .PageWidth = 595.3   ' 8.27 inches * 72
            .PageHeight = 841.9  ' 11.69 inches * 72
        Else  ' Letter
            .PageWidth = 612     ' 8.5 inches * 72
            .PageHeight = 792    ' 11 inches * 72
        End If

        ' Orientation
        If LCase(Trim(sOrientation)) = "landscape" Then
            .Orientation = 1  ' wdOrientLandscape
        Else
            .Orientation = 0  ' wdOrientPortrait
        End If
    End With
End Sub


'--- Apply body (Normal) style. ---
Private Sub ApplyBodyStyle(doc As Object, sFont As String, nSize As Long, dSpacing As Double)
    On Error Resume Next
    With doc.Styles("Normal").Font
        .Name = sFont
        .Size = nSize
    End With
    With doc.Styles("Normal").ParagraphFormat
        .LineSpacingRule = 5  ' wdLineSpaceMultiple
        .LineSpacing = dSpacing * 12  ' 12 points per line
        .SpaceAfter = 8
    End With
    On Error GoTo 0
End Sub


'--- Apply heading style for the configured heading level. ---
Private Sub ApplyHeadingStyle(doc As Object, nLevel As Long, _
    sFont As String, nSize As Long, bBold As Boolean, sColor As String)

    On Error Resume Next
    Dim styleName As String: styleName = "Heading " & nLevel
    With doc.Styles(styleName).Font
        .Name = sFont
        .Size = nSize
        .Bold = bBold
        .Color = HexToRGB(sColor)
    End With
    With doc.Styles(styleName).ParagraphFormat
        .SpaceBefore = 10
        .SpaceAfter = 4
        .KeepWithNext = True
    End With
    On Error GoTo 0
End Sub


'--- Apply header and footer with token resolution. ---
Private Sub ApplyHeaderFooter(doc As Object, tokens As Object, _
    hLeft As String, hCenter As String, hRight As String, _
    hFont As String, hSize As Long, hColor As String, _
    fLeft As String, fCenter As String, fRight As String, _
    fFont As String, fSize As Long, fColor As String)

    Dim sec As Object: Set sec = doc.Sections(1)

    ' --- Header ---
    Dim hdr As Object: Set hdr = sec.Headers(1)  ' wdHeaderFooterPrimary = 1
    BuildTabStopHF hdr, _
        ResolveTokens(hLeft, tokens), _
        ResolveTokens(hCenter, tokens), _
        ResolveTokens(hRight, tokens), _
        hFont, hSize, hColor, doc

    ' --- Footer ---
    Dim ftr As Object: Set ftr = sec.Footers(1)
    BuildTabStopHF ftr, _
        ResolveTokens(fLeft, tokens), _
        ResolveTokens(fCenter, tokens), _
        ResolveTokens(fRight, tokens), _
        fFont, fSize, fColor, doc
End Sub


'--- Build a header/footer paragraph with left/center/right tab stops. ---
'--- Supports {page} and {pages} tokens as live Word fields. ---
Private Sub BuildTabStopHF(hf As Object, leftText As String, centerText As String, _
                           rightText As String, fontName As String, fontSize As Long, _
                           colorHex As String, doc As Object)

    Dim para As Object: Set para = hf.Range.Paragraphs(1)
    para.Range.text = ""  ' Clear existing content

    ' Calculate usable page width for tab stops
    Dim sec As Object: Set sec = doc.Sections(1)
    Dim usableWidth As Double
    usableWidth = sec.PageSetup.PageWidth - sec.PageSetup.LeftMargin - sec.PageSetup.RightMargin

    ' Set tab stops: center at half, right at full width
    para.Format.TabStops.ClearAll
    para.Format.TabStops.Add Position:=usableWidth / 2, Alignment:=1  ' wdAlignTabCenter
    para.Format.TabStops.Add Position:=usableWidth, Alignment:=2       ' wdAlignTabRight

    Dim rng As Object: Set rng = para.Range
    rng.Collapse 0  ' wdCollapseEnd

    ' Left text
    If Len(leftText) > 0 Then EmitHFText rng, leftText, fontName, fontSize, colorHex

    ' Tab to center
    rng.Collapse 0
    rng.InsertAfter vbTab
    rng.Collapse 0

    ' Center text
    If Len(centerText) > 0 Then EmitHFText rng, centerText, fontName, fontSize, colorHex

    ' Tab to right
    rng.Collapse 0
    rng.InsertAfter vbTab
    rng.Collapse 0

    ' Right text
    If Len(rightText) > 0 Then EmitHFText rng, rightText, fontName, fontSize, colorHex
End Sub


'--- Emit text into header/footer, inserting PAGE/NUMPAGES fields for {page}/{pages}. ---
Private Sub EmitHFText(rng As Object, text As String, fontName As String, _
                       fontSize As Long, colorHex As String)

    ' Split on {page} and {pages} tokens
    Dim parts() As String
    Dim temp As String: temp = text

    ' Replace {pages} first (longer token) to avoid partial match with {page}
    temp = Replace(temp, "{pages}", Chr(1))
    temp = Replace(temp, "{page}", Chr(2))

    Dim i As Long
    Dim pos As Long: pos = 1
    Dim ch As String

    For i = 1 To Len(temp)
        ch = Mid(temp, i, 1)

        If ch = Chr(1) Or ch = Chr(2) Then
            ' Flush text before this token
            If i > pos Then
                Dim textBefore As String: textBefore = Mid(temp, pos, i - pos)
                rng.Collapse 0
                rng.InsertAfter textBefore
                FormatLastRun rng, fontName, fontSize, colorHex
            End If

            ' Insert field
            rng.Collapse 0
            If ch = Chr(2) Then
                ' {page} -> PAGE field
                rng.Fields.Add Range:=rng, Type:=-1, text:="PAGE", PreserveFormatting:=False
            Else
                ' {pages} -> NUMPAGES field
                rng.Fields.Add Range:=rng, Type:=-1, text:="NUMPAGES", PreserveFormatting:=False
            End If
            ' Move past the inserted field
            rng.Collapse 0

            pos = i + 1
        End If
    Next i

    ' Flush remaining text
    If pos <= Len(temp) Then
        Dim remaining As String: remaining = Mid(temp, pos)
        rng.Collapse 0
        rng.InsertAfter remaining
        FormatLastRun rng, fontName, fontSize, colorHex
    End If
End Sub


'--- Format the most recently inserted run in a range. ---
Private Sub FormatLastRun(rng As Object, fontName As String, fontSize As Long, colorHex As String)
    On Error Resume Next
    Dim para As Object: Set para = rng.Paragraphs(rng.Paragraphs.Count)
    If para.Range.Characters.Count > 0 Then
        Dim lastChar As Object
        Set lastChar = para.Range.Characters(para.Range.Characters.Count)
        With lastChar.Font
            .Name = fontName
            .Size = fontSize
            .Color = HexToRGB(colorHex)
        End With
    End If
    On Error GoTo 0
End Sub
