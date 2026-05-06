# How To: Different Means Lower Score

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test different means lower score

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.semantic_channel`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign mu_q = np.array(...)

```python
mu_q = np.array([1.0, 0.0])
```

**Verification:**
```python
assert 0.0 < sim < 1.0
```

### Step 2: Assign mu_f = np.array(...)

```python
mu_f = np.array([0.0, 1.0])
```

### Step 3: Assign var = np.array(...)

```python
var = np.array([1.0, 1.0])
```

### Step 4: Assign sim = _fisher_rao_similarity(...)

```python
sim = _fisher_rao_similarity(mu_q, mu_f, var, temperature=15.0)
```

**Verification:**
```python
assert 0.0 < sim < 1.0
```


## Complete Example

```python
# Workflow
mu_q = np.array([1.0, 0.0])
mu_f = np.array([0.0, 1.0])
var = np.array([1.0, 1.0])
sim = _fisher_rao_similarity(mu_q, mu_f, var, temperature=15.0)
assert 0.0 < sim < 1.0
```

## Next Steps


---

*Source: test_semantic_channel.py:100 | Complexity: Intermediate | Last updated: 2026-05-05*