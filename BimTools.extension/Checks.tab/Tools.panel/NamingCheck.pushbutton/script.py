# -*- coding: utf-8 -*-
import re
from pyrevit import revit, script
from Autodesk.Revit.DB import (FilteredElementCollector, View, ViewSheet,
                               ViewType)

doc = revit.doc
output = script.get_output()

# ---- Edit these two settings to match your project standard ----
# Sheet numbers must match this pattern (accepts A-101, A101, G001, S-1204)
SHEET_NUMBER_PATTERN = r"^[A-Z]\d{3}$"

# View names that look like Revit defaults or copies
DEFAULT_VIEW_PATTERNS = [
    r"^Section \d+$", r"^Elevation \d+ - [a-z]$", r"^Detail \d+$",
    r"^Callout \d+$", r"^Drafting \d+$", r"^Legend \d+$",
    r"^\{3D\}$", r"^3D View \d+$", r"(?i)\bcopy\b",
]
# -----------------------------------------------------------------

sheet_re = re.compile(SHEET_NUMBER_PATTERN)
view_res = [re.compile(p) for p in DEFAULT_VIEW_PATTERNS]


def whitespace_issue(text):
    return text != text.strip() or "  " in text


# Sheets
sheet_rows = []
for s in FilteredElementCollector(doc).OfClass(ViewSheet):
    number = s.SheetNumber or ""
    name = s.Name or ""
    problems = []
    if not sheet_re.match(number):
        problems.append("Number does not match pattern")
    if not name.strip():
        problems.append("Empty name")
    if whitespace_issue(number) or whitespace_issue(name):
        problems.append("Extra spaces")
    if problems:
        sheet_rows.append([output.linkify(s.Id), number, name,
                           "; ".join(problems)])

# Views
CHECK_TYPES = [ViewType.FloorPlan, ViewType.CeilingPlan, ViewType.Elevation,
               ViewType.Section, ViewType.Detail, ViewType.ThreeD,
               ViewType.DraftingView, ViewType.Legend, ViewType.AreaPlan,
               ViewType.EngineeringPlan]

view_rows = []
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate or v.ViewType not in CHECK_TYPES:
        continue
    name = v.Name or ""
    problems = []
    if any(r.search(name) for r in view_res):
        problems.append("Default or copied name")
    if whitespace_issue(name):
        problems.append("Extra spaces")
    if problems:
        view_rows.append([output.linkify(v.Id), name, str(v.ViewType),
                          "; ".join(problems)])

output.print_table(
    table_data=[["Sheets with issues", len(sheet_rows)],
                ["Views with issues", len(view_rows)]],
    title="Naming check summary",
    columns=["Check", "Count"])

if sheet_rows:
    output.print_table(
        table_data=sheet_rows,
        title="Sheet issues",
        columns=["Element ID", "Number", "Name", "Issue"])
if view_rows:
    output.print_table(
        table_data=view_rows,
        title="View issues",
        columns=["Element ID", "View Name", "Type", "Issue"])