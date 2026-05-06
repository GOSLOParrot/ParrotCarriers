# How To: Skip Already Consolidated

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Facts already in ccq_consolidated_blocks are excluded.

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

### Step 1: 'Facts already in ccq_consolidated_blocks are excluded.'

```python
'Facts already in ccq_consolidated_blocks are excluded.'
```

**Verification:**
```python
assert len(candidates) == 2
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert candidate_ids == set(fact_ids[3:])
```

### Step 3: Assign fact_ids = value

```python
fact_ids = []
```

### Step 4: Call db.store_ccq_block()

```python
db.store_ccq_block(block_id=_new_id(), profile_id=profile_id, content='Gist of first 3 facts', source_fact_ids=json.dumps(fact_ids[:3]), gist_embedding_rowid=None, char_count=21, cluster_id=_new_id())
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
assert len(candidates) == 2
```

### Step 7: Assign fid = _seed_fact(...)

```python
fid = _seed_fact(db, profile_id, content=f'fact-{i}', entities=['A', 'B'])
```

### Step 8: Call _seed_retention()

```python
_seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
```

### Step 9: Call fact_ids.append()

```python
fact_ids.append(fid)
```


## Complete Example

```python
# Setup
# Fixtures: db, consolidator, profile_id

# Workflow
'Facts already in ccq_consolidated_blocks are excluded.'
_seed_profile(db, profile_id)
fact_ids = []
for i in range(5):
    fid = _seed_fact(db, profile_id, content=f'fact-{i}', entities=['A', 'B'])
    _seed_retention(db, fid, profile_id, retention_score=0.3, lifecycle_zone='warm')
    fact_ids.append(fid)
db.store_ccq_block(block_id=_new_id(), profile_id=profile_id, content='Gist of first 3 facts', source_fact_ids=json.dumps(fact_ids[:3]), gist_embedding_rowid=None, char_count=21, cluster_id=_new_id())
candidates = consolidator._step1_identify(profile_id)
candidate_ids = {c['fact_id'] for c in candidates}
assert len(candidates) == 2
assert candidate_ids == set(fact_ids[3:])
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:207 | Complexity: Advanced | Last updated: 2026-05-05*