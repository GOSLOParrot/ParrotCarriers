# How To: Single Batch Predict Call

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: E2: booster.predict invoked exactly once per ensemble_rerank call.

## Prerequisites

**Required Modules:**
- `__future__`
- `dataclasses`
- `typing`
- `pytest`
- `superlocalmemory.learning.ensemble`
- `json`


## Step-by-Step Guide

### Step 1: 'E2: booster.predict invoked exactly once per ensemble_rerank call.'

```python
'E2: booster.predict invoked exactly once per ensemble_rerank call.'
```

**Verification:**
```python
assert booster.calls == 1
```

### Step 2: Assign booster = _FakeBooster(...)

```python
booster = _FakeBooster()
```

### Step 3: Assign model = _FakeModel(...)

```python
model = _FakeModel(booster=booster)
```

### Step 4: Assign candidates = _mk_candidates(...)

```python
candidates = _mk_candidates(10)
```

### Step 5: Assign weights = EnsembleWeights(...)

```python
weights = EnsembleWeights(0.4, 0.6)
```

### Step 6: Call ensemble_rerank()

```python
ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
```

**Verification:**
```python
assert booster.calls == 1
```


## Complete Example

```python
# Workflow
'E2: booster.predict invoked exactly once per ensemble_rerank call.'
booster = _FakeBooster()
model = _FakeModel(booster=booster)
candidates = _mk_candidates(10)
weights = EnsembleWeights(0.4, 0.6)
ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
assert booster.calls == 1
```

## Next Steps


---

*Source: test_ensemble.py:177 | Complexity: Intermediate | Last updated: 2026-05-05*