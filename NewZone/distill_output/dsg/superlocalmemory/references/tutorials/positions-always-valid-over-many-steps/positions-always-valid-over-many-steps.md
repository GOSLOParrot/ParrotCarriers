# How To: Positions Always Valid Over Many Steps

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test positions always valid over many steps

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
ld = LangevinDynamics(dim=8, dt=0.01, temperature=2.0)
```

**Verification:**
```python
assert norm < 1.0, f'Position escaped ball at step {i}: norm={norm}'
```

### Step 2: Assign pos = value

```python
pos = [0.5 / np.sqrt(8)] * 8
```

**Verification:**
```python
assert 0.0 <= w <= 1.0, f'Weight out of range at step {i}: {w}'
```

### Step 3: Assign unknown = ld.step(...)

```python
pos, w = ld.step(pos, access_count=0, age_days=100.0, importance=0.0, seed=i)
```

### Step 4: Assign norm = np.linalg.norm(...)

```python
norm = np.linalg.norm(pos)
```

**Verification:**
```python
assert norm < 1.0, f'Position escaped ball at step {i}: norm={norm}'
```


## Complete Example

```python
# Workflow
ld = LangevinDynamics(dim=8, dt=0.01, temperature=2.0)
pos = [0.5 / np.sqrt(8)] * 8
for i in range(100):
    pos, w = ld.step(pos, access_count=0, age_days=100.0, importance=0.0, seed=i)
    norm = np.linalg.norm(pos)
    assert norm < 1.0, f'Position escaped ball at step {i}: norm={norm}'
    assert 0.0 <= w <= 1.0, f'Weight out of range at step {i}: {w}'
```

## Next Steps


---

*Source: test_langevin.py:314 | Complexity: Intermediate | Last updated: 2026-05-05*