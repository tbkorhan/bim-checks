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

## Claude connection (revit-mcp)

[`revit-mcp`](revit-mcp/) is a small MCP server that lets Claude read data from an open Revit model.

```
Claude Desktop -> MCP server (Python, uv) -> pyRevit Routes -> Revit
```

It has four read-only tools: Revit status, wall count, parameter names per category, and elements with a missing parameter value (for example walls without a FireRating). Nothing in the model is modified. The Revit side is a `startup.py` in `BimTools.extension` that exposes these checks as local endpoints through pyRevit Routes.

Tested on Revit 2026. See the [revit-mcp README](revit-mcp/README.md) for setup.

### Install
1. Install [pyRevit](https://github.com/pyrevitlabs/pyRevit).
2. Put `BimTools.extension` in a folder, then in pyRevit Settings add that folder under Custom Extension Directories.
3. Click Save Settings and Reload.


![Summary sheet](pyrevitbutton.png)

![Summary sheet](namingcheck.png)


