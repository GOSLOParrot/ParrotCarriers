# How To: Compress Embeddings Disabled

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Step 4 returns (0, 0) when compress_embeddings=False.

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

### Step 1: 'Step 4 returns (0, 0) when compress_embeddings=False.'

```python
'Step 4 returns (0, 0) when compress_embeddings=False.'
```

**Verification:**
```python
assert bb == 0
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert ba == 0
```

### Step 3: Assign config = CCQConfig(...)

```python
config = CCQConfig(use_llm_gist=False, compress_embeddings=False)
```

### Step 4: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=config)
```

### Step 5: Assign fact_ids = _seed_warm_cluster(...)

```python
fact_ids = _seed_warm_cluster(db, profile_id, count=3)
```

### Step 6: Assign cluster = ConsolidationCluster(...)

```python
cluster = ConsolidationCluster(cluster_id=_new_id(), fact_ids=tuple(fact_ids), shared_entities=('Python', 'FastAPI'), temporal_centroid='2026-01-15T12:00:00', avg_retention=0.3, fact_count=3)
```

### Step 7: Assign unknown = cons._step4_compress_embeddings(...)

```python
bb, ba = cons._step4_compress_embeddings(cluster, profile_id)
```

**Verification:**
```python
assert bb == 0
```


## Complete Example

```python
# Setup
# Fixtures: db, profile_id

# Workflow
'Step 4 returns (0, 0) when compress_embeddings=False.'
_seed_profile(db, profile_id)
config = CCQConfig(use_llm_gist=False, compress_embeddings=False)
cons = CognitiveConsolidator(db=db, config=config)
fact_ids = _seed_warm_cluster(db, profile_id, count=3)
cluster = ConsolidationCluster(cluster_id=_new_id(), fact_ids=tuple(fact_ids), shared_entities=('Python', 'FastAPI'), temporal_centroid='2026-01-15T12:00:00', avg_retention=0.3, fact_count=3)
bb, ba = cons._step4_compress_embeddings(cluster, profile_id)
assert bb == 0
assert ba == 0
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:742 | Complexity: Intermediate | Last updated: 2026-05-05*