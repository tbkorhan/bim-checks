import ifcopenshell
import ifcopenshell.util.element as el
from openpyxl import Workbook
from collections import Counter

IFC_FILE = "ornek.ifc"  # change to your IFC file name
PARAMETERS = ["FireRating", "IsExternal", "LoadBearing"]

model = ifcopenshell.open(IFC_FILE)

wb = Workbook()
ws = wb.active
ws.title = "Walls"
ws.append(["GlobalId", "Wall Name"] + PARAMETERS)

missing_count = Counter()
total = 0

for wall in model.by_type("IfcWall"):
    total += 1
    common = el.get_psets(wall).get("Pset_WallCommon", {})
    row = [wall.GlobalId, wall.Name]
    for p in PARAMETERS:
        is_missing = common.get(p) in (None, "")
        row.append("MISSING" if is_missing else "OK")
        if is_missing:
            missing_count[p] += 1
    ws.append(row)

summary = wb.create_sheet("Summary")
summary.append(["Parameter", "Missing", "Total Walls", "Missing %"])
for p in PARAMETERS:
    summary.append([p, missing_count[p], total, round(100 * missing_count[p] / total, 1)])

wb.save("report.xlsx")
print("report.xlsx created")