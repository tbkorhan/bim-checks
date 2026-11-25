# -*- coding: utf-8 -*-
from pyrevit import routes, revit, HOST_APP
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory,
                               BuiltInParameter, StorageType, ElementId)

api = routes.API("bimtools")

CATEGORIES = {
    "Walls": BuiltInCategory.OST_Walls,
    "Doors": BuiltInCategory.OST_Doors,
    "Windows": BuiltInCategory.OST_Windows,
    "Floors": BuiltInCategory.OST_Floors,
    "Rooms": BuiltInCategory.OST_Rooms,
}
MAX_ROWS = 200


def is_empty(p):
    if p is None or not p.HasValue:
        return True
    if p.StorageType == StorageType.String:
        return not (p.AsString() or "").strip()
    if p.StorageType == StorageType.ElementId:
        return p.AsElementId() == ElementId.InvalidElementId
    return False


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


def level_label(doc, element):
    try:
        lid = element.LevelId
    except Exception:
        return "-"
    if lid is None or lid == ElementId.InvalidElementId:
        return "-"
    level = doc.GetElement(lid)
    return level.Name if level else "-"


def collect(doc, category):
    return list(FilteredElementCollector(doc)
                .OfCategory(CATEGORIES[category])
                .WhereElementIsNotElementType().ToElements())


@api.route("/ping/")
def ping():
    return routes.make_response(
        data={"status": "ok", "revit_version": HOST_APP.version})


@api.route("/wallcount/")
def wallcount():
    doc = revit.doc
    if doc is None:
        return routes.make_response(
            data={"error": "no model open"}, status=400)
    count = (FilteredElementCollector(doc)
             .OfCategory(BuiltInCategory.OST_Walls)
             .WhereElementIsNotElementType().GetElementCount())
    return routes.make_response(data={"title": doc.Title, "walls": count})


@api.route("/params/<category>/")
def params(category):
    doc = revit.doc
    if doc is None:
        return routes.make_response(
            data={"error": "no model open"}, status=400)
    if category not in CATEGORIES:
        return routes.make_response(
            data={"error": "unknown category",
                  "valid": sorted(CATEGORIES.keys())}, status=400)
    names = set()
    for e in collect(doc, category)[:50]:
        for p in e.Parameters:
            names.add(p.Definition.Name)
        etype = doc.GetElement(e.GetTypeId())
        if etype is not None:
            for p in etype.Parameters:
                names.add(p.Definition.Name)
    return routes.make_response(
        data={"category": category, "parameters": sorted(names)})


@api.route("/missing/<category>/<param_name>/")
def missing(category, param_name):
    doc = revit.doc
    if doc is None:
        return routes.make_response(
            data={"error": "no model open"}, status=400)
    if category not in CATEGORIES:
        return routes.make_response(
            data={"error": "unknown category",
                  "valid": sorted(CATEGORIES.keys())}, status=400)
    elements = collect(doc, category)
    rows = []
    count = 0
    for e in elements:
        etype = doc.GetElement(e.GetTypeId())
        p = find_param(e, etype, param_name)
        if is_empty(p):
            count += 1
            if len(rows) < MAX_ROWS:
                rows.append({
                    "id": str(e.Id),
                    "type": type_label(e, etype),
                    "level": level_label(doc, e),
                    "status": "Not found" if p is None else "Empty",
                })
    return routes.make_response(data={
        "category": category, "parameter": param_name,
        "total": len(elements), "missing": count,
        "shown": len(rows), "elements": rows})