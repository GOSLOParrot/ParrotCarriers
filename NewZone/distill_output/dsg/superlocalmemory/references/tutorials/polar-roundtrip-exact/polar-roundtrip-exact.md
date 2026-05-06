# How To: Polar Roundtrip Exact

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Coordinate transform (no quantization) preserves vector.

Tests: v -> rotation -> polar -> Cartesian -> inverse rotation
Should get cosine > 0.9999 (only float rounding).

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
# Fixtures: encoder_768d
```

## Step-by-Step Guide

### Step 1: 'Coordinate transform (no quantization) preserves vector.\n\n    Tests: v -> rotation -> polar -> Cartesian -> inverse rotation\n    Should get cosine > 0.9999 (only float rounding).\n    '

```python
'Coordinate transform (no quantization) preserves vector.\n\n    Tests: v -> rotation -> polar -> Cartesian -> inverse rotation\n    Should get cosine > 0.9999 (only float rounding).\n    '
```

**Verification:**
```python
assert cos_sim > 0.9999, f'Exact polar roundtrip cosine={cos_sim:.6f}, expected > 0.9999'
```

### Step 2: Assign v = _random_vec(...)

```python
v = _random_vec(768, seed=42)
```

### Step 3: Assign v_rot = value

```python
v_rot = encoder_768d._S @ v
```

### Step 4: Assign r = float(...)

```python
r = float(np.linalg.norm(v_rot))
```

### Step 5: Assign v_unit = value

```python
v_unit = v_rot / r
```

### Step 6: Assign d = len(...)

```python
d = len(v_unit)
```

### Step 7: Assign angles = np.empty(...)

```python
angles = np.empty(d - 1)
```

### Step 8: Assign v_reconstructed = np.empty(...)

```python
v_reconstructed = np.empty(d)
```

### Step 9: Assign sin_product = 1.0

```python
sin_product = 1.0
```

### Step 10: Assign unknown = sin_product

```python
v_reconstructed[d - 1] = sin_product
```

### Step 11: Assign v_final = value

```python
v_final = encoder_768d._S.T @ (v_reconstructed * r)
```

### Step 12: Assign cos_sim = float(...)

```python
cos_sim = float(np.dot(v, v_final) / (np.linalg.norm(v) * np.linalg.norm(v_final)))
```

**Verification:**
```python
assert cos_sim > 0.9999, f'Exact polar roundtrip cosine={cos_sim:.6f}, expected > 0.9999'
```

### Step 13: Assign remaining = np.linalg.norm(...)

```python
remaining = np.linalg.norm(v_unit[i:])
```

### Step 14: Assign unknown = math.acos(...)

```python
angles[i] = math.acos(np.clip(v_unit[i] / remaining, -1.0, 1.0))
```

### Step 15: Assign unknown = value

```python
v_reconstructed[i] = math.cos(angles[i]) * sin_product
```

### Step 16: Assign unknown = value

```python
angles[i:] = math.pi / 2
```


## Complete Example

```python
# Setup
# Fixtures: encoder_768d

# Workflow
'Coordinate transform (no quantization) preserves vector.\n\n    Tests: v -> rotation -> polar -> Cartesian -> inverse rotation\n    Should get cosine > 0.9999 (only float rounding).\n    '
v = _random_vec(768, seed=42)
v_rot = encoder_768d._S @ v
r = float(np.linalg.norm(v_rot))
v_unit = v_rot / r
d = len(v_unit)
angles = np.empty(d - 1)
for i in range(d - 1):
    remaining = np.linalg.norm(v_unit[i:])
    if remaining < 1e-12:
        angles[i:] = math.pi / 2
        break
    angles[i] = math.acos(np.clip(v_unit[i] / remaining, -1.0, 1.0))
v_reconstructed = np.empty(d)
sin_product = 1.0
for i in range(d - 1):
    v_reconstructed[i] = math.cos(angles[i]) * sin_product
    sin_product *= math.sin(angles[i])
v_reconstructed[d - 1] = sin_product
v_final = encoder_768d._S.T @ (v_reconstructed * r)
cos_sim = float(np.dot(v, v_final) / (np.linalg.norm(v) * np.linalg.norm(v_final)))
assert cos_sim > 0.9999, f'Exact polar roundtrip cosine={cos_sim:.6f}, expected > 0.9999'
```

## Next Steps


---

*Source: test_polar_quant.py:216 | Complexity: Advanced | Last updated: 2026-05-05*