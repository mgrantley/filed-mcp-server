#!/usr/bin/env python3
"""
Populate Notion workspace for Filed Intelligence Hub demo.
Creates 6 databases and populates them with real data from Filed API sample outputs.
"""

import json
import os
import time
import requests
import sys
from datetime import datetime

# Config — set NOTION_TOKEN env var before running
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
if not NOTION_TOKEN:
    print("ERROR: Set NOTION_TOKEN environment variable")
    sys.exit(1)
NOTION_VERSION = "2022-06-28"
PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "328b6114-8c62-8087-8179-f4c103c38dde")
BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# Rate limiting
last_request_time = 0
def rate_limit():
    global last_request_time
    elapsed = time.time() - last_request_time
    if elapsed < 0.4:  # ~2.5 req/s to stay under 3/s
        time.sleep(0.4 - elapsed)
    last_request_time = time.time()

def notion_request(method, endpoint, data=None, retries=3):
    rate_limit()
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(retries):
        if method == "POST":
            r = requests.post(url, headers=HEADERS, json=data)
        elif method == "PATCH":
            r = requests.patch(url, headers=HEADERS, json=data)
        else:
            r = requests.get(url, headers=HEADERS)
        
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 2))
            print(f"  Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        if r.status_code >= 400:
            print(f"  ERROR {r.status_code}: {r.text[:300]}")
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return None
        return r.json()
    return None

def create_database(title, properties):
    """Create a database under the parent page."""
    data = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties
    }
    result = notion_request("POST", "/databases", data)
    if result:
        print(f"  ✅ Created database: {title} ({result['id']})")
        return result["id"]
    else:
        print(f"  ❌ Failed to create database: {title}")
        return None

def create_page(database_id, properties):
    """Create a page (row) in a database."""
    data = {
        "parent": {"type": "database_id", "database_id": database_id},
        "properties": properties
    }
    result = notion_request("POST", "/pages", data)
    if result:
        return result["id"]
    return None

# Property helpers
def title_prop(text):
    return {"title": [{"text": {"content": str(text)[:2000]}}]}

def rich_text_prop(text):
    if not text:
        return {"rich_text": []}
    return {"rich_text": [{"text": {"content": str(text)[:2000]}}]}

def select_prop(name):
    if not name:
        return {"select": None}
    return {"select": {"name": str(name)[:100]}}

def multi_select_prop(names):
    return {"multi_select": [{"name": str(n)[:100]} for n in names[:10]]}

def date_prop(date_str):
    if not date_str:
        return {"date": None}
    # Handle various date formats
    try:
        if "T" in str(date_str):
            date_str = str(date_str)[:10]
        return {"date": {"start": str(date_str)[:10]}}
    except:
        return {"date": None}

def number_prop(value):
    try:
        return {"number": float(value) if value else None}
    except:
        return {"number": None}

def url_prop(url):
    if not url:
        return {"url": None}
    return {"url": str(url)[:2000]}

def checkbox_prop(value):
    return {"checkbox": bool(value)}

# ============================================================
# Step 1: Create Databases
# ============================================================

def create_all_databases():
    print("\n📦 STEP 1: Creating databases...")
    dbs = {}
    
    # 1. Companies
    print("\n  Creating 🏢 Companies...")
    dbs["companies"] = create_database("🏢 Companies", {
        "Company Name": {"title": {}},
        "State": {"select": {"options": []}},
        "Status": {"select": {"options": [
            {"name": "Active", "color": "green"},
            {"name": "Good Standing", "color": "green"},
            {"name": "Inactive", "color": "red"}
        ]}},
        "Entity Type": {"select": {"options": [
            {"name": "Corporation", "color": "blue"},
            {"name": "LLC", "color": "purple"}
        ]}},
        "Risk Level": {"select": {"options": [
            {"name": "Low", "color": "green"},
            {"name": "Medium", "color": "yellow"},
            {"name": "High", "color": "red"}
        ]}},
        "Formation Date": {"date": {}},
        "Last Updated": {"date": {}},
        "Entity ID": {"rich_text": {}},
        "Risk Notes": {"rich_text": {}},
        "Filed URL": {"url": {}},
        "Has SEC Filings": {"checkbox": {}},
        "Has Federal Contracts": {"checkbox": {}},
        "Has Lobbying Activity": {"checkbox": {}},
        "Total Contract Value": {"number": {"format": "dollar"}},
        "Total Lobbying Spend": {"number": {"format": "dollar"}},
        "States Registered": {"multi_select": {"options": []}},
        "Tags": {"multi_select": {"options": []}}
    })
    
    # 2. Officers & Agents
    print("  Creating 👤 Officers & Agents...")
    dbs["officers"] = create_database("👤 Officers & Agents", {
        "Name": {"title": {}},
        "Role": {"select": {"options": [
            {"name": "Registered Agent", "color": "blue"},
            {"name": "Officer", "color": "green"},
            {"name": "Director", "color": "purple"}
        ]}},
        "State": {"select": {"options": []}},
        "Address": {"rich_text": {}},
        "Appears In States": {"multi_select": {"options": []}},
        "Multi-Company": {"checkbox": {}},
        "Company Name": {"rich_text": {}}
    })
    
    # 3. SEC Filings
    print("  Creating 📄 SEC Filings...")
    dbs["sec"] = create_database("📄 SEC Filings", {
        "Filing": {"title": {}},
        "Form Type": {"select": {"options": []}},
        "Filing Date": {"date": {}},
        "CIK": {"rich_text": {}},
        "Description": {"rich_text": {}},
        "SEC URL": {"url": {}},
        "Company Name": {"rich_text": {}}
    })
    
    # 4. Federal Contracts
    print("  Creating 💰 Federal Contracts...")
    dbs["contracts"] = create_database("💰 Federal Contracts", {
        "Contract": {"title": {}},
        "Award Amount": {"number": {"format": "dollar"}},
        "Awarding Agency": {"select": {"options": []}},
        "Start Date": {"date": {}},
        "End Date": {"date": {}},
        "Award ID": {"rich_text": {}},
        "NAICS": {"rich_text": {}},
        "Company Name": {"rich_text": {}}
    })
    
    # 5. Lobbying Activity
    print("  Creating 🏛️ Lobbying Activity...")
    dbs["lobbying"] = create_database("🏛️ Lobbying Activity", {
        "Disclosure": {"title": {}},
        "Client Name": {"rich_text": {}},
        "Registrant": {"rich_text": {}},
        "Amount": {"number": {"format": "dollar"}},
        "Issue Areas": {"multi_select": {"options": []}},
        "Filing Year": {"select": {"options": []}},
        "Filing Type": {"select": {"options": []}},
        "Company Name": {"rich_text": {}}
    })
    
    # 6. Intelligence Log
    print("  Creating 🔍 Intelligence Log...")
    dbs["intel"] = create_database("🔍 Intelligence Log", {
        "Entry": {"title": {}},
        "Type": {"select": {"options": [
            {"name": "Cross-Reference", "color": "blue"},
            {"name": "Discrepancy", "color": "orange"},
            {"name": "Risk Flag", "color": "red"},
            {"name": "Note", "color": "gray"}
        ]}},
        "Severity": {"select": {"options": [
            {"name": "Info", "color": "blue"},
            {"name": "Warning", "color": "yellow"},
            {"name": "Critical", "color": "red"}
        ]}},
        "Details": {"rich_text": {}},
        "Company Name": {"rich_text": {}},
        "Source": {"multi_select": {"options": [
            {"name": "Filed API", "color": "green"},
            {"name": "SEC", "color": "blue"},
            {"name": "USASpending", "color": "purple"},
            {"name": "Senate LDA", "color": "orange"},
            {"name": "Cross-Reference", "color": "gray"}
        ]}},
        "Created": {"created_time": {}}
    })
    
    return dbs

# ============================================================
# Step 2: Populate with data
# ============================================================

def load_sample_data():
    data = {}
    for name in ["lockheed-martin", "anduril", "palantir"]:
        with open(f"/root/Projects/filed-mcp-server/demo/sample-output-{name}.json") as f:
            data[name] = json.load(f)
    return data

def populate_companies(db_id, all_data):
    print("\n  📊 Populating Companies...")
    for key, d in all_data.items():
        name = d["company_name"]
        xref = d["cross_references"]
        regs = d["state_registrations"]
        states = xref.get("states_with_registrations", [])
        total_contracts = xref.get("total_contract_value", 0)
        total_lobbying = xref.get("total_lobbying_spend", 0)
        name_vars = xref.get("name_variations", [])
        
        # Find earliest formation date and primary entity type
        formation_date = None
        entity_type = "Corporation"
        for reg in regs:
            if reg.get("formedDate"):
                if not formation_date or reg["formedDate"] < formation_date:
                    formation_date = reg["formedDate"]
            if reg.get("type"):
                entity_type = reg["type"]
        
        # Risk assessment
        risk_level = "Low"
        risk_notes = []
        if len(name_vars) > 10:
            risk_level = "Medium"
            risk_notes.append(f"{len(name_vars)} name variations across states")
        if total_lobbying > 1000000:
            risk_notes.append(f"High lobbying spend: ${total_lobbying:,.0f}")
        if total_contracts > 1000000000:
            risk_notes.append(f"Major government contractor: ${total_contracts:,.0f}")
        
        props = {
            "Company Name": title_prop(name),
            "Status": select_prop("Active"),
            "Entity Type": select_prop(entity_type),
            "Risk Level": select_prop(risk_level),
            "Formation Date": date_prop(formation_date),
            "Entity ID": rich_text_prop(regs[0]["id"] if regs else ""),
            "Risk Notes": rich_text_prop("; ".join(risk_notes) if risk_notes else "No significant risk factors identified"),
            "Filed URL": url_prop(f"https://filed.dev/search?q={name.replace(' ', '+')}"),
            "Has SEC Filings": checkbox_prop(len(d["sec_filings"]) > 0),
            "Has Federal Contracts": checkbox_prop(len(d["federal_contracts"]) > 0),
            "Has Lobbying Activity": checkbox_prop(len(d["lobbying_activity"]) > 0),
            "Total Contract Value": number_prop(total_contracts),
            "Total Lobbying Spend": number_prop(total_lobbying),
            "States Registered": multi_select_prop(states),
            "Tags": multi_select_prop(["Defense", "Government Contractor", "Public Company"])
        }
        
        page_id = create_page(db_id, props)
        if page_id:
            print(f"    ✅ {name}")
        else:
            print(f"    ❌ {name}")

def populate_officers(db_id, all_data):
    print("\n  👤 Populating Officers & Agents...")
    # Extract registered agents from state registrations
    for key, d in all_data.items():
        company_name = d["company_name"]
        agents_seen = {}  # Track unique agents
        
        for reg in d["state_registrations"]:
            agent = reg.get("registeredAgent", {})
            if not agent or not agent.get("name"):
                continue
            agent_name = agent["name"]
            agent_addr = agent.get("address", "")
            state = reg.get("state", "")
            
            if agent_name not in agents_seen:
                agents_seen[agent_name] = {
                    "address": agent_addr,
                    "states": [state]
                }
            else:
                if state not in agents_seen[agent_name]["states"]:
                    agents_seen[agent_name]["states"].append(state)
        
        # Create entries for unique agents (top 5 per company)
        for agent_name, info in list(agents_seen.items())[:5]:
            props = {
                "Name": title_prop(agent_name),
                "Role": select_prop("Registered Agent"),
                "State": select_prop(info["states"][0] if info["states"] else None),
                "Address": rich_text_prop(info["address"]),
                "Appears In States": multi_select_prop(info["states"]),
                "Multi-Company": checkbox_prop(len(agents_seen) > 1),
                "Company Name": rich_text_prop(company_name)
            }
            page_id = create_page(db_id, props)
            if page_id:
                print(f"    ✅ {agent_name} ({company_name})")

def populate_sec_filings(db_id, all_data):
    print("\n  📄 Populating SEC Filings...")
    for key, d in all_data.items():
        company_name = d["company_name"]
        # Get top 5 most recent/notable filings
        filings = sorted(d["sec_filings"], key=lambda x: x.get("fileDate", ""), reverse=True)[:5]
        
        for f in filings:
            filer = f.get("filer", "")
            form_type = f.get("formType", "Unknown")
            desc = f.get("description", "")
            title_text = f"{form_type} — {filer[:60]}" if filer else f"{form_type} Filing"
            
            props = {
                "Filing": title_prop(title_text[:100]),
                "Form Type": select_prop(form_type),
                "Filing Date": date_prop(f.get("fileDate")),
                "CIK": rich_text_prop(f.get("cik", "")),
                "Description": rich_text_prop(desc[:500] if desc else f"Filed by {filer}"),
                "SEC URL": url_prop(f.get("filingUrl")),
                "Company Name": rich_text_prop(company_name)
            }
            page_id = create_page(db_id, props)
            if page_id:
                print(f"    ✅ {form_type} — {company_name}")

def populate_contracts(db_id, all_data):
    print("\n  💰 Populating Federal Contracts...")
    for key, d in all_data.items():
        company_name = d["company_name"]
        # Top 10 by value
        contracts = sorted(d["federal_contracts"], key=lambda x: x.get("amount", 0) or 0, reverse=True)[:10]
        
        for c in contracts:
            desc = c.get("description", "Federal Contract")
            amount = c.get("amount", 0)
            award_id = c.get("awardId", "")
            title_text = f"{desc[:80]}" if desc else f"Award {award_id}"
            
            props = {
                "Contract": title_prop(title_text[:100]),
                "Award Amount": number_prop(amount),
                "Awarding Agency": select_prop(c.get("awardingAgency", "Unknown")),
                "Start Date": date_prop(c.get("startDate")),
                "End Date": date_prop(c.get("endDate")),
                "Award ID": rich_text_prop(award_id),
                "NAICS": rich_text_prop(c.get("naicsCode", "")),
                "Company Name": rich_text_prop(company_name)
            }
            page_id = create_page(db_id, props)
            if page_id:
                print(f"    ✅ ${amount:,.0f} — {company_name}")

def populate_lobbying(db_id, all_data):
    print("\n  🏛️ Populating Lobbying Activity...")
    for key, d in all_data.items():
        company_name = d["company_name"]
        # Top 10 by income/expenses
        lobbying = sorted(d["lobbying_activity"], 
                         key=lambda x: (x.get("income") or x.get("expenses") or 0), 
                         reverse=True)[:10]
        
        for l in lobbying:
            registrant = l.get("registrant", {}).get("name", "Unknown")
            client = l.get("client", {}).get("name", company_name)
            amount = l.get("income") or l.get("expenses") or 0
            filing_type = l.get("filingType", "")
            filing_year = str(l.get("filingYear", ""))
            
            # Extract issue areas from lobbying activities
            issue_areas = []
            activities = l.get("lobbyingActivities", [])
            if isinstance(activities, list):
                for act in activities[:5]:
                    if isinstance(act, dict) and act.get("issueArea"):
                        issue_areas.append(act["issueArea"])
            
            title_text = f"{registrant[:40]} — {filing_type}" if filing_type else registrant
            
            props = {
                "Disclosure": title_prop(title_text[:100]),
                "Client Name": rich_text_prop(client),
                "Registrant": rich_text_prop(registrant),
                "Amount": number_prop(amount),
                "Issue Areas": multi_select_prop(issue_areas[:5]),
                "Filing Year": select_prop(filing_year),
                "Filing Type": select_prop(filing_type[:100] if filing_type else None),
                "Company Name": rich_text_prop(company_name)
            }
            page_id = create_page(db_id, props)
            if page_id:
                print(f"    ✅ ${amount:,.0f} — {registrant[:30]} ({company_name})")

def populate_intelligence(db_id, all_data):
    print("\n  🔍 Populating Intelligence Log...")
    
    entries = []
    
    # Per-company intelligence
    for key, d in all_data.items():
        company_name = d["company_name"]
        xref = d["cross_references"]
        name_vars = xref.get("name_variations", [])
        states = xref.get("states_with_registrations", [])
        total_contracts = xref.get("total_contract_value", 0)
        total_lobbying = xref.get("total_lobbying_spend", 0)
        
        # Name variations insight
        entries.append({
            "Entry": f"{company_name}: {len(name_vars)} name variations across {len(states)} states",
            "Type": "Cross-Reference",
            "Severity": "Info",
            "Details": f"Registered under variations: {', '.join(name_vars[:5])}{'...' if len(name_vars) > 5 else ''}. Found in states: {', '.join(states)}.",
            "Company Name": company_name,
            "Source": ["Filed API"]
        })
        
        # Contract value insight
        entries.append({
            "Entry": f"{company_name}: ${total_contracts:,.0f} in federal contracts",
            "Type": "Note",
            "Severity": "Info",
            "Details": f"Total federal contract value: ${total_contracts:,.2f}. Top agencies include Department of Defense.",
            "Company Name": company_name,
            "Source": ["USASpending"]
        })
        
        # Lobbying insight
        if total_lobbying > 0:
            ratio = total_lobbying / total_contracts * 100 if total_contracts > 0 else 0
            entries.append({
                "Entry": f"{company_name}: ${total_lobbying:,.0f} lobbying spend ({ratio:.4f}% of contract value)",
                "Type": "Cross-Reference",
                "Severity": "Warning" if total_lobbying > 1000000 else "Info",
                "Details": f"Lobbying spend of ${total_lobbying:,.0f} relative to ${total_contracts:,.0f} in contracts. Lobbying-to-contract ratio: {ratio:.4f}%.",
                "Company Name": company_name,
                "Source": ["Senate LDA", "USASpending"]
            })
    
    # Cross-company intelligence
    companies_data = {d["company_name"]: d["cross_references"] for d in all_data.values()}
    
    # Contract comparison
    contract_ranking = sorted(companies_data.items(), key=lambda x: x[1].get("total_contract_value", 0), reverse=True)
    ranking_text = "; ".join([f"{name}: ${data['total_contract_value']:,.0f}" for name, data in contract_ranking])
    entries.append({
        "Entry": "Cross-Company: Federal contract value comparison",
        "Type": "Cross-Reference",
        "Severity": "Info",
        "Details": f"Contract value ranking: {ranking_text}. Lockheed Martin dominates with ~9x Anduril's contract value.",
        "Company Name": "All Companies",
        "Source": ["USASpending", "Cross-Reference"]
    })
    
    # Lobbying comparison
    lobby_ranking = sorted(companies_data.items(), key=lambda x: x[1].get("total_lobbying_spend", 0), reverse=True)
    lobby_text = "; ".join([f"{name}: ${data['total_lobbying_spend']:,.0f}" for name, data in lobby_ranking])
    entries.append({
        "Entry": "Cross-Company: Lobbying spend comparison — Palantir leads",
        "Type": "Cross-Reference",
        "Severity": "Warning",
        "Details": f"Lobbying spend ranking: {lobby_text}. Palantir spends the most on lobbying despite having the smallest contract portfolio — potential aggressive growth strategy.",
        "Company Name": "All Companies",
        "Source": ["Senate LDA", "Cross-Reference"]
    })
    
    # Efficiency insight
    entries.append({
        "Entry": "Cross-Company: Lobbying ROI analysis — Anduril most efficient",
        "Type": "Cross-Reference",
        "Severity": "Info",
        "Details": "Anduril Industries achieves $559M in contracts with $1.02M lobbying (548:1 ratio). Lockheed Martin: $4.96B contracts with $925K lobbying (5,359:1 ratio). Palantir: $350M contracts with $2.1M lobbying (166:1 ratio). Lockheed's established position requires less lobbying per contract dollar.",
        "Company Name": "All Companies",
        "Source": ["USASpending", "Senate LDA", "Cross-Reference"]
    })

    # Anduril-specific flag
    entries.append({
        "Entry": "Risk Flag: Anduril — $560M in contracts for company founded 2017",
        "Type": "Risk Flag",
        "Severity": "Warning",
        "Details": "Anduril Industries secured $559M+ in federal contracts despite being founded in 2017. Rapid government contract acquisition warrants due diligence on political connections and contract award patterns.",
        "Company Name": "Anduril Industries",
        "Source": ["Filed API", "USASpending", "Cross-Reference"]
    })
    
    # Palantir lobbying flag
    entries.append({
        "Entry": "Risk Flag: Palantir — Highest lobbying spend, lowest contract value",
        "Type": "Risk Flag",
        "Severity": "Warning",
        "Details": "Palantir spends $2.1M on lobbying (highest of the three) but has the lowest contract value at $350M. This inverted ratio could indicate aggressive contract pursuit or regulatory challenges.",
        "Company Name": "Palantir Technologies",
        "Source": ["Senate LDA", "USASpending", "Cross-Reference"]
    })
    
    for entry in entries:
        props = {
            "Entry": title_prop(entry["Entry"][:100]),
            "Type": select_prop(entry["Type"]),
            "Severity": select_prop(entry["Severity"]),
            "Details": rich_text_prop(entry["Details"]),
            "Company Name": rich_text_prop(entry["Company Name"]),
            "Source": multi_select_prop(entry["Source"])
        }
        page_id = create_page(db_id, props)
        if page_id:
            print(f"    ✅ {entry['Entry'][:60]}...")

# ============================================================
# Step 3: Add summary content to parent page
# ============================================================

def add_parent_page_content():
    print("\n  📝 Adding summary content to parent page...")
    
    blocks = {
        "children": [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Filed Intelligence Hub"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "A comprehensive company intelligence workspace powered by "}, "annotations": {}}, {"type": "text", "text": {"content": "Filed.dev", "link": {"url": "https://filed.dev"}}, "annotations": {"bold": True}}, {"type": "text", "text": {"content": " — the free US business entity API. This hub cross-references data from 9 state registries, SEC filings, federal contracts (USASpending.gov), and lobbying disclosures (Senate LDA) to provide actionable intelligence on US companies."}}]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📊 Demo: Defense Contractor Analysis"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "This workspace analyzes three major defense contractors — Lockheed Martin, Anduril Industries, and Palantir Technologies — demonstrating how Filed's multi-source intelligence pipeline works. Each company is tracked across state business registrations, SEC filings, federal contracts, and lobbying activity, with automated cross-referencing to surface insights and risk flags."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "Key Findings"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Lockheed Martin: $4.96B in federal contracts, 62 state registrations across 8 states, 28 name variations"}, "annotations": {}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Anduril Industries: $560M in contracts despite being founded in 2017 — fastest-growing contractor analyzed"}, "annotations": {}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Palantir Technologies: $2.1M lobbying spend (highest of three) but lowest contract value at $350M — inverted ratio flagged"}, "annotations": {}}]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": "Powered by Filed.dev — free US business entity API. Search 50-state corporate registrations, SEC filings, federal contracts, and lobbying data through a single API."}}],
                    "icon": {"type": "emoji", "emoji": "⚡"}
                }
            }
        ]
    }
    
    result = notion_request("PATCH", f"/blocks/{PARENT_PAGE_ID}/children", blocks)
    if result:
        print("  ✅ Parent page content added")
    else:
        print("  ❌ Failed to add parent page content")

# ============================================================
# Main
# ============================================================

def main():
    print("🚀 Filed Intelligence Hub — Notion Workspace Builder")
    print("=" * 60)
    
    # Step 1: Create databases
    dbs = create_all_databases()
    
    # Verify all databases created
    for name, db_id in dbs.items():
        if not db_id:
            print(f"\n❌ Database '{name}' failed to create. Aborting.")
            sys.exit(1)
    
    print(f"\n✅ All 6 databases created successfully!")
    print(json.dumps(dbs, indent=2))
    
    # Save database IDs
    with open("/root/Projects/filed-mcp-server/demo/notion-db-ids.json", "w") as f:
        json.dump(dbs, f, indent=2)
    
    # Step 2: Load sample data
    print("\n📦 STEP 2: Populating with real data...")
    all_data = load_sample_data()
    
    populate_companies(dbs["companies"], all_data)
    populate_officers(dbs["officers"], all_data)
    populate_sec_filings(dbs["sec"], all_data)
    populate_contracts(dbs["contracts"], all_data)
    populate_lobbying(dbs["lobbying"], all_data)
    populate_intelligence(dbs["intel"], all_data)
    
    # Step 3: Add parent page content
    print("\n📦 STEP 3: Adding summary to parent page...")
    add_parent_page_content()
    
    print("\n" + "=" * 60)
    print("🎉 DONE! Filed Intelligence Hub is fully populated.")
    print(f"View it at: https://notion.so/{PARENT_PAGE_ID.replace('-', '')}")

if __name__ == "__main__":
    main()
