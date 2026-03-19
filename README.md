# filed-mcp-server

An MCP (Model Context Protocol) server that gives AI agents access to US business entity data via the [Filed.dev](https://filed.dev) API. Search business registrations across 9 US states, SEC EDGAR filings, federal government contracts, and lobbying disclosures — all from any MCP-compatible client.

## Quick Start

### 1. Get a Filed API key

Sign up at [filed.dev](https://filed.dev) — free tier includes 100 lookups/month.

### 2. Add to your MCP client

**Claude Code:**

```bash
claude mcp add filed -- npx -y filed-mcp-server
# Set your API key as an environment variable
export FILED_API_KEY=fd_live_your_key_here
```

Or add to your project's `.mcp.json`:

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

**Cursor:**

Add to `.cursor/mcp.json` in your project root:

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

**Claude Desktop:**

Edit your config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

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

Ask your AI: *"Search for Lockheed Martin business registrations in Florida"* or *"Run a full company intelligence report on Palantir Technologies"*

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

## Demo: Company Intelligence Reports

Sample outputs from `filed_company_intel` for three defense companies:

| Company | States | Entities | Contracts | Lobbying | Output |
|---------|--------|----------|-----------|----------|--------|
| Lockheed Martin | 8/9 | 62 | $4.96B | $925K | [sample-output-lockheed-martin.json](demo/sample-output-lockheed-martin.json) |
| Anduril Industries | 6/9 | 14 | $560M | $1.02M | [sample-output-anduril.json](demo/sample-output-anduril.json) |
| Palantir Technologies | 3/9 | 13 | $350M | $2.1M | [sample-output-palantir.json](demo/sample-output-palantir.json) |

See [demo/prompts.md](demo/prompts.md) for orchestration prompts that pair this server with [Notion MCP](https://github.com/makenotion/notion-mcp-server) to build a structured intelligence workspace.

## Pairing with Notion MCP

This server works well alongside Notion MCP for building persistent, structured intelligence workspaces. Configure both servers:

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

Then ask: *"Research Palantir Technologies using Filed and add the findings to my Notion intelligence hub."*

## Development

```bash
git clone https://github.com/mgrantley/filed-mcp-server.git
cd filed-mcp-server
npm install
npm run build
FILED_API_KEY=your_key node dist/index.js
```

## API Coverage

**State registries:** AK, CO, CT, DC, FL, IA, NY, OR, PA

**Federal sources:**
- SEC EDGAR — company filings (10-K, 10-Q, 8-K, S-1, proxy statements, etc.)
- USASpending.gov — federal government contracts and awards
- Senate LDA — lobbying disclosures (clients, registrants, amounts, issue areas)

More states and sources are added regularly. See [filed.dev/docs](https://filed.dev/docs) for current coverage.

## License

MIT
