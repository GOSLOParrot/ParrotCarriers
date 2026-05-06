# How To: Rotation Matrix Copy On Detect

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test 6: Copies polar_rotation_{d}.npy if turbo doesn't exist.

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

### Step 1: "Test 6: Copies polar_rotation_{d}.npy if turbo doesn't exist."

```python
"Test 6: Copies polar_rotation_{d}.npy if turbo doesn't exist."
```

**Verification:**
```python
assert not turbo_path.exists()
```

### Step 2: Assign slm_dir = value

```python
slm_dir = tmp_dir / '.superlocalmemory'
```

**Verification:**
```python
assert turbo_path.exists()
```

### Step 3: Call slm_dir.mkdir()

```python
slm_dir.mkdir()
```

### Step 4: Assign d = 32

```python
d = 32
```

### Step 5: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(42)
```

### Step 6: Assign H = rng.standard_normal(...)

```python
H = rng.standard_normal((d, d))
```

### Step 7: Assign unknown = np.linalg.qr(...)

```python
Q, R = np.linalg.qr(H)
```

### Step 8: Assign S_polar = value

```python
S_polar = Q @ np.diag(np.sign(np.diag(R)))
```

### Step 9: Assign polar_path = value

```python
polar_path = slm_dir / f'polar_rotation_{d}.npy'
```

### Step 10: Call np.save()

```python
np.save(str(polar_path), S_polar)
```

### Step 11: Assign turbo_path = value

```python
turbo_path = slm_dir / f'turbo_rotation_{d}.npy'
```

**Verification:**
```python
assert not turbo_path.exists()
```

### Step 12: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal(enc._S, S_polar)
```

### Step 13: Assign config = PolarQuantConfig(...)

```python
config = PolarQuantConfig(dimension=d, rotation_matrix_path='', seed=99, codebook_method='turbo')
```

### Step 14: Assign enc = TurboQuantEncoder(...)

```python
enc = TurboQuantEncoder(config)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_dir

# Workflow
"Test 6: Copies polar_rotation_{d}.npy if turbo doesn't exist."
import shutil
import tempfile
slm_dir = tmp_dir / '.superlocalmemory'
slm_dir.mkdir()
d = 32
rng = np.random.default_rng(42)
H = rng.standard_normal((d, d))
Q, R = np.linalg.qr(H)
S_polar = Q @ np.diag(np.sign(np.diag(R)))
polar_path = slm_dir / f'polar_rotation_{d}.npy'
np.save(str(polar_path), S_polar)
turbo_path = slm_dir / f'turbo_rotation_{d}.npy'
assert not turbo_path.exists()
import unittest.mock
with unittest.mock.patch('superlocalmemory.math.turbo_quant.Path.home', return_value=tmp_dir):
    config = PolarQuantConfig(dimension=d, rotation_matrix_path='', seed=99, codebook_method='turbo')
    enc = TurboQuantEncoder(config)
assert turbo_path.exists()
np.testing.assert_array_equal(enc._S, S_polar)
```

## Next Steps


---

*Source: test_turbo_quant.py:181 | Complexity: Advanced | Last updated: 2026-05-05*