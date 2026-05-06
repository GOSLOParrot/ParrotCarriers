# How To: Opposite Vectors High Severity

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test opposite vectors high severity

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `dataclasses`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.math.sheaf`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign emb_a = np.array(...)

```python
emb_a = np.array([1.0, 0.0])
```

### Step 2: Assign emb_b = np.array(...)

```python
emb_b = np.array([-1.0, 0.0])
```

### Step 3: Assign R = np.eye(...)

```python
R = np.eye(2)
```

### Step 4: Assign severity = coboundary_norm(...)

```python
severity = coboundary_norm(emb_a, emb_b, R, R)
```

### Step 5: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(severity, 1.0, atol=1e-10)
```


## Complete Example

```python
# Workflow
emb_a = np.array([1.0, 0.0])
emb_b = np.array([-1.0, 0.0])
R = np.eye(2)
severity = coboundary_norm(emb_a, emb_b, R, R)
np.testing.assert_allclose(severity, 1.0, atol=1e-10)
```

## Next Steps


---

*Source: test_sheaf.py:131 | Complexity: Intermediate | Last updated: 2026-05-05*