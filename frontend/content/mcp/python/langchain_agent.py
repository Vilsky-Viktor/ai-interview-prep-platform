# pip install "langchain==1.4.6" "langchain-anthropic==1.7.6" "langchain-mcp-adapters==0.3.2" "mcp==1.30.0"
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from prepza_auth import PREPZA_MCP, connection

QUESTION = "Which candidates passed my latest interview?"


async def main() -> None:
    server = {"transport": "streamable_http", "url": PREPZA_MCP, **connection()}
    client = MultiServerMCPClient({"prepza": server})
    tools = await client.get_tools()
    agent = create_agent("anthropic:claude-opus-5-5", tools)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": QUESTION}]})
    print(result["messages"][-1].content)


asyncio.run(main())
