# How To: Rerank Passes Correct Documents

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test rerank passes correct documents

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
assert req['cmd'] == 'rerank'
```

### Step 2: Assign reranker._model_loaded = True

```python
reranker._model_loaded = True
```

**Verification:**
```python
assert req['query'] == 'my query'
```

### Step 3: Assign candidates = value

```python
candidates = [(_make_fact('f1', 'doc one'), 0.5), (_make_fact('f2', 'doc two'), 0.3)]
```

**Verification:**
```python
assert req['documents'] == ['doc one', 'doc two']
```

### Step 4: Assign req = value

```python
req = mock_send.call_args[0][0]
```

**Verification:**
```python
assert req['cmd'] == 'rerank'
```

### Step 5: Call reranker.rerank()

```python
reranker.rerank('my query', candidates)
```


## Complete Example

```python
# Workflow
reranker = _make_reranker(model_name='fake-model')
reranker._model_loaded = True
candidates = [(_make_fact('f1', 'doc one'), 0.5), (_make_fact('f2', 'doc two'), 0.3)]
with patch.object(reranker, '_send_request', return_value={'ok': True, 'scores': [0.8, 0.4]}) as mock_send:
    reranker.rerank('my query', candidates)
req = mock_send.call_args[0][0]
assert req['cmd'] == 'rerank'
assert req['query'] == 'my query'
assert req['documents'] == ['doc one', 'doc two']
```

## Next Steps


---

*Source: test_reranker.py:295 | Complexity: Intermediate | Last updated: 2026-05-05*