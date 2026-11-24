"""Client MCP di esempio: avvia il server via stdio e ne usa tool, resource e prompt.

    uv run mcp-tutorial-client
"""

import asyncio
import sys

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

# Il client lancia il server come sottoprocesso e gli parla su stdin/stdout.
SERVER = StdioTransport(command=sys.executable, args=["-m", "mcp_tutorial.server"])


async def on_progress(progress: float, total: float | None, message: str | None) -> None:
    print(f"  progress: {message}")


async def run() -> None:
    async with Client(SERVER) as client:
        print("Tool disponibili:", [tool.name for tool in await client.list_tools()])

        print("\n1. Tool search_notes('processo')")
        result = await client.call_tool("search_notes", {"query": "processo"})
        print(" ", [note["title"] for note in result.structured_content["result"]])

        print("\n2. Resource notes://1")
        contents = await client.read_resource("notes://1")
        print(" ", contents[0].text)

        print("\n3. Prompt summarize_notes('release')")
        prompt = await client.get_prompt("summarize_notes", {"topic": "release"})
        print(" ", prompt.messages[0].content.text)

        print("\n4. Tool import_notes con progress")
        notes = [{"title": "Daily 1", "content": "CI rotta"}, {"title": "Daily 2", "content": "CI ok"}]
        await client.call_tool("import_notes", {"notes": notes}, progress_handler=on_progress)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
