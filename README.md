## pyRevit extension
`BimTools.extension` adds a "Checks" tab to Revit with five read-only tools. They never change the model. Results open in a table with clickable element IDs, and most tools can export to CSV.

| Tool | What it checks |
|---|---|
| ElementCheck | Walls, doors and windows with a missing FireRating |
| ModelHealth | Warnings, imported CAD files, in-place families, views not on sheets |
| RoomCheck | Unplaced, unenclosed, unnamed and duplicate-number rooms |
| ParameterCheck | Pick categories and any parameter, list elements where it is empty |
| NamingCheck | Sheet numbers and view names against a configurable pattern |

### Install
1. Install [pyRevit](https://github.com/pyrevitlabs/pyRevit).
2. Put `BimTools.extension` in a folder, then in pyRevit Settings add that folder under Custom Extension Directories.
3. Click Save Settings and Reload.

   
![Summary sheet](summary.PNG)

![Summary sheet](pyrevitbutton.png)

![Summary sheet](namingcheck.png)

