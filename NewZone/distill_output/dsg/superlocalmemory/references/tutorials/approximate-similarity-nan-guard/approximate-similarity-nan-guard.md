# How To: Approximate Similarity Nan Guard

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: NaN/Inf in similarity computation returns 0.0.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `tempfile`
- `pathlib`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.polar_quant`
- `unittest.mock`

**Setup Required:**
```python
# Fixtures: encoder_16d
```

## Step-by-Step Guide

### Step 1: 'NaN/Inf in similarity computation returns 0.0.'

```python
'NaN/Inf in similarity computation returns 0.0.'
```

**Verification:**
```python
assert sim == 0.0
```

### Step 2: Assign v = _random_vec(...)

```python
v = _random_vec(16, seed=10)
```

### Step 3: Assign qe = encoder_16d.encode(...)

```python
qe = encoder_16d.encode(v, bit_width=8)
```

### Step 4: Assign nan_vec = np.full(...)

```python
nan_vec = np.full(16, float('nan'))
```

**Verification:**
```python
assert sim == 0.0
```

### Step 5: Assign sim = encoder_16d.approximate_similarity(...)

```python
sim = encoder_16d.approximate_similarity(v, qe)
```


## Complete Example

```python
# Setup
# Fixtures: encoder_16d

# Workflow
'NaN/Inf in similarity computation returns 0.0.'
import unittest.mock
v = _random_vec(16, seed=10)
qe = encoder_16d.encode(v, bit_width=8)
nan_vec = np.full(16, float('nan'))
with unittest.mock.patch.object(PolarQuantEncoder, 'decode', return_value=nan_vec):
    sim = encoder_16d.approximate_similarity(v, qe)
assert sim == 0.0
```

## Next Steps


---

*Source: test_polar_quant.py:376 | Complexity: Intermediate | Last updated: 2026-05-05*