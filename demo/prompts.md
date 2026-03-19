# Filed Intelligence Hub — Orchestration Prompts

These prompts drive Claude Code (or any MCP client) with **both** the Filed MCP server and Notion MCP server configured to build and populate a company intelligence workspace.

## Prerequisites

MCP client config with both servers:

```json
{
  "mcpServers": {
    "filed": {
      "command": "npx",
      "args": ["-y", "filed-mcp-server"],
      "env": {
        "FILED_API_KEY": "your_key_here"
      }
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ntn_your_token\", \"Notion-Version\": \"2022-06-28\"}"
      }
    }
  }
}
```

---

## Prompt 1: Create the Workspace

```
Create a "Filed Intelligence Hub" in my Notion workspace. Set up these 6 databases:

1. **🏢 Companies** — master entity tracker with properties:
   - Company Name (title), State (select), Status (select: Active/Inactive/Dissolved/Suspended),
     Entity Type (select: LLC/Corporation/LP/Nonprofit), Formation Date (date),
     Entity ID (text), Filed URL (url), Risk Level (select: 🟢 Low/🟡 Medium/🔴 High),
     Risk Notes (text), Last Updated (date), Has SEC Filings (checkbox),
     Has Federal Contracts (checkbox), Has Lobbying Activity (checkbox),
     Total Contract Value (number/currency), Tags (multi-select)

2. **👤 Officers & Agents** — people connected to companies:
   - Name (title), Role (select: Officer/Director/Registered Agent/Manager/President/Secretary),
     Company (relation → Companies), State (select), Address (text),
     Appears In States (multi-select), Multi-Company (checkbox)

3. **📄 SEC Filings** — EDGAR filings:
   - Filing (title), Company (relation → Companies), Form Type (select: 10-K/10-Q/8-K/S-1/DEF 14A/13F-HR),
     Filing Date (date), CIK (text), Description (text), SEC URL (url)

4. **💰 Federal Contracts** — USASpending data:
   - Contract (title), Company (relation → Companies), Award Amount (number/currency),
     Awarding Agency (select), Start Date (date), End Date (date),
     Award ID (text), NAICS (text)

5. **🏛️ Lobbying Activity** — Senate LDA disclosures:
   - Disclosure (title), Company (relation → Companies), Client Name (text),
     Registrant (text), Amount (number/currency), Issue Areas (multi-select),
     Filing Year (select), Filing Type (select: Q1/Q2/Q3/Q4/RR)

6. **🔍 Intelligence Log** — cross-reference findings:
   - Entry (title), Company (relation → Companies),
     Type (select: Cross-Reference/Discrepancy/Risk Flag/Note),
     Severity (select: Info/Warning/Critical), Details (text),
     Source (multi-select: State Filing/SEC/Contracts/Lobbying)

Create useful views for each:
- Companies: "All Companies" table, "By State" board, "Risk Dashboard" (filtered to Medium+High risk)
- Officers: "All Officers" table, "Cross-State Flags" (filtered to Multi-Company = true)
- SEC Filings: "All Filings" table sorted by date, "By Form Type" board
- Contracts: "All Contracts" sorted by amount, "By Agency" board, "Big Contracts" (>$100K)
- Lobbying: "All Disclosures" sorted by amount, "By Issue Area" board
- Intelligence Log: "All Intel" sorted by date, "Risk Flags Only" (Warning+Critical)
```

---

## Prompt 2: Research Lockheed Martin

```
Research Lockheed Martin using the Filed MCP server. Run filed_company_intel to search all 9 states for business registrations, SEC filings, federal contracts, and lobbying activity.

Then add all findings to my Filed Intelligence Hub in Notion:

1. Add each state registration as a row in the Companies database (with entity ID, status, formation date, state)
2. Add officers found across states to the Officers database. Flag anyone who appears in multiple states or multiple entities with Multi-Company = true
3. Add SEC filings to the SEC Filings database (form type, date, CIK, link)
4. Add the top federal contracts to the Federal Contracts database (amount, agency, dates)
5. Add lobbying disclosures to the Lobbying Activity database (registrant, amount, issue areas)
6. In the Intelligence Log, add entries for:
   - Total federal contract value across all awards
   - Number of lobbying firms retained and total spend
   - Any officer overlap across states
   - Overall risk assessment (defense sector concentration, government revenue dependency)

Set the main Companies entry risk level based on your analysis.
```

---

## Prompt 3: Research Anduril Industries

```
Now research Anduril Industries the same way — run filed_company_intel and populate all the Notion databases.

Anduril is a defense AI/autonomy startup. Pay special attention to:
- Their state registrations (they're growing fast, may be in many states)
- Federal contracts (they're a newer defense contractor — compare contract volume to Lockheed Martin)
- Lobbying activity (are they lobbying on the same issues as Lockheed?)
- Any officer/agent overlap with Lockheed Martin

Add everything to the Intelligence Hub and log cross-references in the Intelligence Log.
```

---

## Prompt 4: Research Palantir Technologies

```
Research Palantir Technologies — same process. Run filed_company_intel and add to Notion.

Palantir is a data analytics company with heavy government contracts. Focus on:
- Their SEC filings (they're publicly traded — should have 10-K, 10-Q, 8-K filings)
- Federal contract distribution across agencies (are they concentrated in defense like Lockheed, or spread across civilian agencies too?)
- Lobbying topics (what policy areas do they care about?)
- Any connections to the other companies already in the hub

Populate all databases and add intelligence log entries for notable findings.
```

---

## Prompt 5: Cross-Reference Analysis

```
Now analyze the full Intelligence Hub across all three companies:

1. **Officer overlap**: Read the Officers database. Are there any people who appear across multiple companies? Any shared registered agents?

2. **Contract competition**: Compare federal contract values and agencies across all 3 companies. Are they competing for the same agency dollars? Create an intelligence log entry summarizing the competitive landscape.

3. **Lobbying correlation**: Compare lobbying issue areas. Are all three lobbying on DEF (Defense)? Any unique issue areas for specific companies? Does lobbying spend correlate with contract value?

4. **Risk comparison**: Update risk levels for all three companies. Consider:
   - Government revenue concentration risk
   - Regulatory exposure (SEC filing frequency, lobbying intensity)
   - Geographic footprint (states with registrations)

5. Create a summary Intelligence Log entry titled "Three-Company Comparative Analysis" with your findings.
```

---

## Prompt 6: Generate Risk Report

```
Create a new page in Notion titled "📊 Filed Intelligence Hub — Executive Summary" with:

1. **Portfolio Overview**: Table of all 3 companies with state count, total contract value, lobbying spend, and risk level
2. **Key Findings**: Top 3-5 intelligence insights from the cross-reference analysis
3. **Risk Matrix**: Summary of risk factors by company
4. **Data Sources**: List of all data sources used (9 state registries, SEC EDGAR, USASpending, Senate LDA)
5. **Methodology**: Brief description of how the data was gathered (Filed MCP server → Notion MCP server)

End with: "This intelligence hub was built entirely through natural language prompts using Filed.dev's free API and Notion MCP. Total research time: ~10 minutes."
```
