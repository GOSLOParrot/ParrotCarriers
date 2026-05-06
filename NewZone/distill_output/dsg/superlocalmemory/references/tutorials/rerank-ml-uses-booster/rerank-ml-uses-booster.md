# How To: Rerank Ml Uses Booster

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test rerank ml uses booster

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pytest`
- `lightgbm`
- `numpy`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.features`
- `superlocalmemory.learning.labeler`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.ranker`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `lightgbm`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.signals`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `superlocalmemory.learning.model_cache`
- `superlocalmemory.learning.model_cache`
- `hashlib`
- `json`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign unknown = _trained_model(...)

```python
_, model = _trained_model(tmp_path)
```

**Verification:**
```python
assert len(out) == 5
```

### Step 2: Assign r = AdaptiveRanker(...)

```python
r = AdaptiveRanker(signal_count=500, active_model=model)
```

### Step 3: Assign results = value

```python
results = [{'fact_id': f'f-{i}', 'channel_scores': {'semantic': i * 0.1}, 'cross_encoder_score': 0.5, 'trust_score': 0.5, 'fact': {'age_days': 0, 'access_count': 0}} for i in range(5)]
```

### Step 4: Assign out = r.rerank(...)

```python
out = r.rerank(results, {'query_type': 'single_hop'})
```

**Verification:**
```python
assert len(out) == 5
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
_, model = _trained_model(tmp_path)
r = AdaptiveRanker(signal_count=500, active_model=model)
results = [{'fact_id': f'f-{i}', 'channel_scores': {'semantic': i * 0.1}, 'cross_encoder_score': 0.5, 'trust_score': 0.5, 'fact': {'age_days': 0, 'access_count': 0}} for i in range(5)]
out = r.rerank(results, {'query_type': 'single_hop'})
assert len(out) == 5
```

## Next Steps


---

*Source: test_ranker_v2.py:290 | Complexity: Intermediate | Last updated: 2026-05-05*