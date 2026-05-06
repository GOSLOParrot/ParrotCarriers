# How To: Ccq Block Created

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Pipeline creates a row in ccq_consolidated_blocks with correct source_fact_ids.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.learning.consolidation_quantization_worker`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage`
- `superlocalmemory.core.config`
- `superlocalmemory.core.consolidation_engine`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db, ccq_config, profile_id
```

## Step-by-Step Guide

### Step 1: 'Pipeline creates a row in ccq_consolidated_blocks with correct source_fact_ids.'

```python
'Pipeline creates a row in ccq_consolidated_blocks with correct source_fact_ids.'
```

**Verification:**
```python
assert len(blocks) >= 1
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert set(stored_ids) == set(fact_ids)
```

### Step 3: Assign fact_ids = _seed_warm_cluster(...)

```python
fact_ids = _seed_warm_cluster(db, profile_id, count=3)
```

**Verification:**
```python
assert block['compiled_by'] == 'ccq'
```

### Step 4: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=ccq_config)
```

**Verification:**
```python
assert result.blocks_created >= 1
```

### Step 5: Assign result = cons.run_pipeline(...)

```python
result = cons.run_pipeline(profile_id)
```

### Step 6: Assign blocks = db.get_ccq_blocks(...)

```python
blocks = db.get_ccq_blocks(profile_id)
```

**Verification:**
```python
assert len(blocks) >= 1
```

### Step 7: Assign block = value

```python
block = blocks[0]
```

### Step 8: Assign stored_ids = json.loads(...)

```python
stored_ids = json.loads(block['source_fact_ids'])
```

**Verification:**
```python
assert set(stored_ids) == set(fact_ids)
```


## Complete Example

```python
# Setup
# Fixtures: db, ccq_config, profile_id

# Workflow
'Pipeline creates a row in ccq_consolidated_blocks with correct source_fact_ids.'
_seed_profile(db, profile_id)
fact_ids = _seed_warm_cluster(db, profile_id, count=3)
cons = CognitiveConsolidator(db=db, config=ccq_config)
result = cons.run_pipeline(profile_id)
blocks = db.get_ccq_blocks(profile_id)
assert len(blocks) >= 1
block = blocks[0]
stored_ids = json.loads(block['source_fact_ids'])
assert set(stored_ids) == set(fact_ids)
assert block['compiled_by'] == 'ccq'
assert result.blocks_created >= 1
```

## Next Steps


---

*Source: test_consolidation_quantization_worker.py:119 | Complexity: Advanced | Last updated: 2026-05-05*