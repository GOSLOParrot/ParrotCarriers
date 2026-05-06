# How To: Temperature Effect

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test temperature effect

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
assert sim_high_t > sim_low_t
```

### Step 2: Assign mu_f = np.array(...)

```python
mu_f = np.array([0.0, 1.0])
```

### Step 3: Assign var = np.array(...)

```python
var = np.array([1.0, 1.0])
```

### Step 4: Assign sim_low_t = _fisher_rao_similarity(...)

```python
sim_low_t = _fisher_rao_similarity(mu_q, mu_f, var, temperature=1.0)
```

### Step 5: Assign sim_high_t = _fisher_rao_similarity(...)

```python
sim_high_t = _fisher_rao_similarity(mu_q, mu_f, var, temperature=100.0)
```

**Verification:**
```python
assert sim_high_t > sim_low_t
```


## Complete Example

```python
# Workflow
mu_q = np.array([1.0, 0.0])
mu_f = np.array([0.0, 1.0])
var = np.array([1.0, 1.0])
sim_low_t = _fisher_rao_similarity(mu_q, mu_f, var, temperature=1.0)
sim_high_t = _fisher_rao_similarity(mu_q, mu_f, var, temperature=100.0)
assert sim_high_t > sim_low_t
```

## Next Steps


---

*Source: test_semantic_channel.py:117 | Complexity: Intermediate | Last updated: 2026-05-05*