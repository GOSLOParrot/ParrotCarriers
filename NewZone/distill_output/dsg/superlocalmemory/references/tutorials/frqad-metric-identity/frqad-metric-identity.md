# How To: Frqad Metric Identity

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: d(x, x) = 0 when same embedding and same bit-width.

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

### Step 1: 'd(x, x) = 0 when same embedding and same bit-width.'

```python
'd(x, x) = 0 when same embedding and same bit-width.'
```

**Verification:**
```python
assert d == pytest.approx(0.0, abs=1e-10), f'd(x,x) must be 0 at bw={bw}, got {d}'
```

### Step 2: Assign mu = np.array(...)

```python
mu = np.array([0.5, -0.3, 0.8, 0.1])
```

### Step 3: Assign mu = value

```python
mu = mu / np.linalg.norm(mu)
```

### Step 4: Assign var = np.full(...)

```python
var = np.full(4, 0.5)
```

### Step 5: Assign d = frqad.distance(...)

```python
d = frqad.distance(mu, var, bw, mu, var, bw)
```

**Verification:**
```python
assert d == pytest.approx(0.0, abs=1e-10), f'd(x,x) must be 0 at bw={bw}, got {d}'
```


## Complete Example

```python
# Setup
# Fixtures: frqad

# Workflow
'd(x, x) = 0 when same embedding and same bit-width.'
mu = np.array([0.5, -0.3, 0.8, 0.1])
mu = mu / np.linalg.norm(mu)
var = np.full(4, 0.5)
for bw in (2, 4, 8, 32):
    d = frqad.distance(mu, var, bw, mu, var, bw)
    assert d == pytest.approx(0.0, abs=1e-10), f'd(x,x) must be 0 at bw={bw}, got {d}'
```

## Next Steps


---

*Source: test_fisher_quantized.py:261 | Complexity: Intermediate | Last updated: 2026-05-05*