# How To: Lgbm Bypass When Zero Lgbm Weight

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: E3: lgbm weight = 0 → no predict even if model is present.

## Prerequisites

**Required Modules:**
- `__future__`
- `dataclasses`
- `typing`
- `pytest`
- `superlocalmemory.learning.ensemble`
- `json`


## Step-by-Step Guide

### Step 1: 'E3: lgbm weight = 0 → no predict even if model is present.'

```python
'E3: lgbm weight = 0 → no predict even if model is present.'
```

**Verification:**
```python
assert booster.calls == 0
```

### Step 2: Assign booster = _FakeBooster(...)

```python
booster = _FakeBooster()
```

**Verification:**
```python
assert out == candidates
```

### Step 3: Assign model = _FakeModel(...)

```python
model = _FakeModel(booster=booster)
```

### Step 4: Assign weights = EnsembleWeights(...)

```python
weights = EnsembleWeights(1.0, 0.0)
```

### Step 5: Assign candidates = _mk_candidates(...)

```python
candidates = _mk_candidates(5)
```

### Step 6: Assign out = ensemble_rerank(...)

```python
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
```

**Verification:**
```python
assert booster.calls == 0
```


## Complete Example

```python
# Workflow
'E3: lgbm weight = 0 → no predict even if model is present.'
booster = _FakeBooster()
model = _FakeModel(booster=booster)
weights = EnsembleWeights(1.0, 0.0)
candidates = _mk_candidates(5)
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
assert booster.calls == 0
assert out == candidates
```

## Next Steps


---

*Source: test_ensemble.py:150 | Complexity: Intermediate | Last updated: 2026-05-05*