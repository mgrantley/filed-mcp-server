# filed-mcp-server

An MCP (Model Context Protocol) server that gives AI agents access to US business entity data via the [Filed.dev](https://filed.dev) API. Search business registrations across 9 US states, SEC EDGAR filings, federal government contracts, and lobbying disclosures — all from Claude Desktop, Cursor, or any MCP-compatible client.

## Quick Start

### 1. Get a Filed API key

Sign up at [filed.dev](https://filed.dev) — free tier includes 100 lookups/month.

### 2. Add to Claude Desktop

Edit your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "filed": {
      "command": "npx",
      "args": ["-y", "filed-mcp-server"],
      "env": {
        "FILED_API_KEY": "fd_live_your_key_here"
      }
    }
  }
}
```

### 3. Use it

Ask Claude: *"Search for Lockheed Martin business registrations in Florida"* or *"Run a full company intelligence report on Palantir Technologies"*

## Tools

| Tool | Description |
|------|-------------|
| `filed_search_entities` | Search business entities by name in any of 9 US states (AK, CO, CT, DC, FL, IA, NY, OR, PA) |
| `filed_get_entity` | Get full entity details — officers, registered agent, filing history. Optionally enrich with federal data. |
| `filed_search_sec` | Search SEC EDGAR for company filings (10-K, 10-Q, 8-K, S-1, etc.) |
| `filed_search_contracts` | Search federal government contracts from USASpending.gov |
| `filed_search_lobbying` | Search lobbying disclosures from the Senate LDA database |
| `filed_company_intel` | **Power tool** — searches all 9 states + SEC + contracts + lobbying for a company, returns unified intelligence report with cross-references |

## Example Prompts

- "Search for Amazon business registrations in New York"
- "Get the full details for entity FL:P06000113830 including federal data"
- "Find SEC 10-K filings for Tesla"
- "What federal contracts has Booz Allen Hamilton received?"
- "Who lobbies for Pfizer and on what issues?"
- "Run a comprehensive intelligence report on Anduril Industries"

## Development

```bash
git clone https://github.com/mgrantley/filed-mcp-server.git
cd filed-mcp-server
npm install
npm run build
FILED_API_KEY=your_key node dist/index.js
```

## License

MIT
