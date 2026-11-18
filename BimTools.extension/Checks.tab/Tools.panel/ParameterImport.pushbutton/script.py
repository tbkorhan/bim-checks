# -*- coding: utf-8 -*-
from System import Int64
from pyrevit import revit, script, forms
from Autodesk.Revit.DB import ElementId, StorageType

doc = revit.doc
output = script.get_output()
FIXED = [u"Element ID", u"Category", u"Type", u"Level"]


def read_text(path):
    with open(path, "rb") as f:
        data = f.read()
    for enc in ("utf-8-sig", "cp1254"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("cp1252", "replace")


def parse_csv(text, sep):
    rows, row, field = [], [], []
    in_quotes = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_quotes:
            if c == u'"':
                if i + 1 < n and text[i + 1] == u'"':
                    field.append(u'"')
                    i += 1
                else:
                    in_quotes = False
            else:
                field.append(c)
        else:
            if c == u'"':
                in_quotes = True
            elif c == sep:
                row.append(u"".join(field))
                field = []
            elif c == u"\n":
                row.append(u"".join(field))
                field = []
                rows.append(row)
                row = []
            elif c == u"\r":
                pass
            else:
                field.append(c)
        i += 1
    if field or row:
        row.append(u"".join(field))
        rows.append(row)
    return [r for r in rows if any(x.strip() for x in r)]


def make_id(value):
    try:
        return ElementId(Int64(value))
    except Exception:
        return ElementId(int(value))


path = forms.pick_file(file_ext="csv")
if not path:
    script.exit()

text = read_text(path)
first_line = text.split(u"\n")[0]
sep = u";" if first_line.count(u";") >= first_line.count(u",") else u","
rows = parse_csv(text, sep)
if len(rows) < 2:
    forms.alert("The file has no data rows.")
    script.exit()

header = [h.strip() for h in rows[0]]
if u"Element ID" not in header:
    forms.alert("No 'Element ID' column found. Use a file made by ParameterExport.")
    script.exit()

id_col = header.index(u"Element ID")
param_cols = [(i, h) for i, h in enumerate(header) if h and h not in FIXED]
if not param_cols:
    forms.alert("No parameter columns found.")
    script.exit()

changes = []
skipped = []
for row in rows[1:]:
    id_text = row[id_col].strip() if len(row) > id_col else u""
    try:
        element = doc.GetElement(make_id(int(id_text)))
    except Exception:
        element = None
    if element is None:
        skipped.append([id_text, u"-", u"Unknown or deleted Element ID"])
        continue
    for i, name in param_cols:
        new = row[i] if i < len(row) else u""
        p = element.LookupParameter(name)
        if p is None:
            skipped.append([id_text, name, u"Parameter not found"])
        elif p.IsReadOnly:
            skipped.append([id_text, name, u"Read-only"])
        elif p.StorageType != StorageType.String:
            skipped.append([id_text, name, u"Not a text parameter"])
        else:
            old = p.AsString() or u""
            if old != new:
                changes.append((element, name, old, new))

if skipped:
    output.print_table(table_data=skipped, title="Skipped",
                       columns=["Element ID", "Parameter", "Reason"])

if not changes:
    output.print_md("**No changes found.** The model already matches the file.")
    script.exit()

output.print_table(
    table_data=[[output.linkify(e.Id), n, o, v] for e, n, o, v in changes],
    title="Proposed changes ({})".format(len(changes)),
    columns=["Element ID", "Parameter", "Current value", "New value"])

confirmed = forms.alert(
    "{} changes will be written to the model.\nContinue?".format(len(changes)),
    sub_msg="Tip: work on a copy. You can undo with Ctrl+Z (one step).",
    title="Import parameters",
    yes=True, no=True)
if not confirmed:
    output.print_md("Cancelled. Nothing was changed.")
    script.exit()

applied = 0
failed = []
with revit.Transaction("Import parameters from CSV"):
    for element, name, old, new in changes:
        try:
            p = element.LookupParameter(name)
            if p.Set(new):
                applied += 1
            else:
                failed.append([output.linkify(element.Id), name, u"Set returned False"])
        except Exception as ex:
            failed.append([output.linkify(element.Id), name, str(ex)])

output.print_md("**Applied:** {}  |  **Failed:** {}".format(applied, len(failed)))
if failed:
    output.print_table(table_data=failed, title="Failed",
                       columns=["Element ID", "Parameter", "Reason"])