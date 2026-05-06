# How To: Seed Reproducibility

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test seed reproducibility

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
ld = LangevinDynamics()
```

### Step 2: Assign pos = value

```python
pos = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
```

### Step 3: Assign unknown = ld.step(...)

```python
p1, w1 = ld.step(pos, 5, 2.0, 0.5, seed=123)
```

### Step 4: Assign unknown = ld.step(...)

```python
p2, w2 = ld.step(pos, 5, 2.0, 0.5, seed=123)
```

### Step 5: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(p1, p2)
```

### Step 6: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(w1, w2)
```


## Complete Example

```python
# Workflow
ld = LangevinDynamics()
pos = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
p1, w1 = ld.step(pos, 5, 2.0, 0.5, seed=123)
p2, w2 = ld.step(pos, 5, 2.0, 0.5, seed=123)
np.testing.assert_allclose(p1, p2)
np.testing.assert_allclose(w1, w2)
```

## Next Steps


---

*Source: test_langevin.py:98 | Complexity: Intermediate | Last updated: 2026-05-05*