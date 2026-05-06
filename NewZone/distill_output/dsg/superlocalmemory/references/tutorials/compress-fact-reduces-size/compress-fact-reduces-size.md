# How To: Compress Fact Reduces Size

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: compress_fact produces a stored polar embedding with < float32 size.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.math.polar_quant`
- `superlocalmemory.math.qjl`
- `superlocalmemory.storage.quantized_store`

**Setup Required:**
```python
# Fixtures: store
```

## Step-by-Step Guide

### Step 1: 'compress_fact produces a stored polar embedding with < float32 size.'

```python
'compress_fact produces a stored polar embedding with < float32 size.'
```

**Verification:**
```python
assert result is True
```

### Step 2: Assign v = _random_vec(...)

```python
v = _random_vec(768, seed=20)
```

**Verification:**
```python
assert loaded is not None
```

### Step 3: Assign float32_size = value

```python
float32_size = 768 * 4
```

**Verification:**
```python
assert len(loaded.angle_indices) < float32_size
```

### Step 4: Assign result = store.compress_fact(...)

```python
result = store.compress_fact('f-compress', 'p1', v, target_bit_width=4)
```

**Verification:**
```python
assert result is True
```

### Step 5: Assign loaded = store.load(...)

```python
loaded = store.load('f-compress', 'p1')
```

**Verification:**
```python
assert loaded is not None
```


## Complete Example

```python
# Setup
# Fixtures: store

# Workflow
'compress_fact produces a stored polar embedding with < float32 size.'
v = _random_vec(768, seed=20)
float32_size = 768 * 4
result = store.compress_fact('f-compress', 'p1', v, target_bit_width=4)
assert result is True
loaded = store.load('f-compress', 'p1')
assert loaded is not None
assert len(loaded.angle_indices) < float32_size
```

## Next Steps


---

*Source: test_quantized_store.py:208 | Complexity: Intermediate | Last updated: 2026-05-05*