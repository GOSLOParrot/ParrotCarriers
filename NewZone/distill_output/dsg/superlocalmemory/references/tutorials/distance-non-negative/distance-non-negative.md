# How To: Distance Non Negative

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test distance non negative

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

**Verification:**
```python
assert fm.distance(ma, va, mb, vb) >= 0.0
```

### Step 2: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(7)
```

### Step 3: Assign ma = rng.standard_normal.tolist(...)

```python
ma = rng.standard_normal(10).tolist()
```

### Step 4: Assign mb = rng.standard_normal.tolist(...)

```python
mb = rng.standard_normal(10).tolist()
```

### Step 5: Assign va = rng.uniform.tolist(...)

```python
va = rng.uniform(0.3, 2.0, 10).tolist()
```

### Step 6: Assign vb = rng.uniform.tolist(...)

```python
vb = rng.uniform(0.3, 2.0, 10).tolist()
```

**Verification:**
```python
assert fm.distance(ma, va, mb, vb) >= 0.0
```


## Complete Example

```python
# Workflow
fm = FisherRaoMetric()
rng = np.random.default_rng(7)
for _ in range(20):
    ma = rng.standard_normal(10).tolist()
    mb = rng.standard_normal(10).tolist()
    va = rng.uniform(0.3, 2.0, 10).tolist()
    vb = rng.uniform(0.3, 2.0, 10).tolist()
    assert fm.distance(ma, va, mb, vb) >= 0.0
```

## Next Steps


---

*Source: test_fisher.py:115 | Complexity: Intermediate | Last updated: 2026-05-05*