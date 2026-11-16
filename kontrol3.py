import ifcopenshell
import ifcopenshell.util.element as el
from openpyxl import Workbook
from collections import Counter

model = ifcopenshell.open("ornek.ifc")
kontrol_listesi = ["FireRating", "IsExternal", "LoadBearing"]

wb = Workbook()
ws = wb.active
ws.title = "Duvarlar"
ws.append(["GlobalId", "Duvar Adı"] + kontrol_listesi)

sayac = Counter()
toplam = 0

for wall in model.by_type("IfcWall"):
    toplam += 1
    common = el.get_psets(wall).get("Pset_WallCommon", {})
    satir = [wall.GlobalId, wall.Name]
    for p in kontrol_listesi:
        eksik = common.get(p) in (None, "")
        satir.append("EKSİK" if eksik else "OK")
        if eksik:
            sayac[p] += 1
    ws.append(satir)

ozet = wb.create_sheet("Özet")
ozet.append(["Parametre", "Eksik Sayısı", "Toplam Duvar", "Eksik %"])
for p in kontrol_listesi:
    ozet.append([p, sayac[p], toplam, round(100 * sayac[p] / toplam, 1)])

wb.save("rapor2.xlsx")
print("rapor2.xlsx oluşturuldu")