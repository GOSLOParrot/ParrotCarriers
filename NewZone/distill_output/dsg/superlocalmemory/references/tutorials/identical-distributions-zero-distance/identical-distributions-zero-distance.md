# How To: Identical Distributions Zero Distance

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test identical distributions zero distance

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`


## Step-by-Step Guide

### Step 1: Assign fm = FisherRaoMetric(...)

```python
fm = FisherRaoMetric()
```

### Step 2: Assign mean = value

```python
mean = [0.5, -0.3, 0.7]
```

### Step 3: Assign var = value

```python
var = [1.0, 1.0, 1.0]
```

### Step 4: Assign d = fm.distance(...)

```python
d = fm.distance(mean, var, mean, var)
```

### Step 5: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(d, 0.0, atol=1e-10)
```


## Complete Example

```python
# Workflow
fm = FisherRaoMetric()
mean = [0.5, -0.3, 0.7]
var = [1.0, 1.0, 1.0]
d = fm.distance(mean, var, mean, var)
np.testing.assert_allclose(d, 0.0, atol=1e-10)
```

## Next Steps


---

*Source: test_fisher.py:108 | Complexity: Intermediate | Last updated: 2026-05-05*