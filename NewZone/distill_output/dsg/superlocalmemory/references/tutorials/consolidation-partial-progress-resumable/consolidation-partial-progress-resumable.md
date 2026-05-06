# How To: Consolidation Partial Progress Resumable

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: apply_merges is transactional — partial failure leaves DB consistent.

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

### Step 1: 'apply_merges is transactional — partial failure leaves DB consistent.'

```python
'apply_merges is transactional — partial failure leaves DB consistent.'
```

**Verification:**
```python
assert candidates
```

### Step 2: Call _seed_known_duplicates()

```python
_seed_known_duplicates(memory_db, n_unique=5, n_dup_pairs=4)
```

**Verification:**
```python
assert applied_first == 2
```

### Step 3: Assign dedup = HnswDeduplicator(...)

```python
dedup = HnswDeduplicator(memory_db_path=memory_db)
```

**Verification:**
```python
assert merged_so_far == 2
```

### Step 4: Assign candidates = dedup.find_merge_candidates(...)

```python
candidates = dedup.find_merge_candidates('p1')
```

**Verification:**
```python
assert total == 13
```

### Step 5: Assign first = value

```python
first = candidates[:2]
```

### Step 6: Assign applied_first = apply_merges(...)

```python
applied_first = apply_merges(memory_db, first, profile_id='p1')
```

**Verification:**
```python
assert applied_first == 2
```

### Step 7: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

### Step 8: Assign merged_so_far = value

```python
merged_so_far = conn.execute("SELECT COUNT(*) FROM atomic_facts WHERE archive_status='merged'").fetchone()[0]
```

### Step 9: Assign total = value

```python
total = conn.execute('SELECT COUNT(*) FROM atomic_facts').fetchone()[0]
```

### Step 10: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert merged_so_far == 2
```

### Step 11: Assign remaining = value

```python
remaining = [c for c in candidates if c[1] not in {x[1] for x in first}]
```

### Step 12: Call apply_merges()

```python
apply_merges(memory_db, remaining, profile_id='p1')
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
'apply_merges is transactional — partial failure leaves DB consistent.'
from superlocalmemory.learning.hnsw_dedup import HnswDeduplicator
from superlocalmemory.learning.memory_merge import apply_merges
_seed_known_duplicates(memory_db, n_unique=5, n_dup_pairs=4)
dedup = HnswDeduplicator(memory_db_path=memory_db)
candidates = dedup.find_merge_candidates('p1')
assert candidates
first = candidates[:2]
applied_first = apply_merges(memory_db, first, profile_id='p1')
assert applied_first == 2
conn = sqlite3.connect(memory_db)
merged_so_far = conn.execute("SELECT COUNT(*) FROM atomic_facts WHERE archive_status='merged'").fetchone()[0]
total = conn.execute('SELECT COUNT(*) FROM atomic_facts').fetchone()[0]
conn.close()
assert merged_so_far == 2
assert total == 13
remaining = [c for c in candidates if c[1] not in {x[1] for x in first}]
apply_merges(memory_db, remaining, profile_id='p1')
```

## Next Steps


---

*Source: test_hnsw_dedup.py:534 | Complexity: Advanced | Last updated: 2026-05-05*