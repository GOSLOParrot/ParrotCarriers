# How To: Precision Additive

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: 1/new = 1/old + 1/obs.

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`


## Step-by-Step Guide

### Step 1: '1/new = 1/old + 1/obs.'

```python
'1/new = 1/old + 1/obs.'
```

### Step 2: Assign fm = FisherRaoMetric(...)

```python
fm = FisherRaoMetric()
```

### Step 3: Assign old = value

```python
old = [1.0]
```

### Step 4: Assign obs = value

```python
obs = [1.0]
```

### Step 5: Assign new = fm.bayesian_update(...)

```python
new = fm.bayesian_update(old, obs)
```

### Step 6: Assign expected = value

```python
expected = 1.0 / (1.0 / 1.0 + 1.0 / 1.0)
```

### Step 7: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(new, [max(expected, _VARIANCE_FLOOR)], atol=1e-10)
```


## Complete Example

```python
# Workflow
'1/new = 1/old + 1/obs.'
fm = FisherRaoMetric()
old = [1.0]
obs = [1.0]
new = fm.bayesian_update(old, obs)
expected = 1.0 / (1.0 / 1.0 + 1.0 / 1.0)
np.testing.assert_allclose(new, [max(expected, _VARIANCE_FLOOR)], atol=1e-10)
```

## Next Steps


---

*Source: test_fisher.py:216 | Complexity: Intermediate | Last updated: 2026-05-05*