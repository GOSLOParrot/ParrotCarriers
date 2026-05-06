# How To: Store Without Qjl

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: System works without QJL encoder (HR-07).

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
# Fixtures: test_db, polar_encoder, quant_config
```

## Step-by-Step Guide

### Step 1: 'System works without QJL encoder (HR-07).'

```python
'System works without QJL encoder (HR-07).'
```

**Verification:**
```python
assert result is True
```

### Step 2: Assign store_no_qjl = QuantizedEmbeddingStore(...)

```python
store_no_qjl = QuantizedEmbeddingStore(test_db, polar_encoder, None, quant_config)
```

**Verification:**
```python
assert loaded is not None
```

### Step 3: Assign v = _random_vec(...)

```python
v = _random_vec(768, seed=40)
```

**Verification:**
```python
assert loaded.qjl_bits is None
```

### Step 4: Assign result = store_no_qjl.compress_fact(...)

```python
result = store_no_qjl.compress_fact('f-noqjl', 'p1', v, target_bit_width=4)
```

**Verification:**
```python
assert result is True
```

### Step 5: Assign loaded = store_no_qjl.load(...)

```python
loaded = store_no_qjl.load('f-noqjl', 'p1')
```

**Verification:**
```python
assert loaded is not None
```


## Complete Example

```python
# Setup
# Fixtures: test_db, polar_encoder, quant_config

# Workflow
'System works without QJL encoder (HR-07).'
store_no_qjl = QuantizedEmbeddingStore(test_db, polar_encoder, None, quant_config)
v = _random_vec(768, seed=40)
result = store_no_qjl.compress_fact('f-noqjl', 'p1', v, target_bit_width=4)
assert result is True
loaded = store_no_qjl.load('f-noqjl', 'p1')
assert loaded is not None
assert loaded.qjl_bits is None
```

## Next Steps


---

*Source: test_quantized_store.py:250 | Complexity: Intermediate | Last updated: 2026-05-05*