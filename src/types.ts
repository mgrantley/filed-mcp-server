// Filed API response types

export interface SearchMeta {
  total: number;
  limit: number;
  offset: number;
  state?: string;
  source?: string;
}

export interface EntitySummary {
  id: string;
  name: string;
  state: string;
  status: string;
  type: string;
  formation_date?: string;
  registered_agent?: string;
}

export interface SearchResponse {
  data: EntitySummary[];
  meta: SearchMeta;
}

export interface Officer {
  name: string;
  title?: string;
  address?: string;
}

export interface Filing {
  type: string;
  date: string;
  description?: string;
}

export interface EntityDetail {
  id: string;
  name: string;
  state: string;
  status: string;
  type: string;
  formation_date?: string;
  registered_agent?: {
    name: string;
    address?: string;
  };
  officers?: Officer[];
  filing_history?: Filing[];
  // Federal enrichment
  sec_filings?: SecFiling[];
  contracts?: Contract[];
  lobbying?: LobbyingDisclosure[];
}

export interface EntityResponse {
  data: EntityDetail;
}

export interface SecFiling {
  company_name: string;
  cik?: string;
  form_type: string;
  filing_date: string;
  description?: string;
  url?: string;
}

export interface SecSearchResponse {
  data: SecFiling[];
  meta: SearchMeta;
}

export interface Contract {
  recipient_name: string;
  award_amount: number;
  awarding_agency: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  award_id?: string;
  naics?: string;
}

export interface ContractSearchResponse {
  data: Contract[];
  meta: SearchMeta;
}

export interface LobbyingDisclosure {
  client_name: string;
  registrant_name: string;
  amount?: number;
  issue_codes?: string[];
  lobbyists?: string[];
  filing_date?: string;
  filing_year?: string;
  filing_type?: string;
}

export interface LobbyingSearchResponse {
  data: LobbyingDisclosure[];
  meta: SearchMeta;
}

export interface CompanyIntelReport {
  company_name: string;
  states_searched: string[];
  state_registrations: EntitySummary[];
  officers_across_states: Array<{
    name: string;
    roles: Array<{ state: string; title?: string; company: string }>;
  }>;
  sec_filings: SecFiling[];
  federal_contracts: Contract[];
  lobbying_activity: LobbyingDisclosure[];
  cross_references: {
    officer_overlap: string[];
    name_variations: string[];
    total_contract_value: number;
    total_lobbying_spend: number;
    states_with_registrations: string[];
  };
  errors: string[];
}
