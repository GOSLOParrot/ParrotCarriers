# How To: Different Embeddings Nonzero

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test different embeddings nonzero

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
emb_b = np.array([0.0, 1.0])
```

### Step 3: Assign R = np.eye(...)

```python
R = np.eye(2)
```

### Step 4: Assign residual = edge_residual(...)

```python
residual = edge_residual(emb_a, emb_b, R, R)
```

### Step 5: Assign expected = value

```python
expected = emb_b - emb_a
```

### Step 6: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(residual, expected)
```


## Complete Example

```python
# Workflow
emb_a = np.array([1.0, 0.0])
emb_b = np.array([0.0, 1.0])
R = np.eye(2)
residual = edge_residual(emb_a, emb_b, R, R)
expected = emb_b - emb_a
np.testing.assert_allclose(residual, expected)
```

## Next Steps


---

*Source: test_sheaf.py:95 | Complexity: Intermediate | Last updated: 2026-05-05*