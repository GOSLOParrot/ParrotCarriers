# How To: Frqad Similarity In Unit Range

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Similarity is always in [0, 1]. No NaN.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`
- `superlocalmemory.math.fisher_quantized`

**Setup Required:**
```python
# Fixtures: frqad
```

## Step-by-Step Guide

### Step 1: 'Similarity is always in [0, 1]. No NaN.'

```python
'Similarity is always in [0, 1]. No NaN.'
```

**Verification:**
```python
assert not math.isnan(sim), 'Similarity must not be NaN'
```

### Step 2: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(123)
```

**Verification:**
```python
assert 0.0 <= sim <= 1.0, f'Similarity out of [0,1]: {sim}'
```

### Step 3: Assign dim = rng.integers(...)

```python
dim = rng.integers(4, 64)
```

### Step 4: Assign mu_a = rng.standard_normal(...)

```python
mu_a = rng.standard_normal(dim)
```

### Step 5: Assign mu_a = value

```python
mu_a = mu_a / np.linalg.norm(mu_a)
```

### Step 6: Assign var_a = np.clip(...)

```python
var_a = np.clip(rng.uniform(0.05, 2.0, size=dim), 0.05, 10.0)
```

### Step 7: Assign mu_b = rng.standard_normal(...)

```python
mu_b = rng.standard_normal(dim)
```

### Step 8: Assign mu_b = value

```python
mu_b = mu_b / np.linalg.norm(mu_b)
```

### Step 9: Assign var_b = np.clip(...)

```python
var_b = np.clip(rng.uniform(0.05, 2.0, size=dim), 0.05, 10.0)
```

### Step 10: Assign bw_a = rng.choice(...)

```python
bw_a = rng.choice([2, 4, 8, 32])
```

### Step 11: Assign bw_b = rng.choice(...)

```python
bw_b = rng.choice([2, 4, 8, 32])
```

### Step 12: Assign sim = frqad.similarity(...)

```python
sim = frqad.similarity(mu_a, var_a, int(bw_a), mu_b, var_b, int(bw_b))
```

**Verification:**
```python
assert not math.isnan(sim), 'Similarity must not be NaN'
```


## Complete Example

```python
# Setup
# Fixtures: frqad

# Workflow
'Similarity is always in [0, 1]. No NaN.'
rng = np.random.default_rng(123)
for _ in range(30):
    dim = rng.integers(4, 64)
    mu_a = rng.standard_normal(dim)
    mu_a = mu_a / np.linalg.norm(mu_a)
    var_a = np.clip(rng.uniform(0.05, 2.0, size=dim), 0.05, 10.0)
    mu_b = rng.standard_normal(dim)
    mu_b = mu_b / np.linalg.norm(mu_b)
    var_b = np.clip(rng.uniform(0.05, 2.0, size=dim), 0.05, 10.0)
    bw_a = rng.choice([2, 4, 8, 32])
    bw_b = rng.choice([2, 4, 8, 32])
    sim = frqad.similarity(mu_a, var_a, int(bw_a), mu_b, var_b, int(bw_b))
    assert not math.isnan(sim), 'Similarity must not be NaN'
    assert 0.0 <= sim <= 1.0, f'Similarity out of [0,1]: {sim}'
```

## Next Steps


---

*Source: test_fisher_quantized.py:301 | Complexity: Advanced | Last updated: 2026-05-05*