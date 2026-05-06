# How To: With Scaled Restriction

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test with scaled restriction

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
emb_a = np.array([1.0, 2.0])
```

### Step 2: Assign emb_b = np.array(...)

```python
emb_b = np.array([3.0, 4.0])
```

### Step 3: Assign R_a = value

```python
R_a = 0.5 * np.eye(2)
```

### Step 4: Assign R_b = np.eye(...)

```python
R_b = np.eye(2)
```

### Step 5: Assign residual = edge_residual(...)

```python
residual = edge_residual(emb_a, emb_b, R_a, R_b)
```

### Step 6: Assign expected = value

```python
expected = R_b @ emb_b - R_a @ emb_a
```

### Step 7: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(residual, expected)
```


## Complete Example

```python
# Workflow
emb_a = np.array([1.0, 2.0])
emb_b = np.array([3.0, 4.0])
R_a = 0.5 * np.eye(2)
R_b = np.eye(2)
residual = edge_residual(emb_a, emb_b, R_a, R_b)
expected = R_b @ emb_b - R_a @ emb_a
np.testing.assert_allclose(residual, expected)
```

## Next Steps


---

*Source: test_sheaf.py:103 | Complexity: Intermediate | Last updated: 2026-05-05*