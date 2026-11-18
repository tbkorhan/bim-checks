# -*- coding: utf-8 -*-
from pyrevit import revit, script
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory,
                               BuiltInParameter)

doc = revit.doc
output = script.get_output()


def param_text(element, bip):
    p = element.get_Parameter(bip)
    if p is None:
        return ""
    return p.AsString() or ""


rooms = (FilteredElementCollector(doc)
         .OfCategory(BuiltInCategory.OST_Rooms)
         .WhereElementIsNotElementType()
         .ToElements())

unplaced = []
not_enclosed = []
unnamed = []
by_number = {}

for r in rooms:
    number = param_text(r, BuiltInParameter.ROOM_NUMBER)
    name = param_text(r, BuiltInParameter.ROOM_NAME)
    level = r.Level.Name if r.Level else "-"

    if r.Location is None:
        unplaced.append([output.linkify(r.Id), number, name])
        continue  # unplaced rooms have no area, skip the other checks

    if r.Area == 0:
        not_enclosed.append([output.linkify(r.Id), number, name, level])

    if not name.strip() or name.strip() == "Room":
        unnamed.append([output.linkify(r.Id), number, level])

    by_number.setdefault(number, []).append(r)

duplicates = []
for number, group in by_number.items():
    if number and len(group) > 1:
        for r in group:
            name = param_text(r, BuiltInParameter.ROOM_NAME)
            level = r.Level.Name if r.Level else "-"
            duplicates.append([output.linkify(r.Id), number, name, level])

output.print_table(
    table_data=[["Total rooms", len(rooms)],
                ["Not placed", len(unplaced)],
                ["Not enclosed (area = 0)", len(not_enclosed)],
                ["Unnamed or default name", len(unnamed)],
                ["Duplicate numbers", len(duplicates)]],
    title="Room check summary",
    columns=["Check", "Count"])


def show(title, rows, columns):
    if rows:
        output.print_table(table_data=rows, title=title, columns=columns)


show("Rooms not placed", unplaced,
     ["Element ID (click to select)", "Number", "Name"])
show("Rooms not enclosed", not_enclosed,
     ["Element ID (click to select)", "Number", "Name", "Level"])
show("Unnamed rooms", unnamed,
     ["Element ID (click to select)", "Number", "Level"])
show("Duplicate room numbers", duplicates,
     ["Element ID (click to select)", "Number", "Name", "Level"])