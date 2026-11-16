from pyrevit import revit, script
from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInCategory, BuiltInParameter)

doc = revit.doc
output = script.get_output()

walls = (FilteredElementCollector(doc)
         .OfCategory(BuiltInCategory.OST_Walls)
         .WhereElementIsNotElementType()
         .ToElements())

rows = []
for w in walls:
    wtype = doc.GetElement(w.GetTypeId())
    fire = wtype.get_Parameter(BuiltInParameter.FIRE_RATING)
    if fire is None or not fire.AsString():
        type_name = wtype.get_Parameter(
            BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        level_param = w.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
        level = level_param.AsValueString() if level_param else "-"
        rows.append([output.linkify(w.Id), type_name, level])

output.print_md("**Walls:** {}  |  **FireRating missing:** {}".format(
    len(walls), len(rows)))

if rows:
    output.print_table(
        table_data=rows,
        title="Walls with missing FireRating",
        columns=["Element ID (click to select)", "Wall Type", "Base Level"])
else:
    output.print_md("All walls have a FireRating.")