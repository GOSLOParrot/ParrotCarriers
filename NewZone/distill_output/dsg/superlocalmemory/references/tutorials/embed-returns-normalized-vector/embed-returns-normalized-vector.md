# How To: Embed Returns Normalized Vector

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test embed returns normalized vector

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

### Step 1: Assign raw_vec = _random_vec(...)

```python
raw_vec = _random_vec(768)
```

**Verification:**
```python
assert result is not None
```

### Step 2: Assign emb = OllamaEmbedder(...)

```python
emb = OllamaEmbedder(dimension=768)
```

**Verification:**
```python
assert len(result) == 768
```

### Step 3: Assign norm = float(...)

```python
norm = float(np.linalg.norm(result))
```

**Verification:**
```python
assert abs(norm - 1.0) < 1e-05
```

### Step 4: Assign result = emb.embed(...)

```python
result = emb.embed('hello world')
```


## Complete Example

```python
# Workflow
raw_vec = _random_vec(768)
emb = OllamaEmbedder(dimension=768)
with patch('httpx.post', return_value=_fake_embed_response([raw_vec])):
    result = emb.embed('hello world')
assert result is not None
assert len(result) == 768
norm = float(np.linalg.norm(result))
assert abs(norm - 1.0) < 1e-05
```

## Next Steps


---

*Source: test_ollama_embedder.py:105 | Complexity: Intermediate | Last updated: 2026-05-05*