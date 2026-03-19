import type { FiledApiClient } from "../api.js";
import type {
  EntitySummary,
  SecFiling,
  Contract,
  LobbyingDisclosure,
  CompanyIntelReport,
} from "../types.js";

const ALL_STATES = ["AK", "CO", "CT", "DC", "FL", "IA", "NY", "OR", "PA"];

export const companyIntelTool = {
  name: "filed_company_intel",
  description:
    "Run comprehensive intelligence gathering on a company. Searches across all 9 US states (AK, CO, CT, DC, FL, IA, NY, OR, PA) for business registrations, then checks SEC filings, federal contracts, and lobbying disclosures. Returns a unified intelligence report with cross-reference findings. NOTE: This tool makes multiple API calls (up to ~15) and uses more credits than individual tools.",
  inputSchema: {
    type: "object" as const,
    properties: {
      company_name: {
        type: "string",
        description: "Company name to investigate",
      },
      states: {
        type: "array",
        items: { type: "string" },
        description:
          "Specific states to search (default: all 9). Use 2-letter codes.",
      },
      include_sec: {
        type: "boolean",
        description: "Search SEC EDGAR filings (default: true)",
      },
      include_contracts: {
        type: "boolean",
        description: "Search federal contracts (default: true)",
      },
      include_lobbying: {
        type: "boolean",
        description: "Search lobbying disclosures (default: true)",
      },
    },
    required: ["company_name"],
  },
};

export async function handleCompanyIntel(
  client: FiledApiClient,
  args: Record<string, unknown>
): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  const companyName = args.company_name as string;
  const states = (args.states as string[] | undefined) ?? ALL_STATES;
  const includeSec = (args.include_sec as boolean) ?? true;
  const includeContracts = (args.include_contracts as boolean) ?? true;
  const includeLobbying = (args.include_lobbying as boolean) ?? true;

  const report: CompanyIntelReport = {
    company_name: companyName,
    states_searched: states,
    state_registrations: [],
    officers_across_states: [],
    sec_filings: [],
    federal_contracts: [],
    lobbying_activity: [],
    cross_references: {
      officer_overlap: [],
      name_variations: [],
      total_contract_value: 0,
      total_lobbying_spend: 0,
      states_with_registrations: [],
    },
    errors: [],
  };

  // 1. Search each state for the company
  const stateResults = await Promise.allSettled(
    states.map(async (state) => {
      try {
        const result = await client.searchEntities({
          name: companyName,
          state,
          limit: 10,
        });
        return { state, data: result.data };
      } catch (error) {
        return { state, data: [], error: (error as Error).message };
      }
    })
  );

  const nameVariations = new Set<string>();
  const officerMap = new Map<
    string,
    Array<{ state: string; title?: string; company: string }>
  >();
  const entityIds: string[] = [];

  for (const result of stateResults) {
    if (result.status === "fulfilled") {
      const { state, data, error } = result.value as {
        state: string;
        data: EntitySummary[];
        error?: string;
      };
      if (error) {
        report.errors.push(`${state}: ${error}`);
        continue;
      }
      if (data && data.length > 0) {
        report.cross_references.states_with_registrations.push(state);
        for (const entity of data) {
          report.state_registrations.push(entity);
          nameVariations.add(entity.name);
          if (entity.id) {
            entityIds.push(entity.id);
          }
        }
      }
    } else {
      report.errors.push(`State search failed: ${result.reason}`);
    }
  }

  // 2. Fetch entity details for top matches (up to 5 to conserve credits)
  const topEntities = entityIds.slice(0, 5);
  const entityDetails = await Promise.allSettled(
    topEntities.map(async (id) => {
      try {
        const result = await client.getEntity(id, false);
        return result.data;
      } catch (error) {
        report.errors.push(`Entity ${id}: ${(error as Error).message}`);
        return null;
      }
    })
  );

  for (const result of entityDetails) {
    if (result.status === "fulfilled" && result.value) {
      const entity = result.value;
      if (entity.officers) {
        for (const officer of entity.officers) {
          const normalizedName = officer.name.toUpperCase().trim();
          if (!officerMap.has(normalizedName)) {
            officerMap.set(normalizedName, []);
          }
          officerMap.get(normalizedName)!.push({
            state: entity.state,
            title: officer.title,
            company: entity.name,
          });
        }
      }
    }
  }

  // Build officer cross-reference
  for (const [name, roles] of officerMap) {
    report.officers_across_states.push({ name, roles });
    if (roles.length > 1) {
      const stateList = [...new Set(roles.map((r) => r.state))];
      if (stateList.length > 1) {
        report.cross_references.officer_overlap.push(
          `${name} appears in ${stateList.join(", ")} registrations`
        );
      }
    }
  }

  // 3. SEC filings
  if (includeSec) {
    try {
      const secResult = await client.searchSec({
        query: companyName,
        limit: 25,
      });
      report.sec_filings = secResult.data || [];
    } catch (error) {
      report.errors.push(`SEC search: ${(error as Error).message}`);
    }
  }

  // 4. Federal contracts
  if (includeContracts) {
    try {
      const contractResult = await client.searchContracts({
        recipient: companyName,
        limit: 25,
      });
      report.federal_contracts = contractResult.data || [];
      report.cross_references.total_contract_value =
        report.federal_contracts.reduce(
          (sum, c) => sum + ((c as any).amount || c.award_amount || 0),
          0
        );
    } catch (error) {
      report.errors.push(`Contracts search: ${(error as Error).message}`);
    }
  }

  // 5. Lobbying disclosures
  if (includeLobbying) {
    try {
      const lobbyingResult = await client.searchLobbying({
        client_name: companyName,
      });
      report.lobbying_activity = lobbyingResult.data || [];
      report.cross_references.total_lobbying_spend =
        report.lobbying_activity.reduce(
          (sum, l) => sum + ((l as any).income || l.amount || 0),
          0
        );
    } catch (error) {
      report.errors.push(`Lobbying search: ${(error as Error).message}`);
    }
  }

  report.cross_references.name_variations = [...nameVariations];

  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(report, null, 2),
      },
    ],
  };
}
