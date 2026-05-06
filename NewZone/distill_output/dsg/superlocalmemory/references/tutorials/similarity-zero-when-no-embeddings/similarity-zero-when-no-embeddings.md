# How To: Similarity Zero When No Embeddings

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: When vector_store is None, similarity should not contribute.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.hooks.auto_invoker`
- `math`
- `math`
- `math`


## Step-by-Step Guide

### Step 1: 'When vector_store is None, similarity should not contribute.'

```python
'When vector_store is None, similarity should not contribute.'
```

**Verification:**
```python
assert abs(score - expected) < 0.001
```

### Step 2: Assign invoker = _make_scoring_invoker(...)

```python
invoker = _make_scoring_invoker(vector_store=None)
```

### Step 3: Assign signals = value

```python
signals = {'similarity': 0.0, 'recency': 0.5, 'frequency': 0.5, 'trust': 0.5}
```

### Step 4: Assign score = invoker._combine_signals(...)

```python
score = invoker._combine_signals(signals)
```

### Step 5: Assign expected = value

```python
expected = 0.0 * 0.0 + 0.4 * 0.5 + 0.35 * 0.5 + 0.25 * 0.5
```

**Verification:**
```python
assert abs(score - expected) < 0.001
```


## Complete Example

```python
# Workflow
'When vector_store is None, similarity should not contribute.'
invoker = _make_scoring_invoker(vector_store=None)
signals = {'similarity': 0.0, 'recency': 0.5, 'frequency': 0.5, 'trust': 0.5}
score = invoker._combine_signals(signals)
expected = 0.0 * 0.0 + 0.4 * 0.5 + 0.35 * 0.5 + 0.25 * 0.5
assert abs(score - expected) < 0.001
```

## Next Steps


---

*Source: test_multi_signal_scoring.py:168 | Complexity: Intermediate | Last updated: 2026-05-05*