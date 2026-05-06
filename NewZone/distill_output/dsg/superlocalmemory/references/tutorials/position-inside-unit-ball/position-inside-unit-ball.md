# How To: Position Inside Unit Ball

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: All returned positions must have norm < 1.

## Prerequisites

**Required Modules:**
- `__future__`
- `numpy`
- `pytest`
- `superlocalmemory.math.langevin`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'All returned positions must have norm < 1.'

```python
'All returned positions must have norm < 1.'
```

**Verification:**
```python
assert norm < 1.0, f'Position norm {norm} >= 1.0 at iteration {i}'
```

### Step 2: Assign ld = LangevinDynamics(...)

```python
ld = LangevinDynamics(dim=8, temperature=5.0)
```

### Step 3: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(99)
```

### Step 4: Assign pos = unknown.tolist(...)

```python
pos = (rng.standard_normal(8) * 0.5).tolist()
```

### Step 5: Assign unknown = ld.step(...)

```python
new_pos, _ = ld.step(pos, access_count=i, age_days=float(i), importance=0.5, seed=i)
```

### Step 6: Assign norm = np.linalg.norm(...)

```python
norm = np.linalg.norm(new_pos)
```

**Verification:**
```python
assert norm < 1.0, f'Position norm {norm} >= 1.0 at iteration {i}'
```


## Complete Example

```python
# Workflow
'All returned positions must have norm < 1.'
ld = LangevinDynamics(dim=8, temperature=5.0)
rng = np.random.default_rng(99)
for i in range(50):
    pos = (rng.standard_normal(8) * 0.5).tolist()
    new_pos, _ = ld.step(pos, access_count=i, age_days=float(i), importance=0.5, seed=i)
    norm = np.linalg.norm(new_pos)
    assert norm < 1.0, f'Position norm {norm} >= 1.0 at iteration {i}'
```

## Next Steps


---

*Source: test_langevin.py:82 | Complexity: Intermediate | Last updated: 2026-05-05*