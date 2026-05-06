# How To: Ccq Integration With Consolidation

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: consolidation_engine.consolidate() includes 'ccq' in results when wired.

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
# Fixtures: db, profile_id, tmp_path
```

## Step-by-Step Guide

### Step 1: "consolidation_engine.consolidate() includes 'ccq' in results when wired."

```python
"consolidation_engine.consolidate() includes 'ccq' in results when wired."
```

**Verification:**
```python
assert 'ccq' in results
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert results['success'] is True
```

### Step 3: Call _seed_warm_cluster()

```python
_seed_warm_cluster(db, profile_id, count=3)
```

### Step 4: Assign consolidation_config = ConsolidationConfig(...)

```python
consolidation_config = ConsolidationConfig(enabled=True)
```

### Step 5: Assign slm_config = SLMConfig.for_mode(...)

```python
slm_config = SLMConfig.for_mode(Mode.A, base_dir=tmp_path)
```

### Step 6: Assign ccq_config = CCQConfig(...)

```python
ccq_config = CCQConfig(use_llm_gist=False, store_count_trigger=1)
```

### Step 7: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=ccq_config)
```

### Step 8: Assign worker = CCQWorker(...)

```python
worker = CCQWorker(consolidator=cons, config=ccq_config)
```

### Step 9: Assign engine = ConsolidationEngine(...)

```python
engine = ConsolidationEngine(db=db, config=consolidation_config, slm_config=slm_config, ccq_worker=worker)
```

### Step 10: Assign results = engine.consolidate(...)

```python
results = engine.consolidate(profile_id, lightweight=False)
```

**Verification:**
```python
assert 'ccq' in results
```


## Complete Example

```python
# Setup
# Fixtures: db, profile_id, tmp_path

# Workflow
"consolidation_engine.consolidate() includes 'ccq' in results when wired."
from superlocalmemory.core.config import ConsolidationConfig, SLMConfig
from superlocalmemory.core.consolidation_engine import ConsolidationEngine
from superlocalmemory.storage.models import Mode
_seed_profile(db, profile_id)
_seed_warm_cluster(db, profile_id, count=3)
consolidation_config = ConsolidationConfig(enabled=True)
slm_config = SLMConfig.for_mode(Mode.A, base_dir=tmp_path)
ccq_config = CCQConfig(use_llm_gist=False, store_count_trigger=1)
cons = CognitiveConsolidator(db=db, config=ccq_config)
worker = CCQWorker(consolidator=cons, config=ccq_config)
engine = ConsolidationEngine(db=db, config=consolidation_config, slm_config=slm_config, ccq_worker=worker)
results = engine.consolidate(profile_id, lightweight=False)
assert 'ccq' in results
assert results['success'] is True
```

## Next Steps


---

*Source: test_consolidation_quantization_worker.py:168 | Complexity: Advanced | Last updated: 2026-05-05*