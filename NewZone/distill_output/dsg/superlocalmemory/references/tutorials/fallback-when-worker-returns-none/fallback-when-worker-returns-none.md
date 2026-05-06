# How To: Fallback When Worker Returns None

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When worker crashes or times out, return by existing score.

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

### Step 1: 'When worker crashes or times out, return by existing score.'

```python
'When worker crashes or times out, return by existing score.'
```

**Verification:**
```python
assert results[0][0].fact_id == 'f0'
```

### Step 2: Assign reranker = _make_reranker(...)

```python
reranker = _make_reranker(model_name='fake-model')
```

### Step 3: Assign reranker._model_loaded = True

```python
reranker._model_loaded = True
```

### Step 4: Assign candidates = _make_candidates(...)

```python
candidates = _make_candidates(3)
```

**Verification:**
```python
assert results[0][0].fact_id == 'f0'
```

### Step 5: Assign results = reranker.rerank(...)

```python
results = reranker.rerank('query', candidates)
```


## Complete Example

```python
# Workflow
'When worker crashes or times out, return by existing score.'
reranker = _make_reranker(model_name='fake-model')
reranker._model_loaded = True
candidates = _make_candidates(3)
with patch.object(reranker, '_send_request', return_value=None):
    results = reranker.rerank('query', candidates)
assert results[0][0].fact_id == 'f0'
```

## Next Steps


---

*Source: test_reranker.py:333 | Complexity: Intermediate | Last updated: 2026-05-05*