# How To: Hnsw Uses Ram Reservation

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test hnsw uses ram reservation

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
_seed_known_duplicates(memory_db, n_unique=20, n_dup_pairs=5)
```

**Verification:**
```python
assert called['n'] >= 1, 'ram_reservation must be invoked'
```

### Step 2: Assign called = value

```python
called = {'n': 0, 'name': None, 'required_mb': None}
```

**Verification:**
```python
assert called['name'] == 'hnswlib'
```

### Step 3: Assign unknown = name

```python
called['name'] = name
```

**Verification:**
```python
assert isinstance(called['required_mb'], int)
```

### Step 4: Assign unknown = required_mb

```python
called['required_mb'] = required_mb
```

**Verification:**
```python
assert called['required_mb'] > 0
```

### Step 5: yield

```python
yield
```

### Step 6: Assign dedup = mod.HnswDeduplicator(...)

```python
dedup = mod.HnswDeduplicator(memory_db_path=memory_db)
```

### Step 7: Call dedup.find_merge_candidates()

```python
dedup.find_merge_candidates('p1')
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
from superlocalmemory.learning import dedup_hnsw as mod
_seed_known_duplicates(memory_db, n_unique=20, n_dup_pairs=5)
called = {'n': 0, 'name': None, 'required_mb': None}
from contextlib import contextmanager

@contextmanager
def _spy(name: str, *, required_mb: int=0, **kw):
    called['n'] += 1
    called['name'] = name
    called['required_mb'] = required_mb
    yield
with patch.object(mod, 'ram_reservation', _spy):
    dedup = mod.HnswDeduplicator(memory_db_path=memory_db)
    dedup.find_merge_candidates('p1')
assert called['n'] >= 1, 'ram_reservation must be invoked'
assert called['name'] == 'hnswlib'
assert isinstance(called['required_mb'], int)
assert called['required_mb'] > 0
```

## Next Steps


---

*Source: test_hnsw_dedup.py:246 | Complexity: Intermediate | Last updated: 2026-05-05*