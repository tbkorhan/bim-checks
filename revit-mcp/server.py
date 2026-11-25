import json
import urllib.parse
import urllib.request

from mcp.server.fastmcp import FastMCP

BASE = "http://localhost:48884/bimtools"
mcp = FastMCP("revit")


def _get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": "Could not reach Revit. Is Revit open with a "
                         "model, and is Routes enabled? ({})".format(e)}


@mcp.tool()
def revit_status() -> dict:
    """Check that Revit is reachable and return its version."""
    return _get("/ping/")


@mcp.tool()
def count_walls() -> dict:
    """Return the open model's title and its wall count."""
    return _get("/wallcount/")


@mcp.tool()
def list_parameters(category: str) -> dict:
    """List parameter names for a category.
    Valid categories: Walls, Doors, Windows, Floors, Rooms."""
    return _get("/params/{}/".format(urllib.parse.quote(category, safe="")))


@mcp.tool()
def find_missing_values(category: str, parameter: str) -> dict:
    """Find elements where a parameter is empty or not found.
    Valid categories: Walls, Doors, Windows, Floors, Rooms.
    Use list_parameters first to get the exact parameter name."""
    return _get("/missing/{}/{}/".format(
        urllib.parse.quote(category, safe=""),
        urllib.parse.quote(parameter, safe="")))


if __name__ == "__main__":
    mcp.run()