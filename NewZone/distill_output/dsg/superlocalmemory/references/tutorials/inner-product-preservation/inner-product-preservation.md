# How To: Inner Product Preservation

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test 12: |<x,y> - <Q(x),Q(y)>| small at 4-bit.

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

### Step 1: 'Test 12: |<x,y> - <Q(x),Q(y)>| small at 4-bit.'

```python
'Test 12: |<x,y> - <Q(x),Q(y)>| small at 4-bit.'
```

**Verification:**
```python
assert avg_error < 0.05, f'Avg IP error={avg_error:.6f}'
```

### Step 2: Assign errors = value

```python
errors = []
```

### Step 3: Assign avg_error = value

```python
avg_error = sum(errors) / len(errors)
```

**Verification:**
```python
assert avg_error < 0.05, f'Avg IP error={avg_error:.6f}'
```

### Step 4: Assign u = _random_unit_vec(...)

```python
u = _random_unit_vec(768, seed=seed)
```

### Step 5: Assign v = _random_unit_vec(...)

```python
v = _random_unit_vec(768, seed=seed + 1000)
```

### Step 6: Assign ip_exact = float(...)

```python
ip_exact = float(np.dot(u, v))
```

### Step 7: Assign qu = encoder_768d.encode(...)

```python
qu = encoder_768d.encode(u, bit_width=4)
```

### Step 8: Assign qv = encoder_768d.encode(...)

```python
qv = encoder_768d.encode(v, bit_width=4)
```

### Step 9: Assign u_hat = encoder_768d.decode(...)

```python
u_hat = encoder_768d.decode(qu)
```

### Step 10: Assign v_hat = encoder_768d.decode(...)

```python
v_hat = encoder_768d.decode(qv)
```

### Step 11: Assign ip_quant = float(...)

```python
ip_quant = float(np.dot(u_hat, v_hat))
```

### Step 12: Call errors.append()

```python
errors.append(abs(ip_exact - ip_quant))
```


## Complete Example

```python
# Setup
# Fixtures: encoder_768d

# Workflow
'Test 12: |<x,y> - <Q(x),Q(y)>| small at 4-bit.'
errors = []
for seed in range(10):
    u = _random_unit_vec(768, seed=seed)
    v = _random_unit_vec(768, seed=seed + 1000)
    ip_exact = float(np.dot(u, v))
    qu = encoder_768d.encode(u, bit_width=4)
    qv = encoder_768d.encode(v, bit_width=4)
    u_hat = encoder_768d.decode(qu)
    v_hat = encoder_768d.decode(qv)
    ip_quant = float(np.dot(u_hat, v_hat))
    errors.append(abs(ip_exact - ip_quant))
avg_error = sum(errors) / len(errors)
assert avg_error < 0.05, f'Avg IP error={avg_error:.6f}'
```

## Next Steps


---

*Source: test_turbo_quant.py:322 | Complexity: Advanced | Last updated: 2026-05-05*