# How To: Int8 Penalty Applied

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Int8 results are penalized by 0.98 factor.

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
# Fixtures: mock_vector_store, mock_quantized_store, config
```

## Step-by-Step Guide

### Step 1: 'Int8 results are penalized by 0.98 factor.'

```python
'Int8 results are penalized by 0.98 factor.'
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
assert results[0][0] == 'f-int8'
```

### Step 3: Assign mock_vector_store.search_int8.return_value = value

```python
mock_vector_store.search_int8.return_value = [('f-int8', 1.0)]
```

**Verification:**
```python
assert results[0][1] == pytest.approx(0.98, abs=0.001)
```

### Step 4: Assign mock_quantized_store.search.return_value = value

```python
mock_quantized_store.search.return_value = []
```

### Step 5: Assign searcher = QuantizationAwareSearch(...)

```python
searcher = QuantizationAwareSearch(mock_vector_store, mock_quantized_store, config)
```

### Step 6: Assign query = _random_vec(...)

```python
query = _random_vec(768, seed=4)
```

### Step 7: Assign results = searcher.search(...)

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
# Fixtures: mock_vector_store, mock_quantized_store, config

# Workflow
'Int8 results are penalized by 0.98 factor.'
mock_vector_store.search.return_value = []
mock_vector_store.search_int8.return_value = [('f-int8', 1.0)]
mock_quantized_store.search.return_value = []
searcher = QuantizationAwareSearch(mock_vector_store, mock_quantized_store, config)
query = _random_vec(768, seed=4)
results = searcher.search(query, 'p1', top_k=50)
assert len(results) == 1
assert results[0][0] == 'f-int8'
assert results[0][1] == pytest.approx(0.98, abs=0.001)
```

## Next Steps


---

*Source: test_quant_aware_search.py:152 | Complexity: Intermediate | Last updated: 2026-05-05*