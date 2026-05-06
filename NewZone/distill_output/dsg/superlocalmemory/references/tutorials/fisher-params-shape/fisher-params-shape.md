# How To: Fisher Params Shape

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test fisher params shape

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
assert len(mean) == 768
```

### Step 2: Assign vec = _random_vec(...)

```python
vec = _random_vec(768)
```

**Verification:**
```python
assert len(var) == 768
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
mean, var = emb.compute_fisher_params(arr.tolist())
```

**Verification:**
```python
assert len(mean) == 768
```


## Complete Example

```python
# Workflow
emb = OllamaEmbedder(dimension=768)
vec = _random_vec(768)
arr = np.asarray(vec, dtype=np.float32)
arr = arr / np.linalg.norm(arr)
mean, var = emb.compute_fisher_params(arr.tolist())
assert len(mean) == 768
assert len(var) == 768
```

## Next Steps


---

*Source: test_ollama_embedder.py:177 | Complexity: Intermediate | Last updated: 2026-05-05*