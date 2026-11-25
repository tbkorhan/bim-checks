# revit-mcp

A small MCP server that lets Claude read data from an open Revit model.

```
Claude Desktop -> MCP server (Python, uv) -> pyRevit Routes -> Revit
```

All tools are read-only. Nothing in the model is modified.

## Tools

| Tool | What it does |
|---|---|
| `revit_status` | Checks that Revit is reachable, returns the version |
| `count_walls` | Model title and wall count |
| `list_parameters` | Parameter names for a category |
| `find_missing_values` | Elements where a parameter is empty or missing |

Categories: Walls, Doors, Windows, Floors, Rooms.

## Setup

1. Enable the pyRevit Routes server (pyRevit > Settings > Routes).
2. Put `startup.py` in the root of your pyRevit extension (see `BimTools.extension`).
3. Restart Revit. Reloading pyRevit with a model open crashed Revit 2026 in my tests.
4. In this folder run `uv sync` (the MCP package is pinned below version 2).
5. Add the server to Claude Desktop's config under `mcpServers`, with `uv` running `server.py` from this folder.

## Notes

- Tested on Revit 2026 and Windows only.
- The server only talks to `localhost`. If Windows Firewall asks about Revit, you do not need to allow network access.
- Try it on a copy of your model first.
