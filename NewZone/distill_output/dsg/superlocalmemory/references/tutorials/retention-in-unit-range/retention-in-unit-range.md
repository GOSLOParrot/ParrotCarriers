# How To: Retention In Unit Range

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: 0 <= R(t, S) <= 1 for 100 random inputs.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `random`
- `datetime`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.ebbinghaus`
- `statistics`
- `unittest.mock`

**Setup Required:**
```python
# Fixtures: curve
```

## Step-by-Step Guide

### Step 1: '0 <= R(t, S) <= 1 for 100 random inputs.'

```python
'0 <= R(t, S) <= 1 for 100 random inputs.'
```

**Verification:**
```python
assert 0.0 <= r <= 1.0, f'Retention {r} out of [0,1] for t={hours}, S={strength}'
```

### Step 2: Assign rng = random.Random(...)

```python
rng = random.Random(42)
```

### Step 3: Assign hours = rng.uniform(...)

```python
hours = rng.uniform(0.0, 10000.0)
```

### Step 4: Assign strength = rng.uniform(...)

```python
strength = rng.uniform(0.001, 200.0)
```

### Step 5: Assign r = curve.retention(...)

```python
r = curve.retention(hours, strength)
```

**Verification:**
```python
assert 0.0 <= r <= 1.0, f'Retention {r} out of [0,1] for t={hours}, S={strength}'
```


## Complete Example

```python
# Setup
# Fixtures: curve

# Workflow
'0 <= R(t, S) <= 1 for 100 random inputs.'
rng = random.Random(42)
for _ in range(100):
    hours = rng.uniform(0.0, 10000.0)
    strength = rng.uniform(0.001, 200.0)
    r = curve.retention(hours, strength)
    assert 0.0 <= r <= 1.0, f'Retention {r} out of [0,1] for t={hours}, S={strength}'
```

## Next Steps


---

*Source: test_ebbinghaus.py:53 | Complexity: Intermediate | Last updated: 2026-05-05*