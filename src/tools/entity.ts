import type { FiledApiClient } from "../api.js";

export const getEntityTool = {
  name: "filed_get_entity",
  description:
    "Get full details for a specific business entity including officers, registered agent, filing history, and current status. Optionally enrich with federal data (SEC filings, government contracts, lobbying disclosures). The entity ID format is 'STATE:ID' (e.g., 'FL:P06000113830').",
  inputSchema: {
    type: "object" as const,
    properties: {
      id: {
        type: "string",
        description:
          "Entity ID from search results (format: STATE:ID, e.g., 'FL:P06000113830')",
      },
      include_federal: {
        type: "boolean",
        description:
          "Include SEC filings, federal contracts, and lobbying data (default: false). Uses additional API credits.",
      },
    },
    required: ["id"],
  },
};

export async function handleGetEntity(
  client: FiledApiClient,
  args: Record<string, unknown>
) {
  const result = await client.getEntity(
    args.id as string,
    (args.include_federal as boolean) ?? false
  );

  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}
