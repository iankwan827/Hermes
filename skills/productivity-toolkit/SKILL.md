---
name: productivity-toolkit
description: "Productivity integrations: location intelligence (geocoding, POIs, routes) and Notion workspace management."
version: 1.0.0
tags: [productivity, maps, geocoding, notion, workspace, integration]
metadata:
  hermes:
    tags: [productivity, maps, geocoding, notion, workspace, integration]
    category: productivity
---

# Productivity Toolkit

Unified skill for productivity tool integrations — location intelligence
and workspace management.

## Supported Tools

| Tool | Key Operations |
|------|----------------|
| **Maps** | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM |
| **Notion** | Pages, databases, markdown, Workers via API + ntn CLI |

---

## Maps (Location Intelligence)

Location intelligence using free, open data sources. 8 commands, 46 POI
categories, zero dependencies (Python stdlib only), no API key required.

Data sources: OpenStreetMap/Nominatim, Overpass API, OSRM, TimeAPI.io.

### Prerequisites

Python 3.8+ (stdlib only). Script: `scripts/maps_client.py`

### Commands

```bash
MAPS=~/.hermes/skills/productivity-toolkit/scripts/maps_client.py

# Geocode a place name
python3 $MAPS search "Eiffel Tower"

# Coordinates to address
python3 $MAPS reverse 48.8584 2.2945

# Find nearby places
python3 $MAPS nearby 48.8584 2.2945 restaurant --limit 10
python3 $MAPS nearby --near "Times Square, New York" --category cafe

# Travel distance and time
python3 $MAPS distance "Paris" --to "Lyon" --mode driving

# Turn-by-turn directions
python3 $MAPS directions "Eiffel Tower" --to "Louvre Museum" --mode walking

# Timezone for coordinates
python3 $MAPS timezone 48.8584 2.2945

# Bounding box for a place
python3 $MAPS area "Manhattan, New York"

# Search within bounding box
python3 $MAPS bbox 40.75 -74.00 40.77 -73.98 restaurant --limit 20
```

### 46 POI Categories

restaurant, cafe, bar, hospital, pharmacy, hotel, guest_house, camp_site,
supermarket, atm, gas_station, parking, museum, park, school, university,
bank, police, fire_station, library, airport, train_station, bus_stop,
church, mosque, synagogue, dentist, doctor, cinema, theatre, gym,
swimming_pool, post_office, convenience_store, bakery, bookshop, laundry,
car_wash, car_rental, bicycle_rental, taxi, veterinary, zoo, playground,
stadium, nightclub.

Each result includes: name, address, lat/lon, distance_m, maps_url,
directions_url, and promoted tags (cuisine, hours, phone, website).

### Working With Telegram Location Pins

When a user sends a location pin, extract lat/lon and pass to `nearby`:
```bash
python3 $MAPS nearby 36.17 -115.14 cafe --radius 1500
```

### Pitfalls
- Nominatim ToS: max 1 req/s (handled automatically)
- `nearby` requires lat/lon OR `--near "<address>"`
- OSRM routing coverage best for Europe and North America
- Overpass API can be slow during peak hours; script auto-falls back between mirrors

---

## Notion (Workspace Management)

Talk to Notion two ways — `ntn` CLI (preferred, macOS/Linux) or HTTP + curl (cross-platform).

### Setup

1. Create integration at https://notion.so/my-integrations
2. Store API key in `~/.hermes/.env`: `NOTION_API_KEY=ntn_your_key_here`
3. Share target pages/databases with the integration in Notion
4. Install `ntn`: `curl -fsSL https://ntn.dev | bash`

### API Basics

`Notion-Version: 2025-09-03` required on all HTTP requests. In this version,
"databases" are called **data sources** in the API.

### Path A — ntn CLI (preferred)

```bash
# Search
ntn api v1/search query="page title"

# Read page as Markdown
ntn api v1/pages/{page_id}/markdown

# Create page from Markdown
ntn api v1/pages parent[page_id]=xxx \
  properties[title][0][text][content]="Notes from meeting" \
  markdown="# Agenda\n\n- Q3 roadmap"

# Query a database
ntn api v1/data_sources/{data_source_id}/query -X POST \
  filter[property]=Status filter[select][equals]=Active

# File uploads (one-liner)
ntn files create < photo.png
```

### Path B — HTTP + curl

```bash
# Search
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'

# Read page as Markdown
curl -s "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Property Types

- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Date:** `{"date": {"start": "2026-01-15"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`

### Databases vs Data Sources

- **Databases became data sources.** Use `/data_sources/` endpoints for queries.
- Two IDs per database: `database_id` (for creating pages) and `data_source_id` (for querying).

### Notion Workers (advanced, requires ntn)

Workers are TypeScript programs Notion hosts — syncs, tools, webhooks.
Requires Business or Enterprise plan.

```bash
ntn workers new my-worker      # scaffold
ntn workers deploy              # deploy
ntn workers list                # list workers
ntn workers runs list           # recent invocations
```

### Notion-Flavored Markdown

Standard CommonMark plus XML-like tags:
```markdown
<callout icon="🎯" color="blue_bg">
  Ship the MVP by **Friday**.
</callout>

<columns>
  <column>Left side</column>
  <column>Right side</column>
</columns>
```

Inline: `<mention-user url="..."/>`, `<mention-page url="...">Title</mention-page>`,
`<span color="blue">text</span>`, math `$x^2$`.

### Notes
- Page/database IDs are UUIDs (with or without dashes)
- Rate limit: ~3 requests/second
- The API cannot set database view filters (UI-only)
- Use `ntn api v1/pages/{id}/markdown` for agent-friendly reading

---

## Adding More Tools

To add a new productivity integration:
1. Create the SKILL.md section above with setup, commands, and pitfalls
2. Add any scripts to `scripts/`
3. Add any reference files to `references/`
