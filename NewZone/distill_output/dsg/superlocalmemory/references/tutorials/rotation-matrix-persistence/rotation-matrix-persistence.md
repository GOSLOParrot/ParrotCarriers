# How To: Rotation Matrix Persistence

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test 5: Save + load gives same matrix.

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

### Step 1: 'Test 5: Save + load gives same matrix.'

```python
'Test 5: Save + load gives same matrix.'
```

### Step 2: Assign path = str(...)

```python
path = str(tmp_dir / 'persist_rot.npy')
```

### Step 3: Assign config = PolarQuantConfig(...)

```python
config = PolarQuantConfig(dimension=32, rotation_matrix_path=path, seed=42, codebook_method='turbo')
```

### Step 4: Assign enc1 = TurboQuantEncoder(...)

```python
enc1 = TurboQuantEncoder(config)
```

### Step 5: Assign enc2 = TurboQuantEncoder(...)

```python
enc2 = TurboQuantEncoder(config)
```

### Step 6: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal(enc1._S, enc2._S)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_dir

# Workflow
'Test 5: Save + load gives same matrix.'
path = str(tmp_dir / 'persist_rot.npy')
config = PolarQuantConfig(dimension=32, rotation_matrix_path=path, seed=42, codebook_method='turbo')
enc1 = TurboQuantEncoder(config)
enc2 = TurboQuantEncoder(config)
np.testing.assert_array_equal(enc1._S, enc2._S)
```

## Next Steps


---

*Source: test_turbo_quant.py:159 | Complexity: Intermediate | Last updated: 2026-05-05*