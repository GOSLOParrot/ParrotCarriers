# How To: Unit Vector Encode Decode

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test 11: Specific known axis-aligned vector.

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
# Fixtures: encoder_16d
```

## Step-by-Step Guide

### Step 1: 'Test 11: Specific known axis-aligned vector.'

```python
'Test 11: Specific known axis-aligned vector.'
```

**Verification:**
```python
assert cos > 0.9, f'Axis-aligned cosine={cos:.4f}'
```

### Step 2: Assign v = np.zeros(...)

```python
v = np.zeros(16)
```

### Step 3: Assign unknown = 1.0

```python
v[0] = 1.0
```

### Step 4: Assign qe = encoder_16d.encode(...)

```python
qe = encoder_16d.encode(v, bit_width=8)
```

### Step 5: Assign decoded = encoder_16d.decode(...)

```python
decoded = encoder_16d.decode(qe)
```

### Step 6: Assign cos = _cosine_sim(...)

```python
cos = _cosine_sim(v, decoded)
```

**Verification:**
```python
assert cos > 0.9, f'Axis-aligned cosine={cos:.4f}'
```


## Complete Example

```python
# Setup
# Fixtures: encoder_16d

# Workflow
'Test 11: Specific known axis-aligned vector.'
v = np.zeros(16)
v[0] = 1.0
qe = encoder_16d.encode(v, bit_width=8)
decoded = encoder_16d.decode(qe)
cos = _cosine_sim(v, decoded)
assert cos > 0.9, f'Axis-aligned cosine={cos:.4f}'
```

## Next Steps


---

*Source: test_turbo_quant.py:302 | Complexity: Intermediate | Last updated: 2026-05-05*