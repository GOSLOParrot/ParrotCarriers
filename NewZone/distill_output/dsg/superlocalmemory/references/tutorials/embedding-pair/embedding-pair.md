# How To: Embedding Pair

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: Two distinct embedding pairs (mu, var) for distance tests.

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`
- `superlocalmemory.math.fisher_quantized`


## Step-by-Step Guide

### Step 1: 'Two distinct embedding pairs (mu, var) for distance tests.'

```python
'Two distinct embedding pairs (mu, var) for distance tests.'
```

### Step 2: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(42)
```

### Step 3: Assign mu_a = rng.standard_normal(...)

```python
mu_a = rng.standard_normal(16)
```

### Step 4: Assign mu_a = value

```python
mu_a = mu_a / np.linalg.norm(mu_a)
```

### Step 5: Assign var_a = np.full(...)

```python
var_a = np.full(16, 0.5)
```

### Step 6: Assign mu_b = rng.standard_normal(...)

```python
mu_b = rng.standard_normal(16)
```

### Step 7: Assign mu_b = value

```python
mu_b = mu_b / np.linalg.norm(mu_b)
```

### Step 8: Assign var_b = np.full(...)

```python
var_b = np.full(16, 0.5)
```


## Complete Example

```python
# Workflow
'Two distinct embedding pairs (mu, var) for distance tests.'
rng = np.random.default_rng(42)
mu_a = rng.standard_normal(16)
mu_a = mu_a / np.linalg.norm(mu_a)
var_a = np.full(16, 0.5)
mu_b = rng.standard_normal(16)
mu_b = mu_b / np.linalg.norm(mu_b)
var_b = np.full(16, 0.5)
return (mu_a, var_a, mu_b, var_b)
```

## Next Steps


---

*Source: test_fisher_quantized.py:71 | Complexity: Advanced | Last updated: 2026-05-05*