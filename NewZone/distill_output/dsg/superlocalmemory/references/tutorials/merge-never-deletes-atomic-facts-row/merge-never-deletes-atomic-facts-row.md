# How To: Merge Never Deletes Atomic Facts Row

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test merge never deletes atomic facts row

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

### Step 1: Assign unknown = _seed_known_duplicates(...)

```python
_, dup_pairs = _seed_known_duplicates(memory_db, n_unique=10, n_dup_pairs=5)
```

**Verification:**
```python
assert len(candidates) >= 5
```

### Step 2: Assign dedup = HnswDeduplicator(...)

```python
dedup = HnswDeduplicator(memory_db_path=memory_db)
```

**Verification:**
```python
assert applied >= 5
```

### Step 3: Assign candidates = dedup.find_merge_candidates(...)

```python
candidates = dedup.find_merge_candidates('p1')
```

**Verification:**
```python
assert total == 20, f'expected all 20 rows to remain; got {total}'
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

**Verification:**
```python
assert merged >= 5, f'expected >=5 rows flipped to merged; got {merged}'
```

### Step 5: Call conn.set_authorizer()

```python
conn.set_authorizer(_authorizer)
```

### Step 6: Call conn.close()

```python
conn.close()
```

### Step 7: Assign applied = apply_merges(...)

```python
applied = apply_merges(memory_db, candidates, profile_id='p1')
```

**Verification:**
```python
assert applied >= 5
```

### Step 8: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

### Step 9: Assign total = value

```python
total = conn.execute('SELECT COUNT(*) FROM atomic_facts').fetchone()[0]
```

### Step 10: Assign merged = value

```python
merged = conn.execute("SELECT COUNT(*) FROM atomic_facts WHERE archive_status='merged' AND merged_into IS NOT NULL").fetchone()[0]
```

### Step 11: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert total == 20, f'expected all 20 rows to remain; got {total}'
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
from superlocalmemory.learning.hnsw_dedup import HnswDeduplicator
from superlocalmemory.learning.memory_merge import apply_merges
_, dup_pairs = _seed_known_duplicates(memory_db, n_unique=10, n_dup_pairs=5)
dedup = HnswDeduplicator(memory_db_path=memory_db)
candidates = dedup.find_merge_candidates('p1')
assert len(candidates) >= 5
conn = sqlite3.connect(memory_db)

def _authorizer(code, arg1, arg2, arg3, arg4):
    if code == sqlite3.SQLITE_DELETE and arg1 == 'atomic_facts':
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK
conn.set_authorizer(_authorizer)
conn.close()
applied = apply_merges(memory_db, candidates, profile_id='p1')
assert applied >= 5
conn = sqlite3.connect(memory_db)
total = conn.execute('SELECT COUNT(*) FROM atomic_facts').fetchone()[0]
merged = conn.execute("SELECT COUNT(*) FROM atomic_facts WHERE archive_status='merged' AND merged_into IS NOT NULL").fetchone()[0]
conn.close()
assert total == 20, f'expected all 20 rows to remain; got {total}'
assert merged >= 5, f'expected >=5 rows flipped to merged; got {merged}'
```

## Next Steps


---

*Source: test_hnsw_dedup.py:310 | Complexity: Advanced | Last updated: 2026-05-05*