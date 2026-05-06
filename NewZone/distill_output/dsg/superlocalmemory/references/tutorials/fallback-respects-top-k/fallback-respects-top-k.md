# How To: Fallback Respects Top K

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test fallback respects top k

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
assert len(results) == 2
```

### Step 2: Assign reranker._model_loaded = False

```python
reranker._model_loaded = False
```

### Step 3: Assign candidates = _make_candidates(...)

```python
candidates = _make_candidates(5)
```

### Step 4: Assign results = reranker.rerank(...)

```python
results = reranker.rerank('query', candidates, top_k=2)
```

**Verification:**
```python
assert len(results) == 2
```


## Complete Example

```python
# Workflow
reranker = _make_reranker(model_name='fake-model')
reranker._model_loaded = False
candidates = _make_candidates(5)
results = reranker.rerank('query', candidates, top_k=2)
assert len(results) == 2
```

## Next Steps


---

*Source: test_reranker.py:355 | Complexity: Intermediate | Last updated: 2026-05-05*