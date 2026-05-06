# How To: Quantization Variance Increases With Lower Bw

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test quantization variance increases with lower bw

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

### Step 1: Assign base_var = np.full(...)

```python
base_var = np.full(16, 0.5)
```

**Verification:**
```python
assert np.all(var_8 >= var_32)
```

### Step 2: Assign var_32 = frqad.quantization_variance(...)

```python
var_32 = frqad.quantization_variance(base_var, 32)
```

**Verification:**
```python
assert np.all(var_4 >= var_8)
```

### Step 3: Assign var_8 = frqad.quantization_variance(...)

```python
var_8 = frqad.quantization_variance(base_var, 8)
```

**Verification:**
```python
assert np.all(var_2 >= var_4)
```

### Step 4: Assign var_4 = frqad.quantization_variance(...)

```python
var_4 = frqad.quantization_variance(base_var, 4)
```

### Step 5: Assign var_2 = frqad.quantization_variance(...)

```python
var_2 = frqad.quantization_variance(base_var, 2)
```

### Step 6: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal(var_32, base_var)
```

**Verification:**
```python
assert np.all(var_8 >= var_32)
```


## Complete Example

```python
# Setup
# Fixtures: frqad

# Workflow
base_var = np.full(16, 0.5)
var_32 = frqad.quantization_variance(base_var, 32)
var_8 = frqad.quantization_variance(base_var, 8)
var_4 = frqad.quantization_variance(base_var, 4)
var_2 = frqad.quantization_variance(base_var, 2)
np.testing.assert_array_equal(var_32, base_var)
assert np.all(var_8 >= var_32)
assert np.all(var_4 >= var_8)
assert np.all(var_2 >= var_4)
```

## Next Steps


---

*Source: test_fisher_quantized.py:137 | Complexity: Intermediate | Last updated: 2026-05-05*