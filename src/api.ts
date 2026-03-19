import type {
  SearchResponse,
  EntityResponse,
  SecSearchResponse,
  ContractSearchResponse,
  LobbyingSearchResponse,
} from "./types.js";

const BASE_URL = "https://filed.dev/api/v1";
const MAX_RETRIES = 3;
const INITIAL_BACKOFF_MS = 1000;

export class FiledApiClient {
  private apiKey: string;

  constructor(apiKey: string) {
    if (!apiKey) {
      throw new Error(
        "FILED_API_KEY is required. Get one at https://filed.dev"
      );
    }
    this.apiKey = apiKey;
  }

  private async request<T>(path: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${BASE_URL}${path}`);
    if (params) {
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== "") {
          url.searchParams.set(key, value);
        }
      }
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        const response = await fetch(url.toString(), {
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            Accept: "application/json",
          },
        });

        if (response.status === 429) {
          const retryAfter = response.headers.get("retry-after");
          const waitMs = retryAfter
            ? parseInt(retryAfter, 10) * 1000
            : INITIAL_BACKOFF_MS * Math.pow(2, attempt);
          await this.sleep(waitMs);
          continue;
        }

        if (!response.ok) {
          const body = await response.text();
          throw new Error(
            `Filed API error ${response.status}: ${body || response.statusText}`
          );
        }

        return (await response.json()) as T;
      } catch (error) {
        lastError = error as Error;
        if ((error as Error).message?.includes("Filed API error")) {
          throw error; // Don't retry non-429 API errors
        }
        // Network errors — retry with backoff
        if (attempt < MAX_RETRIES - 1) {
          await this.sleep(INITIAL_BACKOFF_MS * Math.pow(2, attempt));
        }
      }
    }

    throw lastError || new Error("Request failed after retries");
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async searchEntities(params: {
    name?: string;
    state: string;
    agent?: string;
    status?: string;
    type?: string;
    limit?: number;
  }): Promise<SearchResponse> {
    const queryParams: Record<string, string> = {
      state: params.state,
    };
    if (params.name) queryParams.name = params.name;
    if (params.agent) queryParams.agent = params.agent;
    if (params.status) queryParams.status = params.status;
    if (params.type) queryParams.type = params.type;
    if (params.limit) queryParams.limit = params.limit.toString();

    return this.request<SearchResponse>("/search", queryParams);
  }

  async getEntity(id: string, includeFederal = false): Promise<EntityResponse> {
    const params: Record<string, string> = {};
    if (includeFederal) {
      params.include = "federal";
    }
    return this.request<EntityResponse>(`/entity/${id}`, params);
  }

  async searchSec(params: {
    query?: string;
    forms?: string;
    cik?: string;
    sic?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<SecSearchResponse> {
    const queryParams: Record<string, string> = {};
    if (params.query) queryParams.q = params.query;
    if (params.forms) queryParams.forms = params.forms;
    if (params.cik) queryParams.cik = params.cik;
    if (params.sic) queryParams.sic = params.sic;
    if (params.start_date) queryParams.start_date = params.start_date;
    if (params.end_date) queryParams.end_date = params.end_date;
    if (params.limit) queryParams.limit = params.limit.toString();

    return this.request<SecSearchResponse>("/sec/search", queryParams);
  }

  async searchContracts(params: {
    recipient?: string;
    agency?: string;
    min_amount?: number;
    max_amount?: number;
    naics?: string;
    start_date?: string;
    end_date?: string;
    sort?: string;
    limit?: number;
  }): Promise<ContractSearchResponse> {
    const queryParams: Record<string, string> = {};
    if (params.recipient) queryParams.recipient = params.recipient;
    if (params.agency) queryParams.agency = params.agency;
    if (params.min_amount) queryParams.min_amount = params.min_amount.toString();
    if (params.max_amount) queryParams.max_amount = params.max_amount.toString();
    if (params.naics) queryParams.naics = params.naics;
    if (params.start_date) queryParams.start_date = params.start_date;
    if (params.end_date) queryParams.end_date = params.end_date;
    if (params.sort) queryParams.sort = params.sort;
    if (params.limit) queryParams.limit = params.limit.toString();

    return this.request<ContractSearchResponse>("/contracts/search", queryParams);
  }

  async searchLobbying(params: {
    client_name?: string;
    registrant_name?: string;
    issue_code?: string;
    filing_year?: string;
    filing_type?: string;
  }): Promise<LobbyingSearchResponse> {
    const queryParams: Record<string, string> = {};
    if (params.client_name) queryParams.client_name = params.client_name;
    if (params.registrant_name) queryParams.registrant_name = params.registrant_name;
    if (params.issue_code) queryParams.issue_code = params.issue_code;
    if (params.filing_year) queryParams.filing_year = params.filing_year;
    if (params.filing_type) queryParams.filing_type = params.filing_type;

    return this.request<LobbyingSearchResponse>("/lobbying/search", queryParams);
  }
}
