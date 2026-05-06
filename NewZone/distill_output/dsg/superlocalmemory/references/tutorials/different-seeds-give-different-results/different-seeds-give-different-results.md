# How To: Different Seeds Give Different Results

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test different seeds give different results

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

**Verification:**
```python
assert not np.allclose(p1, p2)
```

### Step 2: Assign pos = value

```python
pos = [0.1] * 8
```

### Step 3: Assign unknown = ld.step(...)

```python
p1, _ = ld.step(pos, 5, 2.0, 0.5, seed=1)
```

### Step 4: Assign unknown = ld.step(...)

```python
p2, _ = ld.step(pos, 5, 2.0, 0.5, seed=2)
```

**Verification:**
```python
assert not np.allclose(p1, p2)
```


## Complete Example

```python
# Workflow
ld = LangevinDynamics()
pos = [0.1] * 8
p1, _ = ld.step(pos, 5, 2.0, 0.5, seed=1)
p2, _ = ld.step(pos, 5, 2.0, 0.5, seed=2)
assert not np.allclose(p1, p2)
```

## Next Steps


---

*Source: test_langevin.py:106 | Complexity: Intermediate | Last updated: 2026-05-05*