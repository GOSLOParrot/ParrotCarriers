# How To: Hnsw Respects Entity Jaccard Threshold

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test hnsw respects entity jaccard threshold

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
assert candidates == [], f'expected no candidates for jac<0.8; got {candidates}'
```

### Step 2: Assign v = value

```python
v = [1.0, 0.0, 0.0, 0.0]
```

### Step 3: Call _seed_fact()

```python
_seed_fact(conn, 'f1', 'p1', 'x', ['a', 'b', 'c'], v)
```

### Step 4: Call _seed_fact()

```python
_seed_fact(conn, 'f2', 'p1', 'y', ['a', 'x', 'y'], v)
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Call conn.close()

```python
conn.close()
```

### Step 7: Assign dedup = HnswDeduplicator(...)

```python
dedup = HnswDeduplicator(memory_db_path=memory_db)
```

### Step 8: Assign candidates = dedup.find_merge_candidates(...)

```python
candidates = dedup.find_merge_candidates('p1')
```

**Verification:**
```python
assert candidates == [], f'expected no candidates for jac<0.8; got {candidates}'
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
from superlocalmemory.learning.hnsw_dedup import HnswDeduplicator
conn = sqlite3.connect(memory_db)
v = [1.0, 0.0, 0.0, 0.0]
_seed_fact(conn, 'f1', 'p1', 'x', ['a', 'b', 'c'], v)
_seed_fact(conn, 'f2', 'p1', 'y', ['a', 'x', 'y'], v)
conn.commit()
conn.close()
dedup = HnswDeduplicator(memory_db_path=memory_db)
candidates = dedup.find_merge_candidates('p1')
assert candidates == [], f'expected no candidates for jac<0.8; got {candidates}'
```

## Next Steps


---

*Source: test_hnsw_dedup.py:228 | Complexity: Advanced | Last updated: 2026-05-05*