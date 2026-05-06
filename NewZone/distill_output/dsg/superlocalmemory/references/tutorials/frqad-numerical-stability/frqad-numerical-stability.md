# How To: Frqad Numerical Stability

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: No NaN for extreme but valid variance values.

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

### Step 1: 'No NaN for extreme but valid variance values.'

```python
'No NaN for extreme but valid variance values.'
```

**Verification:**
```python
assert math.isfinite(d), f'Distance must be finite, got {d}'
```

### Step 2: Assign mu = np.array(...)

```python
mu = np.array([0.7, -0.7])
```

**Verification:**
```python
assert math.isfinite(d2), f'Distance must be finite, got {d2}'
```

### Step 3: Assign mu = value

```python
mu = mu / np.linalg.norm(mu)
```

### Step 4: Assign var_tiny = np.full(...)

```python
var_tiny = np.full(2, 0.05)
```

### Step 5: Assign d = frqad.distance(...)

```python
d = frqad.distance(mu, var_tiny, 2, mu * 1.01, var_tiny, 2)
```

**Verification:**
```python
assert math.isfinite(d), f'Distance must be finite, got {d}'
```

### Step 6: Assign var_large = np.full(...)

```python
var_large = np.full(2, 9.9)
```

### Step 7: Assign d2 = frqad.distance(...)

```python
d2 = frqad.distance(mu, var_large, 2, -mu, var_large, 2)
```

**Verification:**
```python
assert math.isfinite(d2), f'Distance must be finite, got {d2}'
```


## Complete Example

```python
# Setup
# Fixtures: frqad

# Workflow
'No NaN for extreme but valid variance values.'
mu = np.array([0.7, -0.7])
mu = mu / np.linalg.norm(mu)
var_tiny = np.full(2, 0.05)
d = frqad.distance(mu, var_tiny, 2, mu * 1.01, var_tiny, 2)
assert math.isfinite(d), f'Distance must be finite, got {d}'
var_large = np.full(2, 9.9)
d2 = frqad.distance(mu, var_large, 2, -mu, var_large, 2)
assert math.isfinite(d2), f'Distance must be finite, got {d2}'
```

## Next Steps


---

*Source: test_fisher_quantized.py:381 | Complexity: Intermediate | Last updated: 2026-05-05*