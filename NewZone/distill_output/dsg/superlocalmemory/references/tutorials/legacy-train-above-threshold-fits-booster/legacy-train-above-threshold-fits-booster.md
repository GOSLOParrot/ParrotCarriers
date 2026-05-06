# How To: Legacy Train Above Threshold Fits Booster

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test legacy train above threshold fits booster

## Prerequisites

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


## Step-by-Step Guide

### Step 1: Assign training = value

```python
training = []
```

**Verification:**
```python
assert ok is True
```

### Step 2: Assign r = AdaptiveRanker(...)

```python
r = AdaptiveRanker(signal_count=0)
```

**Verification:**
```python
assert r.active_model is not None
```

### Step 3: Assign ok = r.train(...)

```python
ok = r.train(training)
```

**Verification:**
```python
assert state is not None
```

### Step 4: Assign state = r.get_model_state(...)

```python
state = r.get_model_state()
```

**Verification:**
```python
assert isinstance(state, bytes)
```

### Step 5: Call training.append()

```python
training.append({'features': {'semantic_score': i % 10 / 10.0, 'cross_encoder_score': i % 5 / 5.0}, 'label': 1.0 if i % 2 == 0 else 0.0})
```


## Complete Example

```python
# Workflow
training = []
for i in range(220):
    training.append({'features': {'semantic_score': i % 10 / 10.0, 'cross_encoder_score': i % 5 / 5.0}, 'label': 1.0 if i % 2 == 0 else 0.0})
r = AdaptiveRanker(signal_count=0)
ok = r.train(training)
assert ok is True
assert r.active_model is not None
state = r.get_model_state()
assert state is not None
assert isinstance(state, bytes)
```

## Next Steps


---

*Source: test_ranker_v2.py:357 | Complexity: Intermediate | Last updated: 2026-05-05*