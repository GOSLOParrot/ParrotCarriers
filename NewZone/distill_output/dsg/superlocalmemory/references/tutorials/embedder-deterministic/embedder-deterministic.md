# How To: Embedder Deterministic

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Same text produces the same embedding (deterministic).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `time`
- `pathlib`
- `typing`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.llm.backbone`
- `superlocalmemory.storage.models`
- `httpx`
- `httpx`
- `httpx`
- `warnings`

**Setup Required:**
```python
# Fixtures: ollama_embedder
```

## Step-by-Step Guide

### Step 1: 'Same text produces the same embedding (deterministic).'

```python
'Same text produces the same embedding (deterministic).'
```

**Verification:**
```python
assert cos_sim > 0.999, f'Embeddings not deterministic: cos_sim={cos_sim}'
```

### Step 2: Assign text = 'The quick brown fox jumps over the lazy dog.'

```python
text = 'The quick brown fox jumps over the lazy dog.'
```

### Step 3: Assign v1 = ollama_embedder.embed(...)

```python
v1 = ollama_embedder.embed(text)
```

### Step 4: Assign v2 = ollama_embedder.embed(...)

```python
v2 = ollama_embedder.embed(text)
```

### Step 5: Assign cos_sim = float(...)

```python
cos_sim = float(np.dot(v1, v2))
```

**Verification:**
```python
assert cos_sim > 0.999, f'Embeddings not deterministic: cos_sim={cos_sim}'
```


## Complete Example

```python
# Setup
# Fixtures: ollama_embedder

# Workflow
'Same text produces the same embedding (deterministic).'
text = 'The quick brown fox jumps over the lazy dog.'
v1 = ollama_embedder.embed(text)
v2 = ollama_embedder.embed(text)
cos_sim = float(np.dot(v1, v2))
assert cos_sim > 0.999, f'Embeddings not deterministic: cos_sim={cos_sim}'
```

## Next Steps


---

*Source: test_mode_b_ollama.py:278 | Complexity: Intermediate | Last updated: 2026-05-05*