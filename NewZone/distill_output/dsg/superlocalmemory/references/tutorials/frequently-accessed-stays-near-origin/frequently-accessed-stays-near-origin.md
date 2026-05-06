# How To: Frequently Accessed Stays Near Origin

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: High access count + high importance should keep memory near origin.

## Prerequisites

**Required Modules:**
- `__future__`
- `numpy`
- `pytest`
- `superlocalmemory.math.langevin`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'High access count + high importance should keep memory near origin.'

```python
'High access count + high importance should keep memory near origin.'
```

**Verification:**
```python
assert norm < 0.8, f'Heavily accessed memory drifted to norm={norm}'
```

### Step 2: Assign ld = LangevinDynamics(...)

```python
ld = LangevinDynamics(dim=4, dt=0.01, temperature=0.5)
```

### Step 3: Assign pos = value

```python
pos = [0.0, 0.0, 0.0, 0.0]
```

### Step 4: Assign norm = np.linalg.norm(...)

```python
norm = np.linalg.norm(pos)
```

**Verification:**
```python
assert norm < 0.8, f'Heavily accessed memory drifted to norm={norm}'
```

### Step 5: Assign unknown = ld.step(...)

```python
pos, w = ld.step(pos, access_count=100, age_days=1.0, importance=1.0, seed=i)
```


## Complete Example

```python
# Workflow
'High access count + high importance should keep memory near origin.'
ld = LangevinDynamics(dim=4, dt=0.01, temperature=0.5)
pos = [0.0, 0.0, 0.0, 0.0]
for i in range(20):
    pos, w = ld.step(pos, access_count=100, age_days=1.0, importance=1.0, seed=i)
norm = np.linalg.norm(pos)
assert norm < 0.8, f'Heavily accessed memory drifted to norm={norm}'
```

## Next Steps


---

*Source: test_langevin.py:304 | Complexity: Intermediate | Last updated: 2026-05-05*