# How To: Lgbm Bypass When No Model

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: E3: model=None → no predict, input order preserved.

## Prerequisites

**Required Modules:**
- `__future__`
- `dataclasses`
- `typing`
- `pytest`
- `superlocalmemory.learning.ensemble`
- `json`


## Step-by-Step Guide

### Step 1: 'E3: model=None → no predict, input order preserved.'

```python
'E3: model=None → no predict, input order preserved.'
```

**Verification:**
```python
assert out == candidates
```

### Step 2: Assign booster = _FakeBooster(...)

```python
booster = _FakeBooster()
```

**Verification:**
```python
assert booster.calls == 0
```

### Step 3: Assign model = None

```python
model = None
```

### Step 4: Assign candidates = _mk_candidates(...)

```python
candidates = _mk_candidates(4)
```

### Step 5: Assign weights = EnsembleWeights(...)

```python
weights = EnsembleWeights(1.0, 0.0)
```

### Step 6: Assign out = ensemble_rerank(...)

```python
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
```

**Verification:**
```python
assert out == candidates
```


## Complete Example

```python
# Workflow
'E3: model=None → no predict, input order preserved.'
booster = _FakeBooster()
model = None
candidates = _mk_candidates(4)
weights = EnsembleWeights(1.0, 0.0)
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
assert out == candidates
assert booster.calls == 0
```

## Next Steps


---

*Source: test_ensemble.py:139 | Complexity: Intermediate | Last updated: 2026-05-05*