import os 
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route, Mount
from fastmcp import FastMCP
from whoop_client import WhoopClient
from tools.overview import register_overview_tools
from tools.sleep import register_sleep_tools
from tools.recovery import register_recovery_tools
from tools.strain import register_strain_tools
from tools.healthspan import register_healthspan_tools

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI","https://whoop-mcp-ahmed.onrender.com/callback")
mcp = FastMCP("WHOOP MCP Server")
register_overview_tools(mcp)
register_sleep_tools(mcp)
register_recovery_tools(mcp)
register_strain_tools(mcp)
register_healthspan_tools(mcp)

async def callback(request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("Error: No code provided", status_code=400)
    client = WhoopClient()
    success = client.exchange_code(code)
    if success:
        return HTMLResponse("WHOOP Connected Successfully! You can close this tab now.")
    return HTMLResponse("Failed to exchange token with WHOOP", status_code=500)

async def health(request):
    return JSONResponse({"status": "ok"})

mcp_app = mcp.get_app() if hasattr(mcp, "get_app") else mcp._app

app = Starlette(
    routes=[
        Route("/callback", endpoint=callback, methods=["GET"]),
        Route("/health", endpoint=health, methods=["GET"]),
        Mount("/", app=mcp_app),
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)