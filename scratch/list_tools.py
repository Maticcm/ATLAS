import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    async with stdio_client(StdioServerParameters(command='npx', args=['-y', '@playwright/mcp@latest'])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print([t.name for t in tools.tools])

asyncio.run(run())
