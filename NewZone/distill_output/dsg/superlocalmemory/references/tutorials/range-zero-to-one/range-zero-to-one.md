# How To: Range Zero To One

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test range zero to one

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
assert 0.0 <= s <= 1.0
```

### Step 2: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(42)
```

### Step 3: Assign ma = rng.standard_normal.tolist(...)

```python
ma = rng.standard_normal(8).tolist()
```

### Step 4: Assign mb = rng.standard_normal.tolist(...)

```python
mb = rng.standard_normal(8).tolist()
```

### Step 5: Assign va = rng.uniform.tolist(...)

```python
va = rng.uniform(0.3, 2.0, 8).tolist()
```

### Step 6: Assign vb = rng.uniform.tolist(...)

```python
vb = rng.uniform(0.3, 2.0, 8).tolist()
```

### Step 7: Assign s = fm.similarity(...)

```python
s = fm.similarity(ma, va, mb, vb)
```

**Verification:**
```python
assert 0.0 <= s <= 1.0
```


## Complete Example

```python
# Workflow
fm = FisherRaoMetric()
rng = np.random.default_rng(42)
for _ in range(20):
    ma = rng.standard_normal(8).tolist()
    mb = rng.standard_normal(8).tolist()
    va = rng.uniform(0.3, 2.0, 8).tolist()
    vb = rng.uniform(0.3, 2.0, 8).tolist()
    s = fm.similarity(ma, va, mb, vb)
    assert 0.0 <= s <= 1.0
```

## Next Steps


---

*Source: test_fisher.py:177 | Complexity: Intermediate | Last updated: 2026-05-05*