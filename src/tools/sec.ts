import type { FiledApiClient } from "../api.js";

export const searchSecTool = {
  name: "filed_search_sec",
  description:
    "Search SEC EDGAR filings by company name, CIK number, form type, or industry code. Find 10-K annual reports, 10-Q quarterlies, 8-K event disclosures, S-1 registrations, and more.",
  inputSchema: {
    type: "object" as const,
    properties: {
      query: {
        type: "string",
        description: "Company name or keyword to search",
      },
      forms: {
        type: "string",
        description:
          "Comma-separated form types to filter: 10-K, 10-Q, 8-K, S-1, DEF 14A, 13F-HR, etc.",
      },
      cik: {
        type: "string",
        description: "SEC Central Index Key",
      },
      sic: {
        type: "string",
        description: "Standard Industrial Classification code",
      },
      start_date: {
        type: "string",
        description: "Filter filings after this date (YYYY-MM-DD)",
      },
      end_date: {
        type: "string",
        description: "Filter filings before this date (YYYY-MM-DD)",
      },
      limit: {
        type: "number",
        description: "Max results, up to 100 (default: 25)",
      },
    },
    required: [],
  },
};

export async function handleSearchSec(
  client: FiledApiClient,
  args: Record<string, unknown>
) {
  const result = await client.searchSec({
    query: args.query as string | undefined,
    forms: args.forms as string | undefined,
    cik: args.cik as string | undefined,
    sic: args.sic as string | undefined,
    start_date: args.start_date as string | undefined,
    end_date: args.end_date as string | undefined,
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
