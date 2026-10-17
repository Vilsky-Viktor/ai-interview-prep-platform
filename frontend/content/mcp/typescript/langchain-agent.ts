// npm install langchain@1.5.18 @langchain/core@1.2.18 @langchain/anthropic@1.5.12 @langchain/langgraph@1.5.0 @langchain/mcp-adapters@1.1.4 @modelcontextprotocol/sdk@1.32.1
import { MultiServerMCPClient } from "@langchain/mcp-adapters"
import { createAgent } from "langchain"

import { PREPZA_MCP, signIn } from "./prepza-auth.js"

const QUESTION = "Which candidates passed my latest interview?"

async function main() {
  const client = new MultiServerMCPClient({
    mcpServers: {
      prepza: { transport: "http", url: PREPZA_MCP, ...(await signIn()) },
    },
  })
  const tools = await client.getTools()
  const agent = createAgent({ model: "anthropic:claude-opus-5-5", tools })
  const result = await agent.invoke({
    messages: [{ role: "user", content: QUESTION }],
  })
  console.log(result.messages.at(-1)?.content)
  await client.close()
}

main()
