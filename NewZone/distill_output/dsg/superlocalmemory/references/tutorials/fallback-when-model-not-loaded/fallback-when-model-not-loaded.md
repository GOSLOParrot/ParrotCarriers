# How To: Fallback When Model Not Loaded

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: When worker hasn't loaded model yet, return by existing score.

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

### Step 1: "When worker hasn't loaded model yet, return by existing score."

```python
"When worker hasn't loaded model yet, return by existing score."
```

**Verification:**
```python
assert results[0][0].fact_id == 'f2'
```

### Step 2: Assign reranker = _make_reranker(...)

```python
reranker = _make_reranker(model_name='fake-model')
```

**Verification:**
```python
assert results[1][0].fact_id == 'f3'
```

### Step 3: Assign reranker._model_loaded = False

```python
reranker._model_loaded = False
```

### Step 4: Assign candidates = value

```python
candidates = [(_make_fact('f1'), 0.3), (_make_fact('f2'), 0.9), (_make_fact('f3'), 0.6)]
```

### Step 5: Assign results = reranker.rerank(...)

```python
results = reranker.rerank('query', candidates)
```

**Verification:**
```python
assert results[0][0].fact_id == 'f2'
```


## Complete Example

```python
# Workflow
"When worker hasn't loaded model yet, return by existing score."
reranker = _make_reranker(model_name='fake-model')
reranker._model_loaded = False
candidates = [(_make_fact('f1'), 0.3), (_make_fact('f2'), 0.9), (_make_fact('f3'), 0.6)]
results = reranker.rerank('query', candidates)
assert results[0][0].fact_id == 'f2'
assert results[1][0].fact_id == 'f3'
```

## Next Steps


---

*Source: test_reranker.py:320 | Complexity: Intermediate | Last updated: 2026-05-05*