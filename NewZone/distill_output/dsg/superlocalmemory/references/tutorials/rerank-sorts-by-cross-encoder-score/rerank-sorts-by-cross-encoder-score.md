# How To: Rerank Sorts By Cross Encoder Score

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test rerank sorts by cross encoder score

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.retrieval.reranker`
- `superlocalmemory.storage.models`
- `importlib`
- `superlocalmemory.retrieval`


## Step-by-Step Guide

### Step 1: Assign reranker = _make_reranker(...)

```python
reranker = _make_reranker(model_name='fake-model')
```

**Verification:**
```python
assert results[0][0].fact_id == 'f2'
```

### Step 2: Assign reranker._model_loaded = True

```python
reranker._model_loaded = True
```

**Verification:**
```python
assert results[0][1] == pytest.approx(0.9)
```

### Step 3: Assign candidates = _make_candidates(...)

```python
candidates = _make_candidates(3)
```

**Verification:**
```python
assert results[1][0].fact_id == 'f1'
```

### Step 4: Assign results = reranker.rerank(...)

```python
results = reranker.rerank('query', candidates, top_k=10)
```

**Verification:**
```python
assert results[2][0].fact_id == 'f0'
```


## Complete Example

```python
# Workflow
reranker = _make_reranker(model_name='fake-model')
reranker._model_loaded = True
candidates = _make_candidates(3)
with patch.object(reranker, '_send_request', return_value={'ok': True, 'scores': [0.1, 0.5, 0.9]}):
    results = reranker.rerank('query', candidates, top_k=10)
assert results[0][0].fact_id == 'f2'
assert results[0][1] == pytest.approx(0.9)
assert results[1][0].fact_id == 'f1'
assert results[2][0].fact_id == 'f0'
```

## Next Steps


---

*Source: test_reranker.py:265 | Complexity: Intermediate | Last updated: 2026-05-05*