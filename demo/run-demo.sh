#!/bin/bash
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"

cd /root/Projects/filed-mcp-server

DEMO_PROMPT='You have access to two MCP servers: Filed (US business entity data) and Notion (workspace management).

Your task: Perform a due diligence investigation on three defense companies — Lockheed Martin, Anduril Industries, and Palantir Technologies — and build a structured intelligence workspace in Notion.

The Notion parent page ID is: 329b6114-8c62-8130-8aab-d1982985b2bc

Step by step:

1. First, create a "Companies" database in Notion under that page with properties: Company Name (title), States Found (rich_text), Total Contract Value (number), Lobbying Spend (number), Risk Level (select with options Low/Medium/High), Status Notes (rich_text).

2. Use filed_company_intel to research each company. Search all states.

3. For each company, add a row to the Companies database with the real data.

4. Create an "Intelligence Findings" database with properties: Finding (title), Company (rich_text), Severity (select: Info/Warning/Critical), Details (rich_text), Action Required (rich_text).

5. Analyze the data across all three companies. Look for:
   - Any entity with non-Active status (Revoked, Non-Compliant, Withdrawn)
   - States where companies have federal contracts but NO state registration
   - Unusual lobbying-to-contract ratios compared to peers  
   - Any other discrepancies or risk flags

6. Add each finding to the Intelligence Findings database with specific, actionable details.

Be thorough. The goal is to show that AI + Filed data can surface real compliance risks that would take a human analyst hours to find manually.'

claude -p "$DEMO_PROMPT" \
  --allowedTools "mcp__filed__filed_company_intel,mcp__filed__filed_search_entities,mcp__filed__filed_get_entity,mcp__filed__filed_search_sec,mcp__filed__filed_search_contracts,mcp__filed__filed_search_lobbying,mcp__notion__API-post-page,mcp__notion__API-create-a-data-source,mcp__notion__API-post-search,mcp__notion__API-query-data-source,mcp__notion__API-patch-page,mcp__notion__API-retrieve-a-page,mcp__notion__API-retrieve-a-data-source,Bash" \
  --max-turns 30 \
  --output-format json 2>/dev/null
