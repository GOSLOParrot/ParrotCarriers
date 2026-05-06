# How To: Minimum Cluster Size

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Clusters below min_cluster_size are discarded.

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
# Fixtures: db, profile_id
```

## Step-by-Step Guide

### Step 1: 'Clusters below min_cluster_size are discarded.'

```python
'Clusters below min_cluster_size are discarded.'
```

**Verification:**
```python
assert len(clusters) == 1
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert clusters[0].fact_count == 3
```

### Step 3: Assign config = CCQConfig(...)

```python
config = CCQConfig(use_llm_gist=False, min_cluster_size=3)
```

### Step 4: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=config)
```

### Step 5: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content='isolated', entities=['z', 'w'], observation_date='2026-01-15T12:00:00')
```

### Step 6: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```

### Step 7: Assign candidates = cons._step1_identify(...)

```python
candidates = cons._step1_identify(profile_id)
```

### Step 8: Assign clusters = cons._step2_cluster(...)

```python
clusters = cons._step2_cluster(candidates, profile_id)
```

**Verification:**
```python
assert len(clusters) == 1
```

### Step 9: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'good-{i}', entities=['x', 'y'], observation_date='2026-01-15T12:00:00')
```

### Step 10: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```


## Complete Example

```python
# Setup
# Fixtures: db, profile_id

# Workflow
'Clusters below min_cluster_size are discarded.'
_seed_profile(db, profile_id)
config = CCQConfig(use_llm_gist=False, min_cluster_size=3)
cons = CognitiveConsolidator(db=db, config=config)
for i in range(3):
    fid = _seed_fact(db, profile_id, content=f'good-{i}', entities=['x', 'y'], observation_date='2026-01-15T12:00:00')
    _seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
fid = _seed_fact(db, profile_id, content='isolated', entities=['z', 'w'], observation_date='2026-01-15T12:00:00')
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
candidates = cons._step1_identify(profile_id)
clusters = cons._step2_cluster(candidates, profile_id)
assert len(clusters) == 1
assert clusters[0].fact_count == 3
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:319 | Complexity: Advanced | Last updated: 2026-05-05*