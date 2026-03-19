---
title: "Filed Intelligence Hub: AI-Powered Company Due Diligence with Filed MCP + Notion"
published: false
tags: devchallenge, notionchallenge, mcp, ai
---

*This is a submission for the [Notion MCP Challenge](https://dev.to/challenges/notion-2026-03-04)*

## What I Built

An MCP server that gives AI agents access to US government data through [Filed.dev](https://filed.dev), paired with Notion MCP to build a persistent company intelligence workspace.

**The problem:** Researching a company for due diligence means manually checking state business registries, SEC EDGAR, federal contract databases, and lobbying disclosures — each with different interfaces, different search patterns, different data formats. A basic background check on one company across these sources takes hours.

**The solution:** Two MCP servers working together. Filed MCP provides 6 tools covering 9 state business registries and 3 federal data sources. Notion MCP provides the structured workspace. One natural language prompt triggers a multi-source investigation and populates a Notion hub with cross-referenced findings.

I demonstrated this by building an intelligence hub for three defense companies — Lockheed Martin, Anduril Industries, and Palantir Technologies. In minutes, the AI:

- Found **62 Lockheed Martin entities** across 8 states, **$4.96B** in federal contracts, and **$925K** in lobbying spend across 20+ firms
- Discovered **14 Anduril registrations** across 6 states, **$560M** in contracts, and **$1.02M** in lobbying — a startup scaling fast into the defense establishment
- Mapped **Palantir's** cross-agency contract portfolio (**$350M**), their **$2.1M** lobbying operation, and 25 SEC filings as a public company

Then cross-referenced all three: shared lobbying issue areas (DEF, BUD, TAX), competitive overlap in DoD contracting, and officer networks across states.

### Filed MCP Server — 6 Tools

| Tool | What it does |
|------|-------------|
| `filed_search_entities` | Search business entities by name across 9 US states (AK, CO, CT, DC, FL, IA, NY, OR, PA) |
| `filed_get_entity` | Full entity details — officers, registered agent, filing history, optional federal enrichment |
| `filed_search_sec` | Search SEC EDGAR filings (10-K, 10-Q, 8-K, S-1, etc.) |
| `filed_search_contracts` | Search federal government contracts from USASpending.gov |
| `filed_search_lobbying` | Search Senate lobbying disclosures (LDA database) |
| `filed_company_intel` | **Power tool** — orchestrates all sources for a company into one unified intelligence report |

The `filed_company_intel` tool is the key differentiator. One call searches all 9 states, pulls SEC filings, federal contracts, and lobbying data, then returns a structured report with cross-reference analysis: name variations found, officer overlap across states, total contract value, and total lobbying spend.

## Demo

<!-- TODO: Add video link -->

The demo walks through:

1. **Workspace creation** — AI creates 6 linked Notion databases (Companies, Officers, SEC Filings, Contracts, Lobbying, Intelligence Log) with typed properties and filtered views
2. **Company research** — Three defense companies investigated via `filed_company_intel`, results populated into Notion
3. **Cross-referencing** — AI reads back the populated databases to find patterns: shared lobbyists, competitive contract overlap, officer networks
4. **Risk assessment** — AI generates risk levels and an executive summary page

### Sample Data (Lockheed Martin)

From one `filed_company_intel` call:

- **State registrations:** 62 entities across AK, CT, DC, FL, IA, NY, OR, PA
- **Name variations:** 28 (LOCKHEED MARTIN CORPORATION, LOCKHEED MARTIN SERVICES LLC, LOCKHEED MARTIN GLOBAL TELECOMMUNICATIONS INC, etc.)
- **SEC filings:** 25 recent filings including 10-K, 10-Q, 8-K
- **Federal contracts:** 25 largest contracts totaling **$4.96 billion** — primarily DoD
- **Lobbying:** 25 disclosures totaling **$925K** across firms like Capitol Counsel, Cozen O'Connor Public Strategies, and their in-house team ($4.14M/quarter in direct expenses)
- **Lobbying issues:** DEF (Defense), BUD (Budget/Appropriations), TAX, AER (Aerospace), HOM (Homeland Security), INT (Intelligence), NAT (Natural Resources), TRD (Trade)

Full sample outputs for all three companies are in the [demo/ directory](https://github.com/mgrantley/filed-mcp-server/tree/main/demo).

## Show us the code

**GitHub:** [github.com/mgrantley/filed-mcp-server](https://github.com/mgrantley/filed-mcp-server)

**Install:** `npx filed-mcp-server`

**Architecture:**

```
AI Agent (Claude Code / Cursor / Claude Desktop)
  ├── Filed MCP Server         ← 6 tools, 9 states + federal sources
  │   └── Filed.dev API            (free: 100 lookups/month)
  │       ├── State registries     (AK, CO, CT, DC, FL, IA, NY, OR, PA)
  │       ├── SEC EDGAR
  │       ├── USASpending.gov
  │       └── Senate LDA
  └── Notion MCP Server       ← structures results into workspace
      └── Notion API
          ├── 🏢 Companies         (master tracker with risk levels)
          ├── 👤 Officers          (cross-state person tracking)
          ├── 📄 SEC Filings       (EDGAR filings by form type)
          ├── 💰 Contracts         (federal awards by agency)
          ├── 🏛️ Lobbying          (disclosures by issue area)
          └── 🔍 Intelligence Log  (cross-reference findings)
```

The server is TypeScript, uses `@modelcontextprotocol/sdk`, and runs on stdio. ~500 lines of code total. Each tool maps directly to a Filed API endpoint, with the `filed_company_intel` tool orchestrating 15+ API calls into a single structured report.

**Configuration (any MCP client):**

```json
{
  "mcpServers": {
    "filed": {
      "command": "npx",
      "args": ["-y", "filed-mcp-server"],
      "env": {
        "FILED_API_KEY": "your_key_here"
      }
    }
  }
}
```

Get a free API key at [filed.dev](https://filed.dev) — 100 lookups/month on the free tier.

## How I Used Notion MCP

Notion MCP is the **persistence and analysis layer**. Without it, Filed API responses are ephemeral chat output. With it, the AI builds a structured, queryable workspace that grows with each company researched.

**Database creation:** The AI uses `notion-create-database` to set up 6 databases with typed properties — dates, currencies, selects, relations, checkboxes. The schema maps directly to Filed's data model: state registrations become Companies rows, SEC filings get form type selects, contracts get currency-formatted award amounts.

**Relational structure:** Every database relates back to Companies through Notion relations. This means officers, filings, contracts, and lobbying disclosures are all linked to their parent entity. The Intelligence Log uses relations to connect findings to specific companies.

**Data population:** After each `filed_company_intel` call, the AI uses `notion-create-page` to add structured records. Each data source maps to its own database — a Lockheed Martin intel report becomes 62 company pages, dozens of officer records, 25 SEC filing entries, 25 contract records, and 25 lobbying disclosures.

**Cross-referencing (the key insight):** Because data persists in Notion, the AI can use `notion-search` and database queries to find patterns *across* companies. After researching all three defense companies, it can:
- Query the Officers database for names appearing in multiple companies
- Compare contract agencies across Companies to identify competitive overlap  
- Correlate lobbying issue areas with contract awards (are companies lobbying on the same issues they're winning contracts for?)

**Views for analysis:** `notion-create-view` builds purpose-specific perspectives:
- **Risk Dashboard** — filtered to medium/high risk companies, sorted by risk level
- **Big Contracts** — filtered to awards >$100K, sorted by value
- **Cross-State Flags** — officers appearing in multiple state registrations
- **By Agency / By Issue Area** — board views for pattern recognition

**What makes this different from a CSV export:** The workspace is *alive*. Add a new company next week, and the cross-references update. The AI can re-query the Intelligence Log to see if new findings connect to old ones. It's not a report — it's an evolving intelligence database.

### Why This Pairing Works

Filed MCP handles the hard part: normalizing data from 9 different state business registries (each with its own format), SEC EDGAR, USASpending, and the Senate lobbying database into a consistent API. Notion MCP handles the output part: turning structured data into a navigable, filterable, relational workspace.

Neither server alone does anything special. Together, they turn "research this company" into a one-prompt operation that produces a structured intelligence workspace with cross-referenced findings across 6 federal data sources.

---

*Built by [@mgrantley](https://github.com/mgrantley). Filed is a free US business entity search API — [filed.dev](https://filed.dev).*
