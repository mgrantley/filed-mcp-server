import type { FiledApiClient } from "../api.js";

export const searchContractsTool = {
  name: "filed_search_contracts",
  description:
    "Search federal government contracts from USASpending.gov. Find which companies receive government contracts, from which agencies, and for how much.",
  inputSchema: {
    type: "object" as const,
    properties: {
      recipient: {
        type: "string",
        description: "Contractor/recipient name to search",
      },
      agency: {
        type: "string",
        description: "Awarding agency name",
      },
      min_amount: {
        type: "number",
        description: "Minimum award amount in dollars",
      },
      max_amount: {
        type: "number",
        description: "Maximum award amount in dollars",
      },
      naics: {
        type: "string",
        description: "NAICS industry code",
      },
      start_date: {
        type: "string",
        description: "Contracts starting after this date (YYYY-MM-DD)",
      },
      end_date: {
        type: "string",
        description: "Contracts starting before this date (YYYY-MM-DD)",
      },
      sort: {
        type: "string",
        description: "Sort field (e.g., 'Award Amount', 'Start Date')",
      },
      limit: {
        type: "number",
        description: "Max results, up to 100 (default: 25)",
      },
    },
    required: [],
  },
};

export async function handleSearchContracts(
  client: FiledApiClient,
  args: Record<string, unknown>
) {
  const result = await client.searchContracts({
    recipient: args.recipient as string | undefined,
    agency: args.agency as string | undefined,
    min_amount: args.min_amount as number | undefined,
    max_amount: args.max_amount as number | undefined,
    naics: args.naics as string | undefined,
    start_date: args.start_date as string | undefined,
    end_date: args.end_date as string | undefined,
    sort: args.sort as string | undefined,
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
