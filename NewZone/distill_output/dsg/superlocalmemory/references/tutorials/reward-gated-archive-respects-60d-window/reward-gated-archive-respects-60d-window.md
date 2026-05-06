# How To: Reward Gated Archive Respects 60D Window

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Fact with recent positive reward (<60d) MUST NOT be archived.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `sqlite3`
- `sys`
- `uuid`
- `pathlib`
- `unittest.mock`
- `pytest`
- `resource`
- `hnswlib`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning`
- `contextlib`
- `superlocalmemory.learning`
- `contextlib`
- `superlocalmemory.learning`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.memory_merge`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.memory_merge`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.memory_merge`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.hnsw_dedup`
- `superlocalmemory.learning.memory_merge`
- `superlocalmemory.learning.hnsw_dedup`
- `hnswlib`

**Setup Required:**
```python
# Fixtures: memory_db, tmp_path
```

## Step-by-Step Guide

### Step 1: 'Fact with recent positive reward (<60d) MUST NOT be archived.'

```python
'Fact with recent positive reward (<60d) MUST NOT be archived.'
```

**Verification:**
```python
assert 'f1' not in archived, 'recent-rewarded fact must not be archived'
```

### Step 2: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

**Verification:**
```python
assert 'f2' in archived, 'unrewarded candidate must be archived'
```

### Step 3: Call _seed_fact()

```python
_seed_fact(conn, 'f1', 'p1', 'rewarded', ['e1'], [1.0, 0.0, 0.0])
```

**Verification:**
```python
assert cnt == 2
```

### Step 4: Call _seed_fact()

```python
_seed_fact(conn, 'f2', 'p1', 'cold', ['e2'], [0.0, 1.0, 0.0])
```

### Step 5: Call conn.execute()

```python
conn.execute("INSERT INTO action_outcomes (outcome_id, profile_id, fact_ids_json, reward, settled, settled_at) VALUES (?, ?, ?, ?, ?, datetime('now'))", ('o1', 'p1', json.dumps(['f1']), 0.9, 1))
```

### Step 6: Call conn.commit()

```python
conn.commit()
```

### Step 7: Call conn.close()

```python
conn.close()
```

### Step 8: Assign archived = run_reward_gated_archive(...)

```python
archived = run_reward_gated_archive(memory_db, 'p1', candidate_fact_ids=['f1', 'f2'])
```

**Verification:**
```python
assert 'f1' not in archived, 'recent-rewarded fact must not be archived'
```

### Step 9: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

### Step 10: Assign cnt = value

```python
cnt = conn.execute("SELECT COUNT(*) FROM atomic_facts WHERE fact_id IN ('f1','f2')").fetchone()[0]
```

### Step 11: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert cnt == 2
```


## Complete Example

```python
# Setup
# Fixtures: memory_db, tmp_path

# Workflow
'Fact with recent positive reward (<60d) MUST NOT be archived.'
from superlocalmemory.learning.hnsw_dedup import run_reward_gated_archive
conn = sqlite3.connect(memory_db)
_seed_fact(conn, 'f1', 'p1', 'rewarded', ['e1'], [1.0, 0.0, 0.0])
_seed_fact(conn, 'f2', 'p1', 'cold', ['e2'], [0.0, 1.0, 0.0])
conn.execute("INSERT INTO action_outcomes (outcome_id, profile_id, fact_ids_json, reward, settled, settled_at) VALUES (?, ?, ?, ?, ?, datetime('now'))", ('o1', 'p1', json.dumps(['f1']), 0.9, 1))
conn.commit()
conn.close()
archived = run_reward_gated_archive(memory_db, 'p1', candidate_fact_ids=['f1', 'f2'])
assert 'f1' not in archived, 'recent-rewarded fact must not be archived'
assert 'f2' in archived, 'unrewarded candidate must be archived'
conn = sqlite3.connect(memory_db)
cnt = conn.execute("SELECT COUNT(*) FROM atomic_facts WHERE fact_id IN ('f1','f2')").fetchone()[0]
conn.close()
assert cnt == 2
```

## Next Steps


---

*Source: test_hnsw_dedup.py:414 | Complexity: Advanced | Last updated: 2026-05-05*