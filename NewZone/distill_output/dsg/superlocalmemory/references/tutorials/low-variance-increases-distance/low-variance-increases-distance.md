# How To: Low Variance Increases Distance

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test low variance increases distance

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
assert sim_high_var > sim_low_var
```

### Step 2: Assign mu_f = np.array(...)

```python
mu_f = np.array([0.5, 0.0])
```

### Step 3: Assign var_high = np.array(...)

```python
var_high = np.array([10.0, 10.0])
```

### Step 4: Assign var_low = np.array(...)

```python
var_low = np.array([0.01, 0.01])
```

### Step 5: Assign sim_high_var = _fisher_rao_similarity(...)

```python
sim_high_var = _fisher_rao_similarity(mu_q, mu_f, var_high, temperature=15.0)
```

### Step 6: Assign sim_low_var = _fisher_rao_similarity(...)

```python
sim_low_var = _fisher_rao_similarity(mu_q, mu_f, var_low, temperature=15.0)
```

**Verification:**
```python
assert sim_high_var > sim_low_var
```


## Complete Example

```python
# Workflow
mu_q = np.array([1.0, 0.0])
mu_f = np.array([0.5, 0.0])
var_high = np.array([10.0, 10.0])
var_low = np.array([0.01, 0.01])
sim_high_var = _fisher_rao_similarity(mu_q, mu_f, var_high, temperature=15.0)
sim_low_var = _fisher_rao_similarity(mu_q, mu_f, var_low, temperature=15.0)
assert sim_high_var > sim_low_var
```

## Next Steps


---

*Source: test_semantic_channel.py:107 | Complexity: Intermediate | Last updated: 2026-05-05*