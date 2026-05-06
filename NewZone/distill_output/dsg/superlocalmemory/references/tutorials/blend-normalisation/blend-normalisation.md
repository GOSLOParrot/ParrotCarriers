# How To: Blend Normalisation

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: E4: mixed-magnitude streams ([-10,10] vs [0,1]) both enter [0,1].

Also verify stable ordering under both sort directions.

## Prerequisites

**Required Modules:**
- `__future__`
- `dataclasses`
- `typing`
- `pytest`
- `superlocalmemory.learning.ensemble`
- `json`


## Step-by-Step Guide

### Step 1: 'E4: mixed-magnitude streams ([-10,10] vs [0,1]) both enter [0,1].\n\n    Also verify stable ordering under both sort directions.\n    '

```python
'E4: mixed-magnitude streams ([-10,10] vs [0,1]) both enter [0,1].\n\n    Also verify stable ordering under both sort directions.\n    '
```

**Verification:**
```python
assert {c.fact_id for c in out} == {'a', 'b', 'c', 'd'}
```

### Step 2: Assign booster = _FakeBooster(...)

```python
booster = _FakeBooster()
```

**Verification:**
```python
assert len(out) == 4
```

### Step 3: Call booster.scores_per_batch.append()

```python
booster.scores_per_batch.append([-10.0, 5.0, 10.0, 2.0])
```

### Step 4: Assign model = _FakeModel(...)

```python
model = _FakeModel(booster=booster)
```

### Step 5: Assign candidates = value

```python
candidates = [_Cand(fact_id='a', score=0.1), _Cand(fact_id='b', score=0.5), _Cand(fact_id='c', score=0.9), _Cand(fact_id='d', score=0.4)]
```

### Step 6: Assign weights = EnsembleWeights(...)

```python
weights = EnsembleWeights(0.4, 0.6)
```

### Step 7: Assign out = ensemble_rerank(...)

```python
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
```

**Verification:**
```python
assert {c.fact_id for c in out} == {'a', 'b', 'c', 'd'}
```


## Complete Example

```python
# Workflow
'E4: mixed-magnitude streams ([-10,10] vs [0,1]) both enter [0,1].\n\n    Also verify stable ordering under both sort directions.\n    '
booster = _FakeBooster()
booster.scores_per_batch.append([-10.0, 5.0, 10.0, 2.0])
model = _FakeModel(booster=booster)
candidates = [_Cand(fact_id='a', score=0.1), _Cand(fact_id='b', score=0.5), _Cand(fact_id='c', score=0.9), _Cand(fact_id='d', score=0.4)]
weights = EnsembleWeights(0.4, 0.6)
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, weights, {})
assert {c.fact_id for c in out} == {'a', 'b', 'c', 'd'}
assert len(out) == 4
```

## Next Steps


---

*Source: test_ensemble.py:209 | Complexity: Intermediate | Last updated: 2026-05-05*