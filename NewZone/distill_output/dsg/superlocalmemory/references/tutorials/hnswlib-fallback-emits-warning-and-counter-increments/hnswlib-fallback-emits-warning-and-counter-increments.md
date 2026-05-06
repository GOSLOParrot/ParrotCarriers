# How To: Hnswlib Fallback Emits Warning And Counter Increments

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Stage-8 H-17: fallback to prefix path must be OBSERVABLE.

Old code used ``logger.debug`` — silent in production. New code
uses ``logger.warning`` AND increments a module-level counter that
operators can surface on the dashboard.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `importlib`
- `json`
- `logging`
- `sqlite3`
- `sys`
- `warnings`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.consolidation_cycle`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.dedup_hnsw`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning.ranker_retrain_legacy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path, caplog
```

## Step-by-Step Guide

### Step 1: 'Stage-8 H-17: fallback to prefix path must be OBSERVABLE.\n\n    Old code used ``logger.debug`` — silent in production. New code\n    uses ``logger.warning`` AND increments a module-level counter that\n    operators can surface on the dashboard.\n    '

```python
'Stage-8 H-17: fallback to prefix path must be OBSERVABLE.\n\n    Old code used ``logger.debug`` — silent in production. New code\n    uses ``logger.warning`` AND increments a module-level counter that\n    operators can surface on the dashboard.\n    '
```

**Verification:**
```python
assert before == 0
```

### Step 2: Assign db = value

```python
db = tmp_path / 'memory.db'
```

**Verification:**
```python
assert after == before + 1, f'degradation counter must increment: {before} -> {after}'
```

### Step 3: Call mod.reset_hnsw_degraded_count()

```python
mod.reset_hnsw_degraded_count()
```

**Verification:**
```python
assert any(('degraded' in rec.message.lower() and rec.levelno == logging.WARNING for rec in caplog.records)), f'expected a WARNING-level degradation log; got {[(r.levelname, r.message) for r in caplog.records]}'
```

### Step 4: Assign before = mod.get_hnsw_degraded_count(...)

```python
before = mod.get_hnsw_degraded_count()
```

**Verification:**
```python
assert before == 0
```

### Step 5: Assign after = mod.get_hnsw_degraded_count(...)

```python
after = mod.get_hnsw_degraded_count()
```

**Verification:**
```python
assert after == before + 1, f'degradation counter must increment: {before} -> {after}'
```

### Step 6: Call conn.executescript()

```python
conn.executescript("\n            CREATE TABLE atomic_facts (\n                fact_id TEXT PRIMARY KEY, profile_id TEXT,\n                content TEXT, canonical_entities_json TEXT,\n                embedding TEXT, importance REAL DEFAULT 0.5,\n                confidence REAL DEFAULT 1.0,\n                created_at TEXT DEFAULT (datetime('now')),\n                archive_status TEXT DEFAULT 'live'\n            );\n            INSERT INTO atomic_facts (fact_id, profile_id, content,\n                canonical_entities_json, embedding)\n            VALUES ('a', 'p1', 'aaa', '[]', '[1,0,0]'),\n                   ('b', 'p1', 'bbb', '[]', '[0,1,0]');\n            ")
```

### Step 7: Assign dedup = mod.HnswDeduplicator(...)

```python
dedup = mod.HnswDeduplicator(memory_db_path=db)
```

### Step 8: Call dedup.find_merge_candidates()

```python
dedup.find_merge_candidates('p1', _force_unavailable=True)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, caplog

# Workflow
'Stage-8 H-17: fallback to prefix path must be OBSERVABLE.\n\n    Old code used ``logger.debug`` — silent in production. New code\n    uses ``logger.warning`` AND increments a module-level counter that\n    operators can surface on the dashboard.\n    '
from superlocalmemory.learning import dedup_hnsw as mod
db = tmp_path / 'memory.db'
with sqlite3.connect(db) as conn:
    conn.executescript("\n            CREATE TABLE atomic_facts (\n                fact_id TEXT PRIMARY KEY, profile_id TEXT,\n                content TEXT, canonical_entities_json TEXT,\n                embedding TEXT, importance REAL DEFAULT 0.5,\n                confidence REAL DEFAULT 1.0,\n                created_at TEXT DEFAULT (datetime('now')),\n                archive_status TEXT DEFAULT 'live'\n            );\n            INSERT INTO atomic_facts (fact_id, profile_id, content,\n                canonical_entities_json, embedding)\n            VALUES ('a', 'p1', 'aaa', '[]', '[1,0,0]'),\n                   ('b', 'p1', 'bbb', '[]', '[0,1,0]');\n            ")
mod.reset_hnsw_degraded_count()
before = mod.get_hnsw_degraded_count()
assert before == 0
with caplog.at_level(logging.WARNING, logger=mod.__name__):
    dedup = mod.HnswDeduplicator(memory_db_path=db)
    dedup.find_merge_candidates('p1', _force_unavailable=True)
after = mod.get_hnsw_degraded_count()
assert after == before + 1, f'degradation counter must increment: {before} -> {after}'
assert any(('degraded' in rec.message.lower() and rec.levelno == logging.WARNING for rec in caplog.records)), f'expected a WARNING-level degradation log; got {[(r.levelname, r.message) for r in caplog.records]}'
```

## Next Steps


---

*Source: test_f4a_refactor.py:225 | Complexity: Advanced | Last updated: 2026-05-05*