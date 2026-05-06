# How To: 10K Facts Under 200Mb Ram Peak

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: 10k synthetic facts → peak RAM delta must stay under 200 MB (I2 budget).

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

### Step 1: '10k synthetic facts → peak RAM delta must stay under 200 MB (I2 budget).'

```python
'10k synthetic facts → peak RAM delta must stay under 200 MB (I2 budget).'
```

**Verification:**
```python
assert delta_mb < 200.0, f'RAM delta {delta_mb:.1f} MB exceeds 200 MB budget'
```

### Step 2: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(memory_db)
```

### Step 3: Call conn.execute()

```python
conn.execute('PRAGMA synchronous=OFF')
```

### Step 4: Assign dim = 8

```python
dim = 8
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Call conn.close()

```python
conn.close()
```

### Step 7: Assign before_kb = value

```python
before_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
```

### Step 8: Assign dedup = HnswDeduplicator(...)

```python
dedup = HnswDeduplicator(memory_db_path=memory_db)
```

### Step 9: Call dedup.find_merge_candidates()

```python
dedup.find_merge_candidates('p1', wall_seconds=30.0)
```

### Step 10: Assign after_kb = value

```python
after_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
```

### Step 11: Assign delta_mb = value

```python
delta_mb = after_mb - before_mb
```

**Verification:**
```python
assert delta_mb < 200.0, f'RAM delta {delta_mb:.1f} MB exceeds 200 MB budget'
```

### Step 12: Assign vec = value

```python
vec = [0.0] * dim
```

### Step 13: Assign unknown = 1.0

```python
vec[i % dim] = 1.0
```

### Step 14: Assign unknown = 0.5

```python
vec[(i + 2) % dim] = 0.5
```

### Step 15: Call conn.execute()

```python
conn.execute("INSERT INTO atomic_facts (fact_id, profile_id, content, canonical_entities_json,  embedding, importance, confidence) VALUES (?, 'p1', ?, ?, ?, 0.5, 1.0)", (f'f{i:05d}', f'c{i}', json.dumps([f'e{i % 100}']), json.dumps(vec)))
```

### Step 16: Assign before_mb = value

```python
before_mb = before_kb / (1024 * 1024)
```

### Step 17: Assign before_mb = value

```python
before_mb = before_kb / 1024
```

### Step 18: Assign after_mb = value

```python
after_mb = after_kb / (1024 * 1024)
```

### Step 19: Assign after_mb = value

```python
after_mb = after_kb / 1024
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
'10k synthetic facts → peak RAM delta must stay under 200 MB (I2 budget).'
from superlocalmemory.learning.hnsw_dedup import HnswDeduplicator
conn = sqlite3.connect(memory_db)
conn.execute('PRAGMA synchronous=OFF')
dim = 8
for i in range(10000):
    vec = [0.0] * dim
    vec[i % dim] = 1.0
    vec[(i + 2) % dim] = 0.5
    conn.execute("INSERT INTO atomic_facts (fact_id, profile_id, content, canonical_entities_json,  embedding, importance, confidence) VALUES (?, 'p1', ?, ?, ?, 0.5, 1.0)", (f'f{i:05d}', f'c{i}', json.dumps([f'e{i % 100}']), json.dumps(vec)))
conn.commit()
conn.close()
before_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
if sys.platform == 'darwin':
    before_mb = before_kb / (1024 * 1024)
else:
    before_mb = before_kb / 1024
dedup = HnswDeduplicator(memory_db_path=memory_db)
dedup.find_merge_candidates('p1', wall_seconds=30.0)
after_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
if sys.platform == 'darwin':
    after_mb = after_kb / (1024 * 1024)
else:
    after_mb = after_kb / 1024
delta_mb = after_mb - before_mb
assert delta_mb < 200.0, f'RAM delta {delta_mb:.1f} MB exceeds 200 MB budget'
```

## Next Steps


---

*Source: test_hnsw_dedup.py:569 | Complexity: Advanced | Last updated: 2026-05-05*