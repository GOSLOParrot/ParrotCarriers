# How To: Qjl Correction Improves Polar

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: polar + QJL is closer to true similarity than polar alone.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.qjl`
- `superlocalmemory.math.polar_quant`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'polar + QJL is closer to true similarity than polar alone.'

```python
'polar + QJL is closer to true similarity than polar alone.'
```

**Verification:**
```python
assert abs(correction) > 0.0, 'QJL correction should be non-zero'
```

### Step 2: Assign d = 768

```python
d = 768
```

### Step 3: Assign polar_config = PolarQuantConfig(...)

```python
polar_config = PolarQuantConfig(dimension=d, rotation_matrix_path=str(tmp_path / 'polar_rot.npy'), seed=42)
```

### Step 4: Assign qjl_config = QJLConfig(...)

```python
qjl_config = QJLConfig(projection_dim=128, seed=43)
```

### Step 5: Assign polar = PolarQuantEncoder(...)

```python
polar = PolarQuantEncoder(polar_config)
```

### Step 6: Assign qjl = QJLEncoder(...)

```python
qjl = QJLEncoder(qjl_config)
```

### Step 7: Assign query = _random_vec(...)

```python
query = _random_vec(d, seed=200)
```

### Step 8: Assign target = _random_vec(...)

```python
target = _random_vec(d, seed=201)
```

### Step 9: Assign true_sim = float(...)

```python
true_sim = float(np.dot(query, target) / (np.linalg.norm(query) * np.linalg.norm(target)))
```

### Step 10: Assign qe = polar.encode(...)

```python
qe = polar.encode(target, bit_width=4)
```

### Step 11: Assign polar_sim = polar.approximate_similarity(...)

```python
polar_sim = polar.approximate_similarity(query, qe)
```

### Step 12: Assign decoded = polar.decode(...)

```python
decoded = polar.decode(qe)
```

### Step 13: Assign residual = value

```python
residual = target - decoded
```

### Step 14: Assign qjl_bits = qjl.encode_residual(...)

```python
qjl_bits = qjl.encode_residual(residual)
```

### Step 15: Assign correction = qjl.estimate_correction(...)

```python
correction = qjl.estimate_correction(query, qjl_bits)
```

### Step 16: Assign corrected_sim = value

```python
corrected_sim = polar_sim + correction
```

### Step 17: Assign polar_error = abs(...)

```python
polar_error = abs(true_sim - polar_sim)
```

### Step 18: Assign corrected_error = abs(...)

```python
corrected_error = abs(true_sim - corrected_sim)
```

**Verification:**
```python
assert abs(correction) > 0.0, 'QJL correction should be non-zero'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'polar + QJL is closer to true similarity than polar alone.'
from superlocalmemory.math.polar_quant import PolarQuantEncoder
d = 768
polar_config = PolarQuantConfig(dimension=d, rotation_matrix_path=str(tmp_path / 'polar_rot.npy'), seed=42)
qjl_config = QJLConfig(projection_dim=128, seed=43)
polar = PolarQuantEncoder(polar_config)
qjl = QJLEncoder(qjl_config)
query = _random_vec(d, seed=200)
target = _random_vec(d, seed=201)
true_sim = float(np.dot(query, target) / (np.linalg.norm(query) * np.linalg.norm(target)))
qe = polar.encode(target, bit_width=4)
polar_sim = polar.approximate_similarity(query, qe)
decoded = polar.decode(qe)
residual = target - decoded
qjl_bits = qjl.encode_residual(residual)
correction = qjl.estimate_correction(query, qjl_bits)
corrected_sim = polar_sim + correction
polar_error = abs(true_sim - polar_sim)
corrected_error = abs(true_sim - corrected_sim)
assert abs(correction) > 0.0, 'QJL correction should be non-zero'
```

## Next Steps


---

*Source: test_qjl.py:93 | Complexity: Advanced | Last updated: 2026-05-05*