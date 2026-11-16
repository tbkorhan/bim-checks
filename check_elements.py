import ifcopenshell
import ifcopenshell.util.element as el
from openpyxl import Workbook
from collections import Counter

IFC_FILE = "ornek.ifc"  # change to your IFC file name

# element type -> (sheet name, property set, parameters to check)
CHECKS = {
    "IfcWall": ("Walls", "Pset_WallCommon", ["FireRating", "IsExternal", "LoadBearing"]),
    "IfcDoor": ("Doors", "Pset_DoorCommon", ["FireRating", "IsExternal"]),
    "IfcWindow": ("Windows", "Pset_WindowCommon", ["FireRating", "IsExternal"]),
}

model = ifcopenshell.open(IFC_FILE)
wb = Workbook()
wb.remove(wb.active)

summary_rows = []

for ifc_type, (sheet_name, pset_name, params) in CHECKS.items():
    ws = wb.create_sheet(sheet_name)
    ws.append(["GlobalId", "Name"] + params)

    missing_count = Counter()
    total = 0

    for element in model.by_type(ifc_type):
        total += 1
        common = el.get_psets(element).get(pset_name, {})
        row = [element.GlobalId, element.Name]
        for p in params:
            is_missing = common.get(p) in (None, "")
            row.append("MISSING" if is_missing else "OK")
            if is_missing:
                missing_count[p] += 1
        ws.append(row)

    for p in params:
        pct = round(100 * missing_count[p] / total, 1) if total else 0
        summary_rows.append([sheet_name, p, missing_count[p], total, pct])

summary = wb.create_sheet("Summary", 0)
summary.append(["Element Type", "Parameter", "Missing", "Total", "Missing %"])
for row in summary_rows:
    summary.append(row)

wb.save("report.xlsx")
print("report.xlsx created")