# How To: Merge Reversible Via Unmerge Cli

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test merge reversible via unmerge cli

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
# Fixtures: memory_db
```

## Step-by-Step Guide

### Step 1: Call _seed_known_duplicates()

```python
_seed_known_duplicates(memory_db, n_unique=5, n_dup_pairs=2)
```

**Verification:**
```python
assert merge_rows, 'no merges recorded to unmerge'
```

### Step 2: Assign dedup = HnswDeduplicator(...)

```python
dedup = HnswDeduplicator(memory_db_path=memory_db)
```

**Verification:**
```python
assert ok is True
```

### Step 3: Assign candidates = dedup.find_merge_candidates(...)

```python
candidates = dedup.find_merge_candidates('p1')
```

**Verification:**
```python
assert row is not None
```

### Step 4: Call apply_merges()

```python
apply_merges(memory_db, candidates, profile_id='p1')
```

**Verification:**
```python
assert row[0] == 'live'
```

### Step 5: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

**Verification:**
```python
assert row[1] is None
```

### Step 6: Assign merge_rows = conn.execute.fetchall(...)

```python
merge_rows = conn.execute('SELECT merge_id, merged_fact_id FROM memory_merge_log').fetchall()
```

**Verification:**
```python
assert log_row is not None
```

### Step 7: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert log_row[0] == 0
```

### Step 8: Assign unknown = value

```python
merge_id, merged_fid = merge_rows[0]
```

### Step 9: Assign ok = unmerge(...)

```python
ok = unmerge(memory_db, merge_id)
```

**Verification:**
```python
assert ok is True
```

### Step 10: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

### Step 11: Assign row = conn.execute.fetchone(...)

```python
row = conn.execute('SELECT archive_status, merged_into FROM atomic_facts WHERE fact_id=?', (merged_fid,)).fetchone()
```

### Step 12: Assign log_row = conn.execute.fetchone(...)

```python
log_row = conn.execute('SELECT reversible FROM memory_merge_log WHERE merge_id=?', (merge_id,)).fetchone()
```

### Step 13: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert row is not None
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
from superlocalmemory.learning.hnsw_dedup import HnswDeduplicator
from superlocalmemory.learning.memory_merge import apply_merges, unmerge
_seed_known_duplicates(memory_db, n_unique=5, n_dup_pairs=2)
dedup = HnswDeduplicator(memory_db_path=memory_db)
candidates = dedup.find_merge_candidates('p1')
apply_merges(memory_db, candidates, profile_id='p1')
conn = sqlite3.connect(memory_db)
merge_rows = conn.execute('SELECT merge_id, merged_fact_id FROM memory_merge_log').fetchall()
conn.close()
assert merge_rows, 'no merges recorded to unmerge'
merge_id, merged_fid = merge_rows[0]
ok = unmerge(memory_db, merge_id)
assert ok is True
conn = sqlite3.connect(memory_db)
row = conn.execute('SELECT archive_status, merged_into FROM atomic_facts WHERE fact_id=?', (merged_fid,)).fetchone()
log_row = conn.execute('SELECT reversible FROM memory_merge_log WHERE merge_id=?', (merge_id,)).fetchone()
conn.close()
assert row is not None
assert row[0] == 'live'
assert row[1] is None
assert log_row is not None
assert log_row[0] == 0
```

## Next Steps


---

*Source: test_hnsw_dedup.py:375 | Complexity: Advanced | Last updated: 2026-05-05*