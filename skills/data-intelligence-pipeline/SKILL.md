---
name: data-intelligence-pipeline
description: Build end-to-end data pipelines that fetch, analyze, synthesize, and visualize intelligence from Slack channels, documents, and other sources using incremental processing and AI extraction. Use when building "data pipelines", "intelligence gathering", "Slack analysis", or "data synthesis dashboards".
---

# Data Intelligence Pipeline

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| data-intelligence | "data pipeline", "intelligence gathering", "Slack analysis", "data synthesis dashboard" | High | 5 projects |

Build a complete intelligence pipeline that ingests data from Slack channels, document directories, and other sources, runs each thread or document through Claude-powered extraction to identify customers, experiments, accelerators, gaps, and micro-learnings, then synthesizes cross-source findings into KPIs and funnel stages, and finally renders everything as an interactive single-page HTML dashboard. The pipeline is fully incremental: it tracks what has been fetched and analyzed, skips unchanged items, and can be stopped and resumed at any stage.

## When to Use

- Building a team intelligence dashboard that aggregates insights from Slack conversations
- Extracting structured data (customers, experiments, learnings) from unstructured thread discussions
- Creating a cross-channel synthesis that merges findings by customer or topic
- Generating weekly or monthly readout reports from accumulated intelligence
- Ingesting supplementary data from Excel files or text documents alongside Slack data
- Tracking pipeline health with a status command that shows fetch/analyze/synthesize progress

## Instructions

### Architecture Overview

The pipeline has five sequential stages. Each stage reads from the previous stage's output and writes its own output to disk. Stages can be run independently.

```
Fetch  -->  Analyze  -->  Synthesize  -->  Dashboard  -->  Deploy
(Slack)     (Claude)      (merge/KPI)     (HTML gen)      (optional)
```

All pipeline data lives in a structured directory:

```
data/
  raw/                    # Fetch stage output
    slack/
      {channel}/
        threads.json      # Raw thread data per channel
    documents/
      {source}/
        *.json            # Ingested documents
  extractions/            # Analyze stage output
    {extraction_id}.json  # One file per analyzed thread
  synthesis/              # Synthesize stage output
    customers.json        # Merged customer profiles
    kpis.json             # Computed KPIs
    funnel.json           # Funnel stage assignments
  dashboard/              # Dashboard stage output
    index.html            # Single-page interactive dashboard
.state/
  pipeline_state.json     # Incremental processing state
  analysis_index.json     # Hash-based change detection index
```

---

### Stage 1: Fetch

The Fetch stage pulls raw data from source systems and stores it locally. It uses incremental fetching to avoid re-downloading old data.

#### Slack Integration

```python
import os
import json
import time
from slack_sdk import WebClient
from pathlib import Path

class SlackFetcher:
    def __init__(self, state_manager):
        self.client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
        self.state = state_manager

    def fetch_channel(self, channel_id: str, channel_name: str):
        """Fetch new messages and threads from a Slack channel since last checkpoint."""
        last_ts = self.state.get_last_ts(channel_id)

        # Fetch conversation history (incremental)
        messages = []
        cursor = None
        while True:
            resp = self.client.conversations_history(
                channel=channel_id,
                oldest=last_ts or '0',
                limit=200,
                cursor=cursor
            )
            messages.extend(resp['messages'])
            cursor = resp.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break
            time.sleep(1.2)  # Slack rate limit: ~1 req/sec for Tier 3

        # Resolve threads (fetch full replies for threaded messages)
        threads = []
        for msg in messages:
            if msg.get('reply_count', 0) > 0:
                thread_msgs = self._fetch_thread(channel_id, msg['ts'])
                threads.append({
                    'parent': msg,
                    'replies': thread_msgs,
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'thread_ts': msg['ts'],
                    'message_count': len(thread_msgs) + 1
                })
            time.sleep(0.5)  # Pace thread fetches

        # Resolve user display names
        self._resolve_users(threads)

        # Save raw data
        output_dir = Path(f'data/raw/slack/{channel_name}')
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / 'threads.json', 'w') as f:
            json.dump(threads, f, indent=2, default=str)

        # Update checkpoint
        if messages:
            newest_ts = max(m['ts'] for m in messages)
            self.state.set_last_ts(channel_id, newest_ts, len(messages), len(threads))

        return {'messages': len(messages), 'threads': len(threads)}

    def _fetch_thread(self, channel_id, thread_ts):
        resp = self.client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=200
        )
        return resp['messages'][1:]  # Skip parent message (already have it)

    def _resolve_users(self, threads):
        user_cache = {}
        for thread in threads:
            all_msgs = [thread['parent']] + thread['replies']
            for msg in all_msgs:
                uid = msg.get('user', '')
                if uid and uid not in user_cache:
                    try:
                        info = self.client.users_info(user=uid)
                        profile = info['user']['profile']
                        user_cache[uid] = profile.get('display_name') or profile.get('real_name', uid)
                    except Exception:
                        user_cache[uid] = uid
                msg['user_name'] = user_cache.get(uid, uid)
```

**Auth test before fetching**: Always run `auth_test()` first to verify the token is valid and has the required scopes: `channels:history`, `channels:read`, `users:read`.

#### Cross-Channel Link Crawling

Slack messages often reference threads in other channels via links like `https://team.slack.com/archives/C123456/p1234567890`. Extract these links and fetch the referenced threads even if the target channel is not in your primary fetch list.

```python
import re

SLACK_LINK_RE = re.compile(r'https://\w+\.slack\.com/archives/(\w+)/p(\d+)')

def extract_cross_channel_links(threads):
    """Find all Slack thread links referenced in messages."""
    links = []
    for thread in threads:
        for msg in [thread['parent']] + thread['replies']:
            for match in SLACK_LINK_RE.finditer(msg.get('text', '')):
                links.append({
                    'channel_id': match.group(1),
                    'thread_ts': match.group(2)[:10] + '.' + match.group(2)[10:]
                })
    return links
```

#### Document Ingestion

For supplementary data from Excel files, CSVs, or text documents:

```python
def ingest_directory(source_dir: str, source_name: str):
    """Ingest documents from a local directory into the pipeline data format."""
    output_dir = Path(f'data/raw/documents/{source_name}')
    output_dir.mkdir(parents=True, exist_ok=True)

    for file_path in Path(source_dir).glob('*'):
        if file_path.suffix in ('.xlsx', '.xls'):
            records = parse_excel(file_path)
        elif file_path.suffix == '.csv':
            records = parse_csv(file_path)
        elif file_path.suffix in ('.txt', '.md'):
            records = [{'content': file_path.read_text(), 'source': file_path.name}]
        else:
            continue

        output_file = output_dir / f'{file_path.stem}.json'
        with open(output_file, 'w') as f:
            json.dump(records, f, indent=2)
```

---

### Stage 2: Analyze (Claude-Powered Extraction)

The Analyze stage sends each thread or document through Claude to extract structured intelligence. This is the most expensive stage (API calls), so it uses hash-based caching aggressively.

#### Thread Filtering

Not every thread is worth analyzing. Apply these filters before sending to Claude:

```python
MIN_MESSAGES = 1        # At least 1 reply (not just a solo post)
MIN_WORD_COUNT = 20     # Skip very short threads
MAX_WORDS = 6000        # Truncate extremely long threads to control token usage

def should_analyze(thread):
    word_count = sum(len(m.get('text', '').split()) for m in [thread['parent']] + thread['replies'])
    return (
        thread['message_count'] >= MIN_MESSAGES and
        word_count >= MIN_WORD_COUNT
    )

def prepare_thread_text(thread):
    """Format thread into a readable text block for Claude, respecting MAX_WORDS."""
    lines = []
    all_msgs = [thread['parent']] + thread['replies']
    for msg in all_msgs:
        name = msg.get('user_name', 'Unknown')
        text = msg.get('text', '')
        lines.append(f"[{name}]: {text}")

    full_text = '\n'.join(lines)
    words = full_text.split()
    if len(words) > MAX_WORDS:
        full_text = ' '.join(words[:MAX_WORDS]) + '\n[... truncated]'
    return full_text
```

#### Claude Extraction Prompt

Send each thread to Claude with a structured extraction prompt. The prompt must request a specific JSON schema to ensure consistent output.

```python
EXTRACTION_PROMPT = """Analyze this Slack thread and extract structured intelligence.

Thread from #{channel_name} on {date}:
---
{thread_text}
---

Extract the following as JSON. Be specific and quote the thread where possible.
Every field must be present even if the array is empty.

{
  "customers": [{"name": "...", "context": "..."}],
  "stakeholders": [{"name": "...", "role": "...", "stance": "..."}],
  "experiments": [{"title": "...", "status": "...", "outcome": "..."}],
  "accelerators": [{"title": "...", "description": "...", "impact": "high|medium|low"}],
  "micro_learnings": [{"insight": "...", "source": "..."}],
  "gaps": [{"description": "...", "severity": "high|medium|low"}],
  "thread_summary": "2-3 sentence summary of the thread's key discussion"
}"""
```

See the extraction schema reference (`references/extraction-schema.md`) for the full ThreadExtraction type definition and field-level documentation.

#### Hash-Based Caching

Before calling Claude, compute a SHA-256 hash of the thread text and check the analysis index. If the hash matches a previous extraction, skip the API call entirely.

```python
import hashlib

def analyze_thread(thread, channel_name, analysis_index, claude_client):
    thread_text = prepare_thread_text(thread)
    content_hash = hashlib.sha256(thread_text.encode('utf-8')).hexdigest()[:16]

    thread_key = f"{thread['channel_id']}:{thread['thread_ts']}"

    # Check cache
    if not analysis_index.is_stale('slack', thread_key, content_hash):
        return None  # Already analyzed, unchanged

    # Call Claude
    prompt = EXTRACTION_PROMPT.format(
        channel_name=channel_name,
        date=thread.get('date', 'unknown'),
        thread_text=thread_text
    )

    response = claude_client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=2000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    extraction = json.loads(response.content[0].text)

    # Wrap in ThreadExtraction envelope
    result = {
        'extraction_id': f"ext-{thread_key.replace(':', '-')}",
        'extracted_at': datetime.now().isoformat(),
        'source': {
            'channel_id': thread['channel_id'],
            'channel_name': channel_name,
            'thread_ts': thread['thread_ts'],
            'date': thread.get('date'),
            'participants': list(set(m.get('user_name', '') for m in [thread['parent']] + thread['replies'])),
            'message_count': thread['message_count']
        },
        **extraction
    }

    # Save extraction
    output_path = Path(f"data/extractions/{result['extraction_id']}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    # Update index
    analysis_index.record('slack', thread_key, content_hash, result['extraction_id'])

    return result
```

**API pacing**: Wait 2 seconds between Claude API calls. Use exponential backoff on 429 (rate limit) responses: 2s, 4s, 8s, then stop and save state.

---

### Stage 3: Synthesize

The Synthesize stage merges extractions across all sources to build unified customer profiles, compute KPIs, and assign funnel stages.

#### Customer Name Normalization

Customer names appear inconsistently across threads ("Acme Inc.", "ACME", "Acme Corporation"). Normalize them to enable cross-extraction merging.

```python
COMPANY_SUFFIXES = re.compile(
    r'\s*(Inc\.?|Corp\.?|Corporation|Ltd\.?|LLC|GmbH|Co\.?|Company|Group|Holdings|PLC)\s*$',
    re.IGNORECASE
)

def normalize_customer_name(name: str) -> str:
    name = name.strip()
    name = COMPANY_SUFFIXES.sub('', name)
    name = name.strip().strip(',').strip()
    return name.title()  # "ACME" -> "Acme"
```

#### Cross-Extraction Merging

Group extractions by normalized customer key and merge their data:

```python
def synthesize_customers(extractions: list) -> dict:
    customers = {}

    for ext in extractions:
        for customer in ext.get('customers', []):
            key = normalize_customer_name(customer['name'])
            if key not in customers:
                customers[key] = {
                    'name': key,
                    'mentions': [],
                    'experiments': [],
                    'accelerators': [],
                    'gaps': [],
                    'funnel_stage': 'map-of-interest',
                    'first_seen': ext['extracted_at'],
                    'last_seen': ext['extracted_at']
                }

            profile = customers[key]
            profile['mentions'].append({
                'extraction_id': ext['extraction_id'],
                'channel': ext['source']['channel_name'],
                'date': ext['source']['date'],
                'context': customer.get('context', '')
            })
            profile['last_seen'] = max(profile['last_seen'], ext['extracted_at'])

            # Merge related experiments and gaps
            profile['experiments'].extend(ext.get('experiments', []))
            profile['accelerators'].extend(ext.get('accelerators', []))
            profile['gaps'].extend(ext.get('gaps', []))

    return customers
```

#### KPI Computation

```python
def compute_kpis(extractions, customers):
    return {
        'total_extractions': len(extractions),
        'total_customers': len(customers),
        'total_experiments': sum(len(e.get('experiments', [])) for e in extractions),
        'total_accelerators': sum(len(e.get('accelerators', [])) for e in extractions),
        'total_micro_learnings': sum(len(e.get('micro_learnings', [])) for e in extractions),
        'total_gaps': sum(len(e.get('gaps', [])) for e in extractions),
        'channels_covered': len(set(e['source']['channel_name'] for e in extractions)),
        'date_range': {
            'earliest': min(e['extracted_at'] for e in extractions),
            'latest': max(e['extracted_at'] for e in extractions)
        }
    }
```

#### Funnel Stage Assignment

Map each customer to a funnel stage based on their engagement signals:

```python
FUNNEL_STAGES = [
    'map-of-interest',   # Mentioned, no active engagement
    'prototype',         # Active experiment or proof-of-concept
    'co-innovation',     # Joint development, deep collaboration
    'productized',       # Shipped to production, ongoing relationship
    'dropped'            # Explicitly disengaged or lost
]

def assign_funnel_stage(customer_profile):
    experiments = customer_profile.get('experiments', [])
    accelerators = customer_profile.get('accelerators', [])
    mentions = customer_profile.get('mentions', [])

    if any(e.get('status') == 'production' for e in experiments):
        return 'productized'
    if any(e.get('status') == 'active' for e in experiments) and len(accelerators) >= 2:
        return 'co-innovation'
    if any(e.get('status') in ('active', 'planned') for e in experiments):
        return 'prototype'
    if any(e.get('status') == 'dropped' for e in experiments):
        return 'dropped'
    return 'map-of-interest'
```

---

### Stage 4: Dashboard Generation

Generate a single-page HTML dashboard with embedded CSS and JavaScript. No external dependencies.

Key dashboard sections:
1. **KPI Cards** — Total customers, experiments, accelerators, gaps, micro-learnings
2. **Funnel Visualization** — Horizontal funnel showing customer counts per stage
3. **Customer Table** — Sortable table with name, stage, experiment count, last activity date
4. **Channel Breakdown** — Bar chart showing extraction counts per Slack channel
5. **Timeline** — Monthly activity chart showing extraction volume over time
6. **Gap Analysis** — Severity-colored list of identified gaps
7. **Micro-Learnings Feed** — Scrollable list of extracted insights

Follow the report-hub-generator design system for consistent theming. See that skill for CSS variables and component patterns.

---

### Stage 5: CLI Interface

Expose each stage as a CLI command for incremental execution:

```
pipeline auth-test              # Verify Slack token and scopes
pipeline fetch [--channels X,Y] # Fetch new data from Slack
pipeline analyze [--force]      # Run Claude extraction on new/changed threads
pipeline synthesize             # Merge extractions into customer profiles + KPIs
pipeline dashboard              # Generate HTML dashboard
pipeline deploy [--target URL]  # Deploy dashboard (optional)
pipeline ingest <dir> <name>    # Ingest documents from a local directory
pipeline readout [--period 30d] # Generate a time-bounded readout report
pipeline status                 # Show pipeline health: counts, last run, errors
```

The `status` command should output a table showing each stage's state:

```
Stage       | Last Run            | Items   | Status
------------|---------------------|---------|--------
Fetch       | 2025-12-01 14:30   | 847 msg | OK
Analyze     | 2025-12-01 15:10   | 203 ext | OK (12 skipped)
Synthesize  | 2025-12-01 15:15   | 47 cust | OK
Dashboard   | 2025-12-01 15:16   | 1 file  | OK
```

---

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Slack auth fails | Token expired or wrong scopes | Re-generate bot token with `channels:history`, `channels:read`, `users:read` scopes |
| All threads skipped during analyze | Analysis index shows all hashes unchanged | Use `--force` flag to clear the index and reprocess everything |
| Customer names not merging | Name normalization missing edge cases | Add domain-specific aliases to the normalizer (e.g., "IBM" = "International Business Machines") |
| Claude returns malformed JSON | Thread text too long or ambiguous | Reduce MAX_WORDS, add JSON schema validation with retry on parse failure |
| Dashboard missing recent data | Synthesize stage not re-run after new analysis | Always run synthesize after analyze; add to a pipeline `all` command |
| Rate limiting during analyze | API calls too fast | Increase `api_delay` from 2.0 to 3.0 seconds; check your API tier limits |
| Ingested documents not appearing | File extension not in the supported list | Add the extension to the `ingest_directory` function's suffix check |

### Cross-References

- **incremental-processor** — Core pattern used for hash-based caching and state management in this pipeline
- **report-hub-generator** — Design system and component library used for dashboard generation
- **content-graph** — Applies similar graph analysis techniques to map relationships between extracted entities
