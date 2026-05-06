# How To: Polar Penalty Applied

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Polar results are penalized by config.polar_search_penalty.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.quantization_aware_search`

**Setup Required:**
```python
# Fixtures: mock_vector_store, mock_quantized_store
```

## Step-by-Step Guide

### Step 1: 'Polar results are penalized by config.polar_search_penalty.'

```python
'Polar results are penalized by config.polar_search_penalty.'
```

**Verification:**
```python
assert len(results) == 1
```

### Step 2: Assign mock_vector_store.search.return_value = value

```python
mock_vector_store.search.return_value = []
```

**Verification:**
```python
assert results[0][0] == 'f-polar'
```

### Step 3: Assign mock_vector_store.search_int8.return_value = value

```python
mock_vector_store.search_int8.return_value = []
```

**Verification:**
```python
assert results[0][1] == pytest.approx(0.95, abs=0.001)
```

### Step 4: Assign mock_quantized_store.search.return_value = value

```python
mock_quantized_store.search.return_value = [('f-polar', 1.0)]
```

### Step 5: Assign config = QuantizationConfig(...)

```python
config = QuantizationConfig(polar_search_penalty=0.95)
```

### Step 6: Assign searcher = QuantizationAwareSearch(...)

```python
searcher = QuantizationAwareSearch(mock_vector_store, mock_quantized_store, config)
```

### Step 7: Assign query = _random_vec(...)

```python
query = _random_vec(768, seed=3)
```

### Step 8: Assign results = searcher.search(...)

```python
results = searcher.search(query, 'p1', top_k=50)
```

**Verification:**
```python
assert len(results) == 1
```


## Complete Example

```python
# Setup
# Fixtures: mock_vector_store, mock_quantized_store

# Workflow
'Polar results are penalized by config.polar_search_penalty.'
mock_vector_store.search.return_value = []
mock_vector_store.search_int8.return_value = []
mock_quantized_store.search.return_value = [('f-polar', 1.0)]
config = QuantizationConfig(polar_search_penalty=0.95)
searcher = QuantizationAwareSearch(mock_vector_store, mock_quantized_store, config)
query = _random_vec(768, seed=3)
results = searcher.search(query, 'p1', top_k=50)
assert len(results) == 1
assert results[0][0] == 'f-polar'
assert results[0][1] == pytest.approx(0.95, abs=0.001)
```

## Next Steps


---

*Source: test_quant_aware_search.py:127 | Complexity: Advanced | Last updated: 2026-05-05*