---
name: incremental-processor
description: Process large datasets incrementally using hash-based change detection, state persistence, and API pacing to avoid redundant work. Use when building "incremental processing", "change detection", "batch processing", or "resumable pipelines".
---

# Incremental Processor

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| patterns | "incremental processing", "change detection", "batch processing", "resumable pipelines" | Medium | 3 projects |

Process large datasets efficiently by tracking what has been processed, detecting changes via content hashing, and skipping unchanged items. Combines a StateManager for checkpoint tracking, an AnalysisIndex for hash-based change detection, and disciplined API pacing to build pipelines that resume without losing progress or repeating work.

## When to Use
- Processing a large backlog where reprocessing everything each run is too slow or expensive
- Calling external APIs (LLMs, analytics) where each call costs money and redundant calls waste budget
- Building ETL pipelines that run on a schedule and should only process new or changed data
- Ingesting from APIs with rate limits where you need pacing and crash-safe resumption

## Instructions

### Step 1: StateManager for Checkpoints

Tracks per-source high-watermark checkpoints so you know where to resume. Uses atomic writes (write to `.tmp` then `rename`) to prevent corruption on crash.

```python
import json
from pathlib import Path
from datetime import datetime

class StateManager:
    STATE_FILE = Path('.state') / 'processor_state.json'

    def __init__(self):
        self._state = {"channels": {}, "analysis": {}}
        if self.STATE_FILE.exists():
            try:
                self._state = json.loads(self.STATE_FILE.read_text())
            except json.JSONDecodeError:
                self.STATE_FILE.rename(self.STATE_FILE.with_suffix('.corrupt'))

    def _save(self):
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.STATE_FILE.with_suffix('.tmp')
        tmp.write_text(json.dumps(self._state, indent=2, default=str))
        tmp.rename(self.STATE_FILE)

    def get_last_ts(self, channel: str) -> str | None:
        return self._state["channels"].get(channel, {}).get("last_ts")

    def set_last_ts(self, channel: str, ts: str, count: int, threads: int):
        self._state["channels"][channel] = {
            "last_ts": ts, "message_count": count,
            "thread_count": threads, "updated_at": str(datetime.now())
        }
        self._save()
```

Key rules:
- Save after every checkpoint update, not batched at the end. On crash, you resume from the last completed item.
- Handle corrupt state on load: rename the broken file and start fresh rather than crashing.

### Step 2: AnalysisIndex for Change Detection

Records a content hash per processed item. On subsequent runs, compares current hashes against recorded hashes to skip unchanged items.

```python
import hashlib

class AnalysisIndex:
    INDEX_FILE = Path('.state') / 'analysis_index.json'

    def __init__(self):
        self._index = {}
        if self.INDEX_FILE.exists():
            self._index = json.loads(self.INDEX_FILE.read_text())

    def _save(self):
        self.INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.INDEX_FILE.with_suffix('.tmp')
        tmp.write_text(json.dumps(self._index, indent=2))
        tmp.rename(self.INDEX_FILE)

    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def is_stale(self, source: str, item_id: str, current_hash: str) -> bool:
        entry = self._index.get(f"{source}:{item_id}")
        if entry is None: return True   # New item
        return entry.get("raw_hash") != current_hash  # Changed

    def record(self, source: str, item_id: str, raw_hash: str, result_id: str):
        self._index[f"{source}:{item_id}"] = {
            "raw_hash": raw_hash, "result_id": result_id,
            "processed_at": str(datetime.now())
        }
        self._save()
```

Hash design:
- SHA-256 truncated to 16 hex chars (64 bits): collision probability ~1 in 4B at 100K items.
- Hash the **raw content string**, not serialized objects. Serialization key ordering is non-deterministic.
- Strip volatile metadata (timestamps, view counts) before hashing.

### Step 3: Processing Loop with Retry and Pacing

Ties StateManager and AnalysisIndex together. For each item: compute hash, check staleness, process if needed, record result.

```python
import time

class IncrementalProcessor:
    def __init__(self, api_client, state: StateManager, index: AnalysisIndex):
        self.api = api_client
        self.state = state
        self.index = index
        self.api_delay = 2.0  # seconds between API calls

    def process_source(self, source_id: str, items: list[dict]):
        processed, skipped = 0, 0
        for item in items:
            content_hash = AnalysisIndex.compute_hash(item["content"])
            if not self.index.is_stale(source_id, item["id"], content_hash):
                skipped += 1
                continue
            try:
                result = self._call_with_retry(item["content"])
                self.index.record(source_id, item["id"], content_hash, result["id"])
                processed += 1
                time.sleep(self.api_delay)
            except ThrottlingError:
                break  # Save state, resume next run
        if items and processed > 0:
            self.state.set_last_ts(source_id, items[-1]["timestamp"], processed, skipped)
        return {"processed": processed, "skipped": skipped}

    def _call_with_retry(self, content: str, max_retries: int = 3) -> dict:
        for attempt in range(max_retries):
            try:
                return self.api.analyze(content)
            except ThrottlingError:
                if attempt == max_retries - 1: raise
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
```

Pacing rules:
- Default delay: 2.0s between calls. Conservative but safe for most APIs.
- Exponential backoff on throttling: `2^attempt` seconds. Never fixed-delay retries.
- Break on persistent throttling: save state and stop. Next run resumes from checkpoint.

### Step 4: Pipeline Runner

All state lives in `.state/` (add to `.gitignore`; mount as Docker volume for persistence). For multiple sources, namespace files: `slack_state.json`, `github_index.json`, etc.

```python
def run_pipeline(api_client, sources: list[str]):
    state = StateManager()
    index = AnalysisIndex()
    processor = IncrementalProcessor(api_client, state, index)
    for source_id in sources:
        last_ts = state.get_last_ts(source_id)
        items = api_client.fetch_items(source_id, since=last_ts)
        if not items:
            continue
        result = processor.process_source(source_id, items)
        print(f"[{source_id}] Processed: {result['processed']}, Skipped: {result['skipped']}")
```

To force reprocessing after analysis logic changes, clear the index: `index._index = {}; index._save()`. Without clearing, partial failures resolve naturally -- recorded hashes let the next run skip completed items.

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Everything reprocesses every run | Non-deterministic content hashing | Normalize before hashing: sort keys, strip whitespace, remove volatile fields |
| State file empty or `{}` | Crash during write | Use atomic writes: `.tmp` then `os.rename` |
| Rate limit despite pacing | Multiple instances running | Use a lock file in `.state/` to prevent concurrent runs |
| Index grows indefinitely | Deleted items never cleaned | Periodically prune entries whose source items no longer exist |
| Hash collisions skip items | Truncated hash too short | Increase hash from 16 to 32 hex chars for datasets over 1M items |

### Cross-References
- **data-intelligence-pipeline** -- Full pipeline architecture using incremental processing as a core pattern
- **multi-provider-fallback** -- API client abstraction used in `_call_with_retry` for provider switching
