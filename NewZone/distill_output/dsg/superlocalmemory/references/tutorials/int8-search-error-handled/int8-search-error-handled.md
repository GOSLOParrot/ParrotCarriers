# How To: Int8 Search Error Handled

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Int8 tier exception returns empty, other tiers still work.

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

### Step 1: 'Int8 tier exception returns empty, other tiers still work.'

```python
'Int8 tier exception returns empty, other tiers still work.'
```

**Verification:**
```python
assert len(results) >= 1
```

### Step 2: Assign mock_vector_store.search_int8.side_effect = RuntimeError(...)

```python
mock_vector_store.search_int8.side_effect = RuntimeError('int8 broke')
```

### Step 3: Assign mock_quantized_store.search.return_value = value

```python
mock_quantized_store.search.return_value = []
```

### Step 4: Assign searcher = QuantizationAwareSearch(...)

```python
searcher = QuantizationAwareSearch(mock_vector_store, mock_quantized_store, config)
```

### Step 5: Assign query = _random_vec(...)

```python
query = _random_vec(768, seed=6)
```

### Step 6: Assign results = searcher.search(...)

```python
results = searcher.search(query, 'p1', top_k=50)
```

**Verification:**
```python
assert len(results) >= 1
```


## Complete Example

```python
# Setup
# Fixtures: mock_vector_store, mock_quantized_store, config

# Workflow
'Int8 tier exception returns empty, other tiers still work.'
mock_vector_store.search_int8.side_effect = RuntimeError('int8 broke')
mock_quantized_store.search.return_value = []
searcher = QuantizationAwareSearch(mock_vector_store, mock_quantized_store, config)
query = _random_vec(768, seed=6)
results = searcher.search(query, 'p1', top_k=50)
assert len(results) >= 1
```

## Next Steps


---

*Source: test_quant_aware_search.py:194 | Complexity: Advanced | Last updated: 2026-05-05*