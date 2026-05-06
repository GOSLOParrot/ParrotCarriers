# How To: Variance Within Bounds

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test variance within bounds

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`


## Step-by-Step Guide

### Step 1: Assign fm = FisherRaoMetric(...)

```python
fm = FisherRaoMetric()
```

**Verification:**
```python
assert np.all(arr >= _VARIANCE_FLOOR - 1e-12)
```

### Step 2: Assign emb = np.random.default_rng.standard_normal.tolist(...)

```python
emb = np.random.default_rng(42).standard_normal(768).tolist()
```

**Verification:**
```python
assert np.all(arr <= _VARIANCE_CEIL + 1e-12)
```

### Step 3: Assign unknown = fm.compute_params(...)

```python
_, var = fm.compute_params(emb)
```

### Step 4: Assign arr = np.array(...)

```python
arr = np.array(var)
```

**Verification:**
```python
assert np.all(arr >= _VARIANCE_FLOOR - 1e-12)
```


## Complete Example

```python
# Workflow
fm = FisherRaoMetric()
emb = np.random.default_rng(42).standard_normal(768).tolist()
_, var = fm.compute_params(emb)
arr = np.array(var)
assert np.all(arr >= _VARIANCE_FLOOR - 1e-12)
assert np.all(arr <= _VARIANCE_CEIL + 1e-12)
```

## Next Steps


---

*Source: test_fisher.py:73 | Complexity: Intermediate | Last updated: 2026-05-05*