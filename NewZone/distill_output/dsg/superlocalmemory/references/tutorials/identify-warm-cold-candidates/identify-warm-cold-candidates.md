# How To: Identify Warm Cold Candidates

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Step 1 returns only warm/cold facts below retention threshold.

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

### Step 1: 'Step 1 returns only warm/cold facts below retention threshold.'

```python
'Step 1 returns only warm/cold facts below retention threshold.'
```

**Verification:**
```python
assert len(candidates) == 6
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert set(warm_ids + cold_ids) == candidate_ids
```

### Step 3: Assign warm_ids = value

```python
warm_ids = []
```

### Step 4: Assign cold_ids = value

```python
cold_ids = []
```

### Step 5: Assign candidates = consolidator._step1_identify(...)

```python
candidates = consolidator._step1_identify(profile_id)
```

### Step 6: Assign candidate_ids = value

```python
candidate_ids = {c['fact_id'] for c in candidates}
```

**Verification:**
```python
assert len(candidates) == 6
```

### Step 7: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'warm-{i}', entities=['A', 'B'])
```

### Step 8: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```

### Step 9: Call warm_ids.append()

```python
warm_ids.append(fid)
```

### Step 10: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'cold-{i}', entities=['A', 'B'])
```

### Step 11: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.1, lifecycle_zone='cold')
```

### Step 12: Call cold_ids.append()

```python
cold_ids.append(fid)
```

### Step 13: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'active-{i}', entities=['X', 'Y'])
```

### Step 14: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.9, lifecycle_zone='active')
```


## Complete Example

```python
# Setup
# Fixtures: db, consolidator, profile_id

# Workflow
'Step 1 returns only warm/cold facts below retention threshold.'
_seed_profile(db, profile_id)
warm_ids = []
for i in range(3):
    fid = _seed_fact(db, profile_id, content=f'warm-{i}', entities=['A', 'B'])
    _seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
    warm_ids.append(fid)
cold_ids = []
for i in range(3):
    fid = _seed_fact(db, profile_id, content=f'cold-{i}', entities=['A', 'B'])
    _seed_retention(db, fid, profile_id, retention_score=0.1, lifecycle_zone='cold')
    cold_ids.append(fid)
for i in range(4):
    fid = _seed_fact(db, profile_id, content=f'active-{i}', entities=['X', 'Y'])
    _seed_retention(db, fid, profile_id, retention_score=0.9, lifecycle_zone='active')
candidates = consolidator._step1_identify(profile_id)
candidate_ids = {c['fact_id'] for c in candidates}
assert len(candidates) == 6
assert set(warm_ids + cold_ids) == candidate_ids
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:172 | Complexity: Advanced | Last updated: 2026-05-05*