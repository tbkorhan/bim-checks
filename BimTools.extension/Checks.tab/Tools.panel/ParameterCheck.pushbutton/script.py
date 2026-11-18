# -*- coding: utf-8 -*-
import codecs
from pyrevit import revit, script, forms
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory,
                               BuiltInParameter, StorageType, ElementId)

doc = revit.doc
output = script.get_output()
SEP = u";"  # use u"," if Excel opens the CSV as a single column

CATEGORIES = {
    "Walls": BuiltInCategory.OST_Walls,
    "Doors": BuiltInCategory.OST_Doors,
    "Windows": BuiltInCategory.OST_Windows,
    "Floors": BuiltInCategory.OST_Floors,
    "Ceilings": BuiltInCategory.OST_Ceilings,
    "Roofs": BuiltInCategory.OST_Roofs,
    "Rooms": BuiltInCategory.OST_Rooms,
    "Columns": BuiltInCategory.OST_Columns,
    "Structural Columns": BuiltInCategory.OST_StructuralColumns,
    "Structural Framing": BuiltInCategory.OST_StructuralFraming,
    "Furniture": BuiltInCategory.OST_Furniture,
    "Generic Models": BuiltInCategory.OST_GenericModel,
}


def cell(value):
    text = u"{0}".format(value).replace(u'"', u'""')
    return u'"' + text + u'"'


def is_empty(p):
    if p is None or not p.HasValue:
        return True
    if p.StorageType == StorageType.String:
        return not (p.AsString() or "").strip()
    if p.StorageType == StorageType.ElementId:
        return p.AsElementId() == ElementId.InvalidElementId
    return False  # numbers (including 0) and Yes/No count as filled


def find_param(element, etype, name):
    p = element.LookupParameter(name)
    if p is None and etype is not None:
        p = etype.LookupParameter(name)
    return p


def type_label(element, etype):
    if etype is not None:
        p = etype.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
        if p and p.AsString():
            return p.AsString()
    try:
        return element.Name
    except Exception:
        return "-"


def level_label(element):
    lid = element.LevelId
    if lid is None or lid == ElementId.InvalidElementId:
        return "-"
    level = doc.GetElement(lid)
    return level.Name if level else "-"


# Step 1: choose categories
chosen = forms.SelectFromList.show(
    sorted(CATEGORIES.keys()),
    title="Select categories to check",
    multiselect=True,
    button_name="Next")
if not chosen:
    script.exit()

elements_by_cat = {}
for cat_name in chosen:
    elements_by_cat[cat_name] = list(
        FilteredElementCollector(doc)
        .OfCategory(CATEGORIES[cat_name])
        .WhereElementIsNotElementType()
        .ToElements())

if not any(elements_by_cat.values()):
    forms.alert("No elements found in the selected categories.")
    script.exit()

# Step 2: collect parameter names (sample of up to 300 elements per category)
names = set()
for elements in elements_by_cat.values():
    for e in elements[:300]:
        for p in e.Parameters:
            names.add(p.Definition.Name)
        etype = doc.GetElement(e.GetTypeId())
        if etype is not None:
            for p in etype.Parameters:
                names.add(p.Definition.Name)

param_name = forms.SelectFromList.show(
    sorted(names, key=lambda s: s.lower()),
    title="Select the parameter to check",
    button_name="Check")
if not param_name:
    script.exit()

# Step 3: check
summary = []
rows = []
csv_rows = []
for cat_name in chosen:
    elements = elements_by_cat[cat_name]
    missing = 0
    for e in elements:
        etype = doc.GetElement(e.GetTypeId())
        p = find_param(e, etype, param_name)
        if is_empty(p):
            missing += 1
            status = "Not found" if p is None else "Empty"
            t = type_label(e, etype)
            lvl = level_label(e)
            rows.append([cat_name, output.linkify(e.Id), t, lvl, status])
            csv_rows.append([cat_name, str(e.Id), t, lvl, status])
    summary.append([cat_name, len(elements), missing])

output.print_md("**Parameter checked:** {}".format(param_name))
output.print_table(
    table_data=summary,
    title="Summary",
    columns=["Category", "Total", "Missing"])

if rows:
    output.print_table(
        table_data=rows,
        title="Elements with missing '{}'".format(param_name),
        columns=["Category", "Element ID (click to select)",
                 "Type", "Level", "Status"])

    path = forms.save_file(file_ext="csv", default_name="parameter_check")
    if path:
        header = [u"Category", u"Element ID", u"Type", u"Level", u"Status"]
        with codecs.open(path, "w", "utf-8-sig") as f:
            f.write(SEP.join(cell(h) for h in header) + u"\r\n")
            for r in csv_rows:
                f.write(SEP.join(cell(v) for v in r) + u"\r\n")
        output.print_md("CSV saved: `{}`".format(path))
else:
    output.print_md("All elements have a value for '{}'.".format(param_name))