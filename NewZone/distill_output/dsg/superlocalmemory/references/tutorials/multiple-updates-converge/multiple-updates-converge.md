# How To: Multiple Updates Converge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Repeated identical observations should narrow variance toward floor.

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`


## Step-by-Step Guide

### Step 1: 'Repeated identical observations should narrow variance toward floor.'

```python
'Repeated identical observations should narrow variance toward floor.'
```

### Step 2: Assign fm = FisherRaoMetric(...)

```python
fm = FisherRaoMetric()
```

### Step 3: Assign var = value

```python
var = [_VARIANCE_CEIL] * 4
```

### Step 4: Assign obs = value

```python
obs = [1.0] * 4
```

### Step 5: Assign var = fm.bayesian_update(...)

```python
var = fm.bayesian_update(var, obs)
```

### Step 6: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(v, _VARIANCE_FLOOR, atol=0.01)
```


## Complete Example

```python
# Workflow
'Repeated identical observations should narrow variance toward floor.'
fm = FisherRaoMetric()
var = [_VARIANCE_CEIL] * 4
obs = [1.0] * 4
for _ in range(50):
    var = fm.bayesian_update(var, obs)
for v in var:
    np.testing.assert_allclose(v, _VARIANCE_FLOOR, atol=0.01)
```

## Next Steps


---

*Source: test_fisher.py:246 | Complexity: Intermediate | Last updated: 2026-05-05*