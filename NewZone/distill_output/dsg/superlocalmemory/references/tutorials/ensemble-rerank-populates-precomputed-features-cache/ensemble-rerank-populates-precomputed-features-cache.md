# How To: Ensemble Rerank Populates Precomputed Features Cache

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: PERF-v2-02: ``ensemble_rerank`` MUST stash a
``{fact_id: features_json_str}`` dict on
``query_context['_precomputed_features_json']`` so the downstream
signal writer can skip re-extracting features for the same candidates.

## Prerequisites

**Required Modules:**
- `__future__`
- `dataclasses`
- `typing`
- `pytest`
- `superlocalmemory.learning.ensemble`
- `json`


## Step-by-Step Guide

### Step 1: "PERF-v2-02: ``ensemble_rerank`` MUST stash a\n    ``{fact_id: features_json_str}`` dict on\n    ``query_context['_precomputed_features_json']`` so the downstream\n    signal writer can skip re-extracting features for the same candidates.\n    "

```python
"PERF-v2-02: ``ensemble_rerank`` MUST stash a\n    ``{fact_id: features_json_str}`` dict on\n    ``query_context['_precomputed_features_json']`` so the downstream\n    signal writer can skip re-extracting features for the same candidates.\n    "
```

**Verification:**
```python
assert len(out) == 3
```

### Step 2: Assign model = _FakeModel(...)

```python
model = _FakeModel(booster=_FakeBooster())
```

**Verification:**
```python
assert isinstance(cache, dict), 'ensemble_rerank must populate _precomputed_features_json'
```

### Step 3: Assign candidates = _mk_candidates(...)

```python
candidates = _mk_candidates(3)
```

**Verification:**
```python
assert expected in cache, f'{expected} missing from features cache'
```

### Step 4: Assign out = ensemble_rerank(...)

```python
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, EnsembleWeights(bandit=0.4, lgbm=0.6), query_context)
```

**Verification:**
```python
assert 'semantic_score' in parsed
```

### Step 5: Assign cache = query_context.get(...)

```python
cache = query_context.get('_precomputed_features_json')
```

**Verification:**
```python
assert 'cross_encoder_score' in parsed
```

### Step 6: Assign c.fact_id = value

```python
c.fact_id = f'f{i}'
```

**Verification:**
```python
assert expected in cache, f'{expected} missing from features cache'
```

### Step 7: Assign parsed = _json.loads(...)

```python
parsed = _json.loads(cache[expected])
```

**Verification:**
```python
assert 'semantic_score' in parsed
```


## Complete Example

```python
# Workflow
"PERF-v2-02: ``ensemble_rerank`` MUST stash a\n    ``{fact_id: features_json_str}`` dict on\n    ``query_context['_precomputed_features_json']`` so the downstream\n    signal writer can skip re-extracting features for the same candidates.\n    "
import json as _json
model = _FakeModel(booster=_FakeBooster())
candidates = _mk_candidates(3)
for i, c in enumerate(candidates):
    c.fact_id = f'f{i}'
query_context: dict = {'query_type': 'single_hop', 'profile_id': 'p'}
out = ensemble_rerank(candidates, _FakeBanditChoice(), model, EnsembleWeights(bandit=0.4, lgbm=0.6), query_context)
assert len(out) == 3
cache = query_context.get('_precomputed_features_json')
assert isinstance(cache, dict), 'ensemble_rerank must populate _precomputed_features_json'
for expected in ('f0', 'f1', 'f2'):
    assert expected in cache, f'{expected} missing from features cache'
    parsed = _json.loads(cache[expected])
    assert 'semantic_score' in parsed
    assert 'cross_encoder_score' in parsed
```

## Next Steps


---

*Source: test_ensemble.py:255 | Complexity: Intermediate | Last updated: 2026-05-05*