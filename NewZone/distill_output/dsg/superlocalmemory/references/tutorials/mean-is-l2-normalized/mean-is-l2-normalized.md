# How To: Mean Is L2 Normalized

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test mean is l2 normalized

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

### Step 2: Assign emb = value

```python
emb = [3.0, 4.0]
```

### Step 3: Assign unknown = fm.compute_params(...)

```python
mean, _ = fm.compute_params(emb)
```

### Step 4: Assign norm = math.sqrt(...)

```python
norm = math.sqrt(sum((m ** 2 for m in mean)))
```

### Step 5: Call np.testing.assert_allclose()

```python
np.testing.assert_allclose(norm, 1.0, atol=1e-10)
```


## Complete Example

```python
# Workflow
fm = FisherRaoMetric()
emb = [3.0, 4.0]
mean, _ = fm.compute_params(emb)
norm = math.sqrt(sum((m ** 2 for m in mean)))
np.testing.assert_allclose(norm, 1.0, atol=1e-10)
```

## Next Steps


---

*Source: test_fisher.py:66 | Complexity: Intermediate | Last updated: 2026-05-05*