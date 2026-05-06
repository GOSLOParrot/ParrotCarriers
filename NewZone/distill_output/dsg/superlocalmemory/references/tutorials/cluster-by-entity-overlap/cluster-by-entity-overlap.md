# How To: Cluster By Entity Overlap

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Union-Find groups facts by shared entities (min_overlap=2).

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

### Step 1: 'Union-Find groups facts by shared entities (min_overlap=2).'

```python
'Union-Find groups facts by shared entities (min_overlap=2).'
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
assert set(group1) in cluster_fact_sets
```

### Step 3: Assign group1 = value

```python
group1 = []
```

**Verification:**
```python
assert set(group2) in cluster_fact_sets
```

### Step 4: Assign group2 = value

```python
group2 = []
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
assert set(group1) in cluster_fact_sets
```

### Step 8: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'g1-{i}', entities=['x', 'y'], observation_date='2026-01-15T12:00:00')
```

### Step 9: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```

### Step 10: Call group1.append()

```python
group1.append(fid)
```

### Step 11: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'g2-{i}', entities=['z', 'w'], observation_date='2026-01-15T12:00:00')
```

### Step 12: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```

### Step 13: Call group2.append()

```python
group2.append(fid)
```


## Complete Example

```python
# Setup
# Fixtures: db, consolidator, profile_id

# Workflow
'Union-Find groups facts by shared entities (min_overlap=2).'
_seed_profile(db, profile_id)
group1 = []
for i in range(3):
    fid = _seed_fact(db, profile_id, content=f'g1-{i}', entities=['x', 'y'], observation_date='2026-01-15T12:00:00')
    _seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
    group1.append(fid)
group2 = []
for i in range(3):
    fid = _seed_fact(db, profile_id, content=f'g2-{i}', entities=['z', 'w'], observation_date='2026-01-15T12:00:00')
    _seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
    group2.append(fid)
candidates = consolidator._step1_identify(profile_id)
clusters = consolidator._step2_cluster(candidates, profile_id)
assert len(clusters) == 2
cluster_fact_sets = [set(c.fact_ids) for c in clusters]
assert set(group1) in cluster_fact_sets
assert set(group2) in cluster_fact_sets
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:241 | Complexity: Advanced | Last updated: 2026-05-05*