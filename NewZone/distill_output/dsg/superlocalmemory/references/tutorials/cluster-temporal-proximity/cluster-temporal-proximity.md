# How To: Cluster Temporal Proximity

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Facts separated by >7 days form separate temporal sub-clusters.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `unittest.mock`
- `superlocalmemory.encoding.cognitive_consolidator`
- `unittest.mock`
- `builtins`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.core.config`
- `unittest.mock`

**Setup Required:**
```python
# Fixtures: db, consolidator, profile_id
```

## Step-by-Step Guide

### Step 1: 'Facts separated by >7 days form separate temporal sub-clusters.'

```python
'Facts separated by >7 days form separate temporal sub-clusters.'
```

**Verification:**
```python
assert len(clusters) == 2
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert set(jan_ids) in cluster_fact_sets
```

### Step 3: Assign jan_ids = value

```python
jan_ids = []
```

**Verification:**
```python
assert set(mar_ids) in cluster_fact_sets
```

### Step 4: Assign mar_ids = value

```python
mar_ids = []
```

### Step 5: Assign candidates = consolidator._step1_identify(...)

```python
candidates = consolidator._step1_identify(profile_id)
```

### Step 6: Assign clusters = consolidator._step2_cluster(...)

```python
clusters = consolidator._step2_cluster(candidates, profile_id)
```

**Verification:**
```python
assert len(clusters) == 2
```

### Step 7: Assign cluster_fact_sets = value

```python
cluster_fact_sets = [set(c.fact_ids) for c in clusters]
```

**Verification:**
```python
assert set(jan_ids) in cluster_fact_sets
```

### Step 8: Assign dt = value

```python
dt = datetime(2026, 1, 10, 12, 0) + timedelta(hours=i)
```

### Step 9: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'jan-{i}', entities=['x', 'y'], observation_date=dt.isoformat())
```

### Step 10: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```

### Step 11: Call jan_ids.append()

```python
jan_ids.append(fid)
```

### Step 12: Assign dt = value

```python
dt = datetime(2026, 3, 10, 12, 0) + timedelta(hours=i)
```

### Step 13: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'mar-{i}', entities=['x', 'y'], observation_date=dt.isoformat())
```

### Step 14: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```

### Step 15: Call mar_ids.append()

```python
mar_ids.append(fid)
```


## Complete Example

```python
# Setup
# Fixtures: db, consolidator, profile_id

# Workflow
'Facts separated by >7 days form separate temporal sub-clusters.'
_seed_profile(db, profile_id)
jan_ids = []
for i in range(3):
    dt = datetime(2026, 1, 10, 12, 0) + timedelta(hours=i)
    fid = _seed_fact(db, profile_id, content=f'jan-{i}', entities=['x', 'y'], observation_date=dt.isoformat())
    _seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
    jan_ids.append(fid)
mar_ids = []
for i in range(3):
    dt = datetime(2026, 3, 10, 12, 0) + timedelta(hours=i)
    fid = _seed_fact(db, profile_id, content=f'mar-{i}', entities=['x', 'y'], observation_date=dt.isoformat())
    _seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
    mar_ids.append(fid)
candidates = consolidator._step1_identify(profile_id)
clusters = consolidator._step2_cluster(candidates, profile_id)
assert len(clusters) == 2
cluster_fact_sets = [set(c.fact_ids) for c in clusters]
assert set(jan_ids) in cluster_fact_sets
assert set(mar_ids) in cluster_fact_sets
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:279 | Complexity: Advanced | Last updated: 2026-05-05*