# How To: Fisher Variance Bounds

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test fisher variance bounds

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.ollama_embedder`
- `httpx`


## Step-by-Step Guide

### Step 1: Assign emb = OllamaEmbedder(...)

```python
emb = OllamaEmbedder(dimension=768)
```

**Verification:**
```python
assert float(np.min(var_arr)) >= 0.05 - 1e-07
```

### Step 2: Assign vec = _random_vec(...)

```python
vec = _random_vec(768)
```

**Verification:**
```python
assert float(np.max(var_arr)) <= 2.0 + 1e-07
```

### Step 3: Assign arr = np.asarray(...)

```python
arr = np.asarray(vec, dtype=np.float32)
```

### Step 4: Assign arr = value

```python
arr = arr / np.linalg.norm(arr)
```

### Step 5: Assign unknown = emb.compute_fisher_params(...)

```python
_, var = emb.compute_fisher_params(arr.tolist())
```

### Step 6: Assign var_arr = np.asarray(...)

```python
var_arr = np.asarray(var)
```

**Verification:**
```python
assert float(np.min(var_arr)) >= 0.05 - 1e-07
```


## Complete Example

```python
# Workflow
emb = OllamaEmbedder(dimension=768)
vec = _random_vec(768)
arr = np.asarray(vec, dtype=np.float32)
arr = arr / np.linalg.norm(arr)
_, var = emb.compute_fisher_params(arr.tolist())
var_arr = np.asarray(var)
assert float(np.min(var_arr)) >= 0.05 - 1e-07
assert float(np.max(var_arr)) <= 2.0 + 1e-07
```

## Next Steps


---

*Source: test_ollama_embedder.py:187 | Complexity: Intermediate | Last updated: 2026-05-05*