# How To: Encode Decode Roundtrip 4Bit

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test 2: 4-bit avg MSE < 0.02 (paper: 0.009).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `sys`
- `pathlib`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.turbo_quant`
- `shutil`
- `tempfile`
- `unittest.mock`
- `superlocalmemory.math.turbo_quant`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.polar_quant`

**Setup Required:**
```python
# Fixtures: encoder_768d
```

## Step-by-Step Guide

### Step 1: 'Test 2: 4-bit avg MSE < 0.02 (paper: 0.009).'

```python
'Test 2: 4-bit avg MSE < 0.02 (paper: 0.009).'
```

**Verification:**
```python
assert avg_mse < 0.02, f'4-bit avg MSE={avg_mse:.6f}, expected < 0.02'
```

### Step 2: Assign mses = value

```python
mses = []
```

### Step 3: Assign avg_mse = value

```python
avg_mse = sum(mses) / len(mses)
```

**Verification:**
```python
assert avg_mse < 0.02, f'4-bit avg MSE={avg_mse:.6f}, expected < 0.02'
```

### Step 4: Assign v = _random_unit_vec(...)

```python
v = _random_unit_vec(768, seed=seed + 100)
```

### Step 5: Assign qe = encoder_768d.encode(...)

```python
qe = encoder_768d.encode(v, bit_width=4)
```

### Step 6: Assign decoded = encoder_768d.decode(...)

```python
decoded = encoder_768d.decode(qe)
```

### Step 7: Call mses.append()

```python
mses.append(_mse(v, decoded))
```


## Complete Example

```python
# Setup
# Fixtures: encoder_768d

# Workflow
'Test 2: 4-bit avg MSE < 0.02 (paper: 0.009).'
mses = []
for seed in range(20):
    v = _random_unit_vec(768, seed=seed + 100)
    qe = encoder_768d.encode(v, bit_width=4)
    decoded = encoder_768d.decode(qe)
    mses.append(_mse(v, decoded))
avg_mse = sum(mses) / len(mses)
assert avg_mse < 0.02, f'4-bit avg MSE={avg_mse:.6f}, expected < 0.02'
```

## Next Steps


---

*Source: test_turbo_quant.py:115 | Complexity: Intermediate | Last updated: 2026-05-05*