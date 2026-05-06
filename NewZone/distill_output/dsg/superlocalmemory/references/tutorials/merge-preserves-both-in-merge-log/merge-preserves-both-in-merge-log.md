# How To: Merge Preserves Both In Merge Log

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test merge preserves both in merge log

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
_seed_known_duplicates(memory_db, n_unique=5, n_dup_pairs=3)
```

**Verification:**
```python
assert len(rows) >= 3
```

### Step 2: Assign dedup = HnswDeduplicator(...)

```python
dedup = HnswDeduplicator(memory_db_path=memory_db)
```

**Verification:**
```python
assert canonical and merged
```

### Step 3: Assign candidates = dedup.find_merge_candidates(...)

```python
candidates = dedup.find_merge_candidates('p1')
```

**Verification:**
```python
assert canonical != merged
```

### Step 4: Call apply_merges()

```python
apply_merges(memory_db, candidates, profile_id='p1')
```

**Verification:**
```python
assert 0.0 <= cos <= 1.0 + 1e-06
```

### Step 5: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

**Verification:**
```python
assert 0.0 <= jac <= 1.0 + 1e-06
```

### Step 6: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT canonical_fact_id, merged_fact_id, cosine_sim, entity_jaccard FROM memory_merge_log WHERE profile_id=?', ('p1',)).fetchall()
```

### Step 7: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert len(rows) >= 3
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
from superlocalmemory.learning.hnsw_dedup import HnswDeduplicator
from superlocalmemory.learning.memory_merge import apply_merges
_seed_known_duplicates(memory_db, n_unique=5, n_dup_pairs=3)
dedup = HnswDeduplicator(memory_db_path=memory_db)
candidates = dedup.find_merge_candidates('p1')
apply_merges(memory_db, candidates, profile_id='p1')
conn = sqlite3.connect(memory_db)
rows = conn.execute('SELECT canonical_fact_id, merged_fact_id, cosine_sim, entity_jaccard FROM memory_merge_log WHERE profile_id=?', ('p1',)).fetchall()
conn.close()
assert len(rows) >= 3
for canonical, merged, cos, jac in rows:
    assert canonical and merged
    assert canonical != merged
    assert 0.0 <= cos <= 1.0 + 1e-06
    assert 0.0 <= jac <= 1.0 + 1e-06
```

## Next Steps


---

*Source: test_hnsw_dedup.py:350 | Complexity: Intermediate | Last updated: 2026-05-05*