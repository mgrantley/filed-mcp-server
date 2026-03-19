#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

import { FiledApiClient } from "./api.js";
import { searchEntitiesTool, handleSearchEntities } from "./tools/search.js";
import { getEntityTool, handleGetEntity } from "./tools/entity.js";
import { searchSecTool, handleSearchSec } from "./tools/sec.js";
import { searchContractsTool, handleSearchContracts } from "./tools/contracts.js";
import { searchLobbyingTool, handleSearchLobbying } from "./tools/lobbying.js";
import { companyIntelTool, handleCompanyIntel } from "./tools/intel.js";

const apiKey = process.env.FILED_API_KEY;
if (!apiKey) {
  console.error(
    "Error: FILED_API_KEY environment variable is required.\n" +
      "Get a free API key at https://filed.dev"
  );
  process.exit(1);
}

const client = new FiledApiClient(apiKey);

const server = new Server(
  {
    name: "filed-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool list
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    searchEntitiesTool,
    getEntityTool,
    searchSecTool,
    searchContractsTool,
    searchLobbyingTool,
    companyIntelTool,
  ],
}));

// Route tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "filed_search_entities":
        return await handleSearchEntities(client, args ?? {});
      case "filed_get_entity":
        return await handleGetEntity(client, args ?? {});
      case "filed_search_sec":
        return await handleSearchSec(client, args ?? {});
      case "filed_search_contracts":
        return await handleSearchContracts(client, args ?? {});
      case "filed_search_lobbying":
        return await handleSearchLobbying(client, args ?? {});
      case "filed_company_intel":
        return await handleCompanyIntel(client, args ?? {});
      default:
        return {
          content: [
            {
              type: "text" as const,
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text" as const,
          text: `Error: ${(error as Error).message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Filed MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
