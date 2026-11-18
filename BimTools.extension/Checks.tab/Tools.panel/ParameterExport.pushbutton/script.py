# -*- coding: utf-8 -*-
import codecs
from pyrevit import revit, script, forms
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory,
                               BuiltInParameter, StorageType, ElementId)

doc = revit.doc
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

FIXED = [u"Element ID", u"Category", u"Type", u"Level"]


def cell(value):
    text = u"{0}".format(value).replace(u'"', u'""')
    return u'"' + text + u'"'


def type_label(etype):
    if etype is not None:
        p = etype.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
        if p and p.AsString():
            return p.AsString()
    return u"-"


def level_label(element):
    try:
        lid = element.LevelId
        if lid is None or lid == ElementId.InvalidElementId:
            return u"-"
        level = doc.GetElement(lid)
        return level.Name if level else u"-"
    except Exception:
        return u"-"


cat_name = forms.SelectFromList.show(
    sorted(CATEGORIES.keys()),
    title="Select a category to export",
    button_name="Next")
if not cat_name:
    script.exit()

elements = list(FilteredElementCollector(doc)
                .OfCategory(CATEGORIES[cat_name])
                .WhereElementIsNotElementType()
                .ToElements())
if not elements:
    forms.alert("No elements found in this category.")
    script.exit()

# Editable text instance parameters (sample of up to 300 elements)
names = set()
for e in elements[:300]:
    for p in e.Parameters:
        if (not p.IsReadOnly) and p.StorageType == StorageType.String:
            names.add(p.Definition.Name)
if not names:
    forms.alert("No editable text parameters found.")
    script.exit()

chosen = forms.SelectFromList.show(
    sorted(names, key=lambda s: s.lower()),
    title="Select text parameters to export",
    multiselect=True,
    button_name="Export")
if not chosen:
    script.exit()

path = forms.save_file(
    file_ext="csv",
    default_name="parameters_{}".format(cat_name.replace(" ", "_")))
if not path:
    script.exit()

with codecs.open(path, "w", "utf-8-sig") as f:
    header = FIXED + list(chosen)
    f.write(SEP.join(cell(h) for h in header) + u"\r\n")
    for e in elements:
        etype = doc.GetElement(e.GetTypeId())
        values = [str(e.Id), cat_name, type_label(etype), level_label(e)]
        for name in chosen:
            p = e.LookupParameter(name)
            if p is not None and p.StorageType == StorageType.String:
                values.append(p.AsString() or u"")
            else:
                values.append(u"")
        f.write(SEP.join(cell(v) for v in values) + u"\r\n")

forms.alert("Exported {} elements.\n\n{}".format(len(elements), path))