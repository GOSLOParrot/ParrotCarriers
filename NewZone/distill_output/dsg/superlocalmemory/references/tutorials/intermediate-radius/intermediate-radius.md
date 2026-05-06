# How To: Intermediate Radius

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test intermediate radius

## Prerequisites

**Required Modules:**
- `__future__`
- `numpy`
- `pytest`
- `superlocalmemory.math.langevin`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign ld = LangevinDynamics(...)

```python
ld = LangevinDynamics(weight_range=(0.0, 1.0))
```

### Step 2: Assign pos = value

```python
pos = [0.5 / np.sqrt(8)] * 8
```

### Step 3: Assign w = ld.compute_lifecycle_weight(...)

```python
w = ld.compute_lifecycle_weight(pos)
```

### Step 4: Assign expected_radius = np.linalg.norm(...)

```python
expected_radius = np.linalg.norm(pos)
```

### Step 5: Assign expected_weight = value

```python
expected_weight = 1.0 - expected_radius / _MAX_NORM
```

### Step 6: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(w, expected_weight, atol=1e-06)
```


## Complete Example

```python
# Workflow
ld = LangevinDynamics(weight_range=(0.0, 1.0))
pos = [0.5 / np.sqrt(8)] * 8
w = ld.compute_lifecycle_weight(pos)
expected_radius = np.linalg.norm(pos)
expected_weight = 1.0 - expected_radius / _MAX_NORM
np.testing.assert_allclose(w, expected_weight, atol=1e-06)
```

## Next Steps


---

*Source: test_langevin.py:155 | Complexity: Intermediate | Last updated: 2026-05-05*