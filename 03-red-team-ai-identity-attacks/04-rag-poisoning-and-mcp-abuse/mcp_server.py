
import sys
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server BEFORE declaring tools
mcp = FastMCP("Email MCP Server")


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Simulate sending an email. No real email is sent."""

    email = f"""
To      : {to}
Subject : {subject}
Body    : {body}
    """
    print("[MCP SERVER] send_email invoked", file=sys.stderr, flush=True)
    return email


if __name__ == "__main__":
    print("[MCP SERVER] Starting...", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")
