# How To: Seed Consistency In Batch

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test seed consistency in batch

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
ld = LangevinDynamics(dim=4)
```

### Step 2: Assign facts = value

```python
facts = [{'fact_id': f'f{i}', 'position': [0.1 * i] * 4, 'access_count': i, 'age_days': float(i), 'importance': 0.5} for i in range(5)]
```

### Step 3: Assign r1 = ld.batch_step(...)

```python
r1 = ld.batch_step(facts, seed=100)
```

### Step 4: Assign r2 = ld.batch_step(...)

```python
r2 = ld.batch_step(facts, seed=100)
```

### Step 5: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(a['position'], b['position'])
```


## Complete Example

```python
# Workflow
ld = LangevinDynamics(dim=4)
facts = [{'fact_id': f'f{i}', 'position': [0.1 * i] * 4, 'access_count': i, 'age_days': float(i), 'importance': 0.5} for i in range(5)]
r1 = ld.batch_step(facts, seed=100)
r2 = ld.batch_step(facts, seed=100)
for a, b in zip(r1, r2):
    np.testing.assert_allclose(a['position'], b['position'])
```

## Next Steps


---

*Source: test_langevin.py:246 | Complexity: Intermediate | Last updated: 2026-05-05*