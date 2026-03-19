import type { FiledApiClient } from "../api.js";

export const searchEntitiesTool = {
  name: "filed_search_entities",
  description:
    "Search US business entities by name across 9 states (AK, CO, CT, DC, FL, IA, NY, OR, PA). Returns matching companies with state registration details including entity type, status, and formation date.",
  inputSchema: {
    type: "object" as const,
    properties: {
      name: {
        type: "string",
        description: "Business name to search (required if agent not provided)",
      },
      state: {
        type: "string",
        description: "Two-letter state code (AK, CO, CT, DC, FL, IA, NY, OR, PA)",
        enum: ["AK", "CO", "CT", "DC", "FL", "IA", "NY", "OR", "PA"],
      },
      agent: {
        type: "string",
        description: "Registered agent name to search",
      },
      status: {
        type: "string",
        description: "Filter by status",
        enum: ["active", "inactive", "all"],
      },
      type: {
        type: "string",
        description: "Filter by entity type",
        enum: ["llc", "corporation", "lp"],
      },
      limit: {
        type: "number",
        description: "Results per page, max 50 (default: 10)",
      },
    },
    required: ["state"],
  },
};

export async function handleSearchEntities(
  client: FiledApiClient,
  args: Record<string, unknown>
) {
  const result = await client.searchEntities({
    name: args.name as string | undefined,
    state: args.state as string,
    agent: args.agent as string | undefined,
    status: args.status as string | undefined,
    type: args.type as string | undefined,
    limit: args.limit as number | undefined,
  });

  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}
