# How To: Compression Ratio

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Full pipeline produces correct metrics even without PolarQuant.

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

### Step 1: 'Full pipeline produces correct metrics even without PolarQuant.'

```python
'Full pipeline produces correct metrics even without PolarQuant.'
```

**Verification:**
```python
assert isinstance(result, CCQPipelineResult)
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert result.clusters_processed >= 1
```

### Step 3: Assign fact_ids = _seed_warm_cluster(...)

```python
fact_ids = _seed_warm_cluster(db, profile_id, count=5, shared_entities=['Python', 'FastAPI'])
```

**Verification:**
```python
assert result.blocks_created >= 1
```

### Step 4: Assign config = CCQConfig(...)

```python
config = CCQConfig(use_llm_gist=False, min_cluster_size=3)
```

**Verification:**
```python
assert result.total_bytes_before > 0
```

### Step 5: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=config)
```

**Verification:**
```python
assert result.total_bytes_before >= result.total_bytes_after
```

### Step 6: Assign result = cons.run_pipeline(...)

```python
result = cons.run_pipeline(profile_id)
```

**Verification:**
```python
assert isinstance(result, CCQPipelineResult)
```

### Step 7: Call db.execute()

```python
db.execute("INSERT INTO embedding_metadata (vec_rowid, fact_id, profile_id, model_name, dimension) VALUES (?, ?, ?, 'nomic', 768)", (i + 100, fid, profile_id))
```


## Complete Example

```python
# Setup
# Fixtures: db, profile_id

# Workflow
'Full pipeline produces correct metrics even without PolarQuant.'
_seed_profile(db, profile_id)
fact_ids = _seed_warm_cluster(db, profile_id, count=5, shared_entities=['Python', 'FastAPI'])
for i, fid in enumerate(fact_ids):
    db.execute("INSERT INTO embedding_metadata (vec_rowid, fact_id, profile_id, model_name, dimension) VALUES (?, ?, ?, 'nomic', 768)", (i + 100, fid, profile_id))
config = CCQConfig(use_llm_gist=False, min_cluster_size=3)
cons = CognitiveConsolidator(db=db, config=config)
result = cons.run_pipeline(profile_id)
assert isinstance(result, CCQPipelineResult)
assert result.clusters_processed >= 1
assert result.blocks_created >= 1
assert result.total_bytes_before > 0
assert result.total_bytes_before >= result.total_bytes_after
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:546 | Complexity: Intermediate | Last updated: 2026-05-05*