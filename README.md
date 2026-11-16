# IFC Element Parameter Checker

A small Python tool that checks IFC models exported from Revit for missing parameters on walls, doors and windows, and writes the result to Excel.

## What it does
- Reads all IfcWall, IfcDoor and IfcWindow elements from an IFC file
- Checks FireRating, IsExternal (and LoadBearing for walls) in the standard Pset_*Common property sets
- Outputs report.xlsx with four sheets:
  - Summary: missing count and percentage per element type and parameter
  - Walls, Doors, Windows: one row per element, marked OK or MISSING

## Requirements
- Python 3
- pip install ifcopenshell openpyxl

## Usage
1. Export your Revit model as IFC (with "Export IFC common property sets" enabled)
2. Put the file next to the script and set its name in IFC_FILE at the top of the script
3. Run: python check_elements.py

## Why I built it
As a BIM coordinator, I often had to check models for missing data by hand. This is the first step toward automating that process.

![Summary sheet](summary.PNG)

## pyRevit button
A pyRevit extension that runs the same check inside Revit and lists walls with a missing FireRating, with clickable element IDs. Exports the result to CSV.

![Summary sheet](pyrevitbutton.png)
