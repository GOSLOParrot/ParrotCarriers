# How To: Rerank Ml Unknown Drift Falls Back

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test rerank ml unknown drift falls back

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
assert out[0]['fact_id'] == 'b'
```

### Step 2: Assign drifted = ActiveModel(...)

```python
drifted = ActiveModel(profile_id=model.profile_id, booster=model.booster, feature_names=tuple(FEATURE_NAMES) + ('alien',), trained_at=model.trained_at, sha256=model.sha256)
```

### Step 3: Assign r = AdaptiveRanker(...)

```python
r = AdaptiveRanker(signal_count=500, active_model=drifted)
```

### Step 4: Assign results = value

```python
results = [{'fact_id': 'a', 'cross_encoder_score': 0.5, 'trust_score': 0.5, 'fact': {'age_days': 0, 'access_count': 0}}, {'fact_id': 'b', 'cross_encoder_score': 0.9, 'trust_score': 0.5, 'fact': {'age_days': 0, 'access_count': 0}}]
```

### Step 5: Assign out = r.rerank(...)

```python
out = r.rerank(results, {})
```

**Verification:**
```python
assert out[0]['fact_id'] == 'b'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
_, model = _trained_model(tmp_path)
drifted = ActiveModel(profile_id=model.profile_id, booster=model.booster, feature_names=tuple(FEATURE_NAMES) + ('alien',), trained_at=model.trained_at, sha256=model.sha256)
r = AdaptiveRanker(signal_count=500, active_model=drifted)
results = [{'fact_id': 'a', 'cross_encoder_score': 0.5, 'trust_score': 0.5, 'fact': {'age_days': 0, 'access_count': 0}}, {'fact_id': 'b', 'cross_encoder_score': 0.9, 'trust_score': 0.5, 'fact': {'age_days': 0, 'access_count': 0}}]
out = r.rerank(results, {})
assert out[0]['fact_id'] == 'b'
```

## Next Steps


---

*Source: test_ranker_v2.py:305 | Complexity: Intermediate | Last updated: 2026-05-05*