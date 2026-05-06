# How To: Distance Symmetry

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test distance symmetry

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

### Step 2: Assign ma = value

```python
ma = [0.1, 0.2, 0.3]
```

### Step 3: Assign va = value

```python
va = [0.5, 0.5, 0.5]
```

### Step 4: Assign mb = value

```python
mb = [0.4, 0.5, 0.6]
```

### Step 5: Assign vb = value

```python
vb = [1.0, 1.0, 1.0]
```

### Step 6: Assign d1 = fm.distance(...)

```python
d1 = fm.distance(ma, va, mb, vb)
```

### Step 7: Assign d2 = fm.distance(...)

```python
d2 = fm.distance(mb, vb, ma, va)
```

### Step 8: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(d1, d2, atol=1e-10)
```


## Complete Example

```python
# Workflow
fm = FisherRaoMetric()
ma = [0.1, 0.2, 0.3]
va = [0.5, 0.5, 0.5]
mb = [0.4, 0.5, 0.6]
vb = [1.0, 1.0, 1.0]
d1 = fm.distance(ma, va, mb, vb)
d2 = fm.distance(mb, vb, ma, va)
np.testing.assert_allclose(d1, d2, atol=1e-10)
```

## Next Steps


---

*Source: test_fisher.py:125 | Complexity: Advanced | Last updated: 2026-05-05*