# How To: Worker Run Executes Pipeline

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Worker.run() delegates to consolidator and increments run_count.

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

### Step 1: 'Worker.run() delegates to consolidator and increments run_count.'

```python
'Worker.run() delegates to consolidator and increments run_count.'
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
assert result.blocks_created >= 1
```

### Step 3: Call _seed_warm_cluster()

```python
_seed_warm_cluster(db, profile_id, count=3)
```

**Verification:**
```python
assert stats['total_runs'] == 1
```

### Step 4: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=ccq_config)
```

**Verification:**
```python
assert stats['enabled'] is True
```

### Step 5: Assign worker = CCQWorker(...)

```python
worker = CCQWorker(consolidator=cons, config=ccq_config)
```

### Step 6: Assign result = worker.run(...)

```python
result = worker.run(profile_id)
```

**Verification:**
```python
assert isinstance(result, CCQPipelineResult)
```

### Step 7: Assign stats = worker.get_stats(...)

```python
stats = worker.get_stats()
```

**Verification:**
```python
assert stats['total_runs'] == 1
```


## Complete Example

```python
# Setup
# Fixtures: db, ccq_config, profile_id

# Workflow
'Worker.run() delegates to consolidator and increments run_count.'
_seed_profile(db, profile_id)
_seed_warm_cluster(db, profile_id, count=3)
cons = CognitiveConsolidator(db=db, config=ccq_config)
worker = CCQWorker(consolidator=cons, config=ccq_config)
result = worker.run(profile_id)
assert isinstance(result, CCQPipelineResult)
assert result.blocks_created >= 1
stats = worker.get_stats()
assert stats['total_runs'] == 1
assert stats['enabled'] is True
```

## Next Steps


---

*Source: test_consolidation_quantization_worker.py:237 | Complexity: Intermediate | Last updated: 2026-05-05*