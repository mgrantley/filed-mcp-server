import type { FiledApiClient } from "../api.js";

export const searchLobbyingTool = {
  name: "filed_search_lobbying",
  description:
    "Search federal lobbying disclosures from the Senate LDA database. Find which companies hire lobbyists, what issues they lobby on, and how much they spend.",
  inputSchema: {
    type: "object" as const,
    properties: {
      client_name: {
        type: "string",
        description: "Client company being represented",
      },
      registrant_name: {
        type: "string",
        description: "Lobbying firm name",
      },
      issue_code: {
        type: "string",
        description:
          "Issue area code: HCR (Health), DEF (Defense), TAX (Taxation), ENV (Environment), TRD (Trade), etc.",
      },
      filing_year: {
        type: "string",
        description: "Filing year (e.g., '2025')",
      },
      filing_type: {
        type: "string",
        description: "Filing type: RR (Registration), Q1, Q2, Q3, Q4 (Quarterly)",
      },
    },
    required: [],
  },
};

export async function handleSearchLobbying(
  client: FiledApiClient,
  args: Record<string, unknown>
) {
  const result = await client.searchLobbying({
    client_name: args.client_name as string | undefined,
    registrant_name: args.registrant_name as string | undefined,
    issue_code: args.issue_code as string | undefined,
    filing_year: args.filing_year as string | undefined,
    filing_type: args.filing_type as string | undefined,
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
