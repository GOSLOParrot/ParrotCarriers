# How To: Identical Gives One

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test identical gives one

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

### Step 2: Assign m = value

```python
m = [0.3, 0.4]
```

### Step 3: Assign v = value

```python
v = [1.0, 1.0]
```

### Step 4: Assign s = fm.similarity(...)

```python
s = fm.similarity(m, v, m, v)
```

### Step 5: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(s, 1.0, atol=1e-10)
```


## Complete Example

```python
# Workflow
fm = FisherRaoMetric()
m = [0.3, 0.4]
v = [1.0, 1.0]
s = fm.similarity(m, v, m, v)
np.testing.assert_allclose(s, 1.0, atol=1e-10)
```

## Next Steps


---

*Source: test_fisher.py:170 | Complexity: Intermediate | Last updated: 2026-05-05*