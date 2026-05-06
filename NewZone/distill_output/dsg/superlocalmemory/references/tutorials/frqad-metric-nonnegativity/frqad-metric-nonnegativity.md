# How To: Frqad Metric Nonnegativity

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: d >= 0 for random embedding pairs at various bit-widths.

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

### Step 1: 'd >= 0 for random embedding pairs at various bit-widths.'

```python
'd >= 0 for random embedding pairs at various bit-widths.'
```

**Verification:**
```python
assert d >= 0.0, f'Distance must be non-negative, got {d}'
```

### Step 2: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(99)
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
var_a = np.clip(rng.uniform(0.1, 1.5, size=dim), 0.05, 10.0)
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
var_b = np.clip(rng.uniform(0.1, 1.5, size=dim), 0.05, 10.0)
```

### Step 10: Assign bw_a = rng.choice(...)

```python
bw_a = rng.choice([2, 4, 8, 32])
```

### Step 11: Assign bw_b = rng.choice(...)

```python
bw_b = rng.choice([2, 4, 8, 32])
```

### Step 12: Assign d = frqad.distance(...)

```python
d = frqad.distance(mu_a, var_a, int(bw_a), mu_b, var_b, int(bw_b))
```

**Verification:**
```python
assert d >= 0.0, f'Distance must be non-negative, got {d}'
```


## Complete Example

```python
# Setup
# Fixtures: frqad

# Workflow
'd >= 0 for random embedding pairs at various bit-widths.'
rng = np.random.default_rng(99)
for _ in range(20):
    dim = rng.integers(4, 64)
    mu_a = rng.standard_normal(dim)
    mu_a = mu_a / np.linalg.norm(mu_a)
    var_a = np.clip(rng.uniform(0.1, 1.5, size=dim), 0.05, 10.0)
    mu_b = rng.standard_normal(dim)
    mu_b = mu_b / np.linalg.norm(mu_b)
    var_b = np.clip(rng.uniform(0.1, 1.5, size=dim), 0.05, 10.0)
    bw_a = rng.choice([2, 4, 8, 32])
    bw_b = rng.choice([2, 4, 8, 32])
    d = frqad.distance(mu_a, var_a, int(bw_a), mu_b, var_b, int(bw_b))
    assert d >= 0.0, f'Distance must be non-negative, got {d}'
```

## Next Steps


---

*Source: test_fisher_quantized.py:234 | Complexity: Advanced | Last updated: 2026-05-05*