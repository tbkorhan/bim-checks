# -*- coding: utf-8 -*-
import codecs
from pyrevit import revit, script, forms
from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInCategory, BuiltInParameter)

doc = revit.doc
output = script.get_output()
SEP = u";"  # use u"," if your Excel opens the CSV as a single column


def cell(value):
    text = u"{0}".format(value).replace(u'"', u'""')
    return u'"' + text + u'"'


walls = (FilteredElementCollector(doc)
         .OfCategory(BuiltInCategory.OST_Walls)
         .WhereElementIsNotElementType()
         .ToElements())

rows = []      # for the on-screen table
csv_rows = []  # for the CSV file
for w in walls:
    wtype = doc.GetElement(w.GetTypeId())
    fire = wtype.get_Parameter(BuiltInParameter.FIRE_RATING)
    if fire is None or not fire.AsString():
        type_name = wtype.get_Parameter(
            BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        level_param = w.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
        level = level_param.AsValueString() if level_param else "-"
        rows.append([output.linkify(w.Id), type_name, level])
        csv_rows.append([str(w.Id), type_name, level])

output.print_md("**Walls:** {}  |  **FireRating missing:** {}".format(
    len(walls), len(rows)))

if rows:
    output.print_table(
        table_data=rows,
        title="Walls with missing FireRating",
        columns=["Element ID (click to select)", "Wall Type", "Base Level"])

    path = forms.save_file(file_ext="csv",
                           default_name="walls_missing_fire_rating")
    if path:
        header = [u"Element ID", u"Wall Type", u"Base Level"]
        with codecs.open(path, "w", "utf-8-sig") as f:
            f.write(SEP.join(cell(h) for h in header) + u"\r\n")
            for r in csv_rows:
                f.write(SEP.join(cell(v) for v in r) + u"\r\n")
        output.print_md("CSV saved: `{}`".format(path))
else:
    output.print_md("All walls have a FireRating.")
