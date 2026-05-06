# How To: Processes All Facts

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: test processes all facts

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

**Verification:**
```python
assert len(results) == 3
```

### Step 2: Assign facts = value

```python
facts = [{'fact_id': 'f1', 'position': [0.0] * 4, 'access_count': 10, 'age_days': 1.0, 'importance': 0.8}, {'fact_id': 'f2', 'position': [0.2] * 4, 'access_count': 0, 'age_days': 30.0, 'importance': 0.2}, {'fact_id': 'f3', 'position': [0.1, -0.1, 0.05, 0.0], 'access_count': 5, 'age_days': 7.0, 'importance': 0.5}]
```

**Verification:**
```python
assert 'fact_id' in r
```

### Step 3: Assign results = ld.batch_step(...)

```python
results = ld.batch_step(facts, seed=42)
```

**Verification:**
```python
assert 'position' in r
```


## Complete Example

```python
# Workflow
ld = LangevinDynamics(dim=4)
facts = [{'fact_id': 'f1', 'position': [0.0] * 4, 'access_count': 10, 'age_days': 1.0, 'importance': 0.8}, {'fact_id': 'f2', 'position': [0.2] * 4, 'access_count': 0, 'age_days': 30.0, 'importance': 0.2}, {'fact_id': 'f3', 'position': [0.1, -0.1, 0.05, 0.0], 'access_count': 5, 'age_days': 7.0, 'importance': 0.5}]
results = ld.batch_step(facts, seed=42)
assert len(results) == 3
for r in results:
    assert 'fact_id' in r
    assert 'position' in r
    assert 'weight' in r
    assert 'lifecycle' in r
    assert len(r['position']) == 4
```

## Next Steps


---

*Source: test_langevin.py:209 | Complexity: Beginner | Last updated: 2026-05-05*