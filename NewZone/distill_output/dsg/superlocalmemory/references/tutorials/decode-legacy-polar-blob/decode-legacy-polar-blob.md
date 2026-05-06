# How To: Decode Legacy Polar Blob

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test 17: BLOB without TQ prefix decodes via polar path.

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
# Fixtures: tmp_dir
```

## Step-by-Step Guide

### Step 1: 'Test 17: BLOB without TQ prefix decodes via polar path.'

```python
'Test 17: BLOB without TQ prefix decodes via polar path.'
```

**Verification:**
```python
assert polar_qe.angle_indices[:2] != TQ_MAGIC
```

### Step 2: Assign d = 16

```python
d = 16
```

**Verification:**
```python
assert decoded.shape == (d,)
```

### Step 3: Assign config = PolarQuantConfig(...)

```python
config = PolarQuantConfig(dimension=d, rotation_matrix_path=str(tmp_dir / 'legacy_rot.npy'), seed=42, codebook_method='polar_legacy')
```

**Verification:**
```python
assert np.all(np.isfinite(decoded))
```

### Step 4: Assign polar_enc = PolarQuantEncoder(...)

```python
polar_enc = PolarQuantEncoder(config)
```

### Step 5: Assign v = _random_unit_vec(...)

```python
v = _random_unit_vec(d, seed=5)
```

### Step 6: Assign polar_qe = polar_enc.encode(...)

```python
polar_qe = polar_enc.encode(v, bit_width=4)
```

**Verification:**
```python
assert polar_qe.angle_indices[:2] != TQ_MAGIC
```

### Step 7: Assign turbo_config = PolarQuantConfig(...)

```python
turbo_config = PolarQuantConfig(dimension=d, rotation_matrix_path=str(tmp_dir / 'legacy_rot.npy'), seed=42, codebook_method='turbo')
```

### Step 8: Assign turbo_enc = TurboQuantEncoder(...)

```python
turbo_enc = TurboQuantEncoder(turbo_config)
```

### Step 9: Assign turbo_result = TurboQuantResult(...)

```python
turbo_result = TurboQuantResult(radius=polar_qe.radius, indices=polar_qe.angle_indices, bit_width=polar_qe.bit_width)
```

### Step 10: Assign decoded = turbo_enc.decode(...)

```python
decoded = turbo_enc.decode(turbo_result)
```

**Verification:**
```python
assert decoded.shape == (d,)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_dir

# Workflow
'Test 17: BLOB without TQ prefix decodes via polar path.'
from superlocalmemory.math.polar_quant import PolarQuantEncoder, _cartesian_to_polar_angles, _polar_to_cartesian
d = 16
config = PolarQuantConfig(dimension=d, rotation_matrix_path=str(tmp_dir / 'legacy_rot.npy'), seed=42, codebook_method='polar_legacy')
polar_enc = PolarQuantEncoder(config)
v = _random_unit_vec(d, seed=5)
polar_qe = polar_enc.encode(v, bit_width=4)
assert polar_qe.angle_indices[:2] != TQ_MAGIC
turbo_config = PolarQuantConfig(dimension=d, rotation_matrix_path=str(tmp_dir / 'legacy_rot.npy'), seed=42, codebook_method='turbo')
turbo_enc = TurboQuantEncoder(turbo_config)
turbo_result = TurboQuantResult(radius=polar_qe.radius, indices=polar_qe.angle_indices, bit_width=polar_qe.bit_width)
decoded = turbo_enc.decode(turbo_result)
assert decoded.shape == (d,)
assert np.all(np.isfinite(decoded))
```

## Next Steps


---

*Source: test_turbo_quant.py:422 | Complexity: Advanced | Last updated: 2026-05-05*