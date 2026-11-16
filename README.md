# IFC Wall Parameter Checker

A small Python tool that checks IFC models exported from Revit for missing wall parameters and writes the result to Excel.

## What it does
- Reads all IfcWall elements from an IFC file
- Checks FireRating, IsExternal and LoadBearing in Pset_WallCommon
- Outputs report.xlsx with two sheets:
  - Walls: one row per wall, marked OK or MISSING
  - Summary: number and percentage of missing values per parameter

## Requirements
- Python 3
- pip install ifcopenshell openpyxl

## Usage
1. Export your Revit model as IFC (with "Export IFC common property sets" enabled)
2. Put the file next to the script and set its name in the script
3. Run: python check_walls.py

## Why I built it
As a BIM coordinator, I often had to check models for missing data by hand. This is the first step toward automating that process.

![Summary sheet](summary.PNG)
