# -*- coding: utf-8 -*-
from pyrevit import revit, script
from Autodesk.Revit.DB import (FilteredElementCollector, ImportInstance,
                               FamilyInstance, View, ViewSheet, ViewType)

doc = revit.doc
output = script.get_output()

# 1. Warnings
warning_count = len(list(doc.GetWarnings()))

# 2. Imported CAD files (linked files are fine, imports are not)
cad_rows = []
for e in FilteredElementCollector(doc).OfClass(ImportInstance):
    if not e.IsLinked:
        etype = doc.GetElement(e.GetTypeId())
        name = etype.Name if etype else "-"
        cad_rows.append([output.linkify(e.Id), name])

# 3. In-place families
inplace_rows = []
for e in FilteredElementCollector(doc).OfClass(FamilyInstance):
    symbol = e.Symbol
    if symbol is not None and symbol.Family.IsInPlace:
        cat = e.Category.Name if e.Category else "-"
        inplace_rows.append([output.linkify(e.Id), symbol.Family.Name, cat])

# 4. Views that are not placed on any sheet
CHECK_TYPES = [ViewType.FloorPlan, ViewType.CeilingPlan, ViewType.Elevation,
               ViewType.Section, ViewType.Detail, ViewType.ThreeD,
               ViewType.DraftingView, ViewType.Legend, ViewType.AreaPlan,
               ViewType.EngineeringPlan]

placed = set()
for sheet in FilteredElementCollector(doc).OfClass(ViewSheet):
    for vid in sheet.GetAllPlacedViews():
        placed.add(str(vid))

view_rows = []
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate or v.ViewType not in CHECK_TYPES:
        continue
    if str(v.Id) not in placed:
        view_rows.append([output.linkify(v.Id), v.Name, str(v.ViewType)])

# Output
output.print_table(
    table_data=[["Warnings", warning_count],
                ["Imported CAD files", len(cad_rows)],
                ["In-place families", len(inplace_rows)],
                ["Views not on sheets", len(view_rows)]],
    title="Model health summary",
    columns=["Check", "Count"])


def show(title, rows, columns):
    if rows:
        output.print_table(table_data=rows, title=title, columns=columns)


show("Imported CAD files", cad_rows,
     ["Element ID (click to select)", "Name"])
show("In-place families", inplace_rows,
     ["Element ID (click to select)", "Family", "Category"])
show("Views not on sheets", view_rows,
     ["Element ID", "View Name", "Type"])