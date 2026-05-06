# How To: Source Facts Archived

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: After pipeline, source facts have lifecycle='archived' and zone='archive'.

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

### Step 1: "After pipeline, source facts have lifecycle='archived' and zone='archive'."

```python
"After pipeline, source facts have lifecycle='archived' and zone='archive'."
```

**Verification:**
```python
assert result.facts_archived == 3
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert dict(rows[0])['lifecycle'] == 'archived'
```

### Step 3: Assign fact_ids = _seed_warm_cluster(...)

```python
fact_ids = _seed_warm_cluster(db, profile_id, count=3, shared_entities=['Python', 'FastAPI'])
```

**Verification:**
```python
assert dict(rows[0])['lifecycle_zone'] == 'archive'
```

### Step 4: Assign config = CCQConfig(...)

```python
config = CCQConfig(use_llm_gist=False, min_cluster_size=3)
```

### Step 5: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=config)
```

### Step 6: Assign result = cons.run_pipeline(...)

```python
result = cons.run_pipeline(profile_id)
```

**Verification:**
```python
assert result.facts_archived == 3
```

### Step 7: Assign rows = db.execute(...)

```python
rows = db.execute('SELECT lifecycle FROM atomic_facts WHERE fact_id = ?', (fid,))
```

**Verification:**
```python
assert dict(rows[0])['lifecycle'] == 'archived'
```

### Step 8: Assign rows = db.execute(...)

```python
rows = db.execute('SELECT lifecycle_zone FROM fact_retention WHERE fact_id = ?', (fid,))
```

**Verification:**
```python
assert dict(rows[0])['lifecycle_zone'] == 'archive'
```


## Complete Example

```python
# Setup
# Fixtures: db, profile_id

# Workflow
"After pipeline, source facts have lifecycle='archived' and zone='archive'."
_seed_profile(db, profile_id)
fact_ids = _seed_warm_cluster(db, profile_id, count=3, shared_entities=['Python', 'FastAPI'])
config = CCQConfig(use_llm_gist=False, min_cluster_size=3)
cons = CognitiveConsolidator(db=db, config=config)
result = cons.run_pipeline(profile_id)
assert result.facts_archived == 3
for fid in fact_ids:
    rows = db.execute('SELECT lifecycle FROM atomic_facts WHERE fact_id = ?', (fid,))
    assert dict(rows[0])['lifecycle'] == 'archived'
for fid in fact_ids:
    rows = db.execute('SELECT lifecycle_zone FROM fact_retention WHERE fact_id = ?', (fid,))
    assert dict(rows[0])['lifecycle_zone'] == 'archive'
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:582 | Complexity: Advanced | Last updated: 2026-05-05*