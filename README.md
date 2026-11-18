# BIM Checks for Revit and IFC

Small Python tools that check BIM models for missing data, for use by BIM coordinators.

## IFC checker (Python script)
`check_elements.py` reads an IFC model exported from Revit, checks walls, doors and windows for missing parameters (FireRating, IsExternal, LoadBearing) and writes `report.xlsx` with a summary sheet.

### Requirements
- Python 3
- `pip install ifcopenshell openpyxl`

### Usage
1. Export your Revit model as IFC (with "Export IFC common property sets" enabled)
2. Put the file next to the script and set its name in `IFC_FILE` at the top of the script
3. Run: `python check_elements.py`

![Summary sheet](summary.PNG)

## pyRevit extension
`BimTools.extension` adds a "Checks" tab to Revit with seven tools. Five are read-only checks. Results open in a table with clickable element IDs, and most can export to CSV. `ParameterImport` is the only tool that writes to the model, and it always shows a preview and asks for confirmation first. Try it on a copy of your model; one Ctrl+Z undoes the whole import.

| Tool | What it checks |
|---|---|
| ElementCheck | Walls, doors and windows with a missing FireRating |
| ModelHealth | Warnings, imported CAD files, in-place families, views not on sheets |
| RoomCheck | Unplaced, unenclosed, unnamed and duplicate-number rooms |
| ParameterCheck | Pick categories and any parameter, list elements where it is empty |
| NamingCheck | Sheet numbers and view names against a configurable pattern |
| ParameterExport | Exports editable text parameters of one category to CSV for editing in Excel |
| ParameterImport | Reads the edited CSV, shows a preview of the changes, then writes them to the model after confirmation |

### Install
1. Install [pyRevit](https://github.com/pyrevitlabs/pyRevit).
2. Put `BimTools.extension` in a folder, then in pyRevit Settings add that folder under Custom Extension Directories.
3. Click Save Settings and Reload.


![Summary sheet](pyrevitbutton.png)

![Summary sheet](namingcheck.png)

