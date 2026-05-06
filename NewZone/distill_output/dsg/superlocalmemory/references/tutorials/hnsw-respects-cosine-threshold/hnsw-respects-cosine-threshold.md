# How To: Hnsw Respects Cosine Threshold

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test hnsw respects cosine threshold

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

### Step 1: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

**Verification:**
```python
assert cos > HnswDeduplicator.COSINE_THRESHOLD, f'candidate cos={cos} should be > {HnswDeduplicator.COSINE_THRESHOLD}'
```

### Step 2: Assign v1 = value

```python
v1 = [1.0, 0.0, 0.0, 0.0]
```

### Step 3: Assign v2 = value

```python
v2 = [0.94, 0.3411, 0.0, 0.0]
```

### Step 4: Call _seed_fact()

```python
_seed_fact(conn, 'f1', 'p1', 'alpha', ['shared'], v1)
```

### Step 5: Call _seed_fact()

```python
_seed_fact(conn, 'f2', 'p1', 'beta', ['shared'], v2)
```

### Step 6: Call conn.commit()

```python
conn.commit()
```

### Step 7: Call conn.close()

```python
conn.close()
```

### Step 8: Assign dedup = HnswDeduplicator(...)

```python
dedup = HnswDeduplicator(memory_db_path=memory_db)
```

### Step 9: Assign candidates = dedup.find_merge_candidates(...)

```python
candidates = dedup.find_merge_candidates('p1')
```

**Verification:**
```python
assert cos > HnswDeduplicator.COSINE_THRESHOLD, f'candidate cos={cos} should be > {HnswDeduplicator.COSINE_THRESHOLD}'
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
from superlocalmemory.learning.hnsw_dedup import HnswDeduplicator
conn = sqlite3.connect(memory_db)
v1 = [1.0, 0.0, 0.0, 0.0]
v2 = [0.94, 0.3411, 0.0, 0.0]
_seed_fact(conn, 'f1', 'p1', 'alpha', ['shared'], v1)
_seed_fact(conn, 'f2', 'p1', 'beta', ['shared'], v2)
conn.commit()
conn.close()
dedup = HnswDeduplicator(memory_db_path=memory_db)
candidates = dedup.find_merge_candidates('p1')
for canonical, loser, cos, jac in candidates:
    assert cos > HnswDeduplicator.COSINE_THRESHOLD, f'candidate cos={cos} should be > {HnswDeduplicator.COSINE_THRESHOLD}'
```

## Next Steps


---

*Source: test_hnsw_dedup.py:208 | Complexity: Advanced | Last updated: 2026-05-05*