from fastmcp import Client
import os

#Run MCP
async def run_tool(tool_name: str, tool_input: dict):
    async with Client(f"{os.getenv('MCP_URL')}") as client:
        result = await client.call_tool(
            tool_name,
            tool_input
        )
        return result.data