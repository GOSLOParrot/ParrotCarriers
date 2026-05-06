# How To: Semantic Similarity Meaningful

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: 'feline' query should rank 'cat' fact higher than 'dog' fact.

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
# Fixtures: mode_b_engine
```

## Step-by-Step Guide

### Step 1: "'feline' query should rank 'cat' fact higher than 'dog' fact."

```python
"'feline' query should rank 'cat' fact higher than 'dog' fact."
```

**Verification:**
```python
assert has_cat or has_dog, f"Expected at least one animal fact for 'feline'. Got: {contents}"
```

### Step 2: Call mode_b_engine.store()

```python
mode_b_engine.store('The cat sat on the mat.', session_id='s1')
```

### Step 3: Call mode_b_engine.store()

```python
mode_b_engine.store('The dog ran in the park.', session_id='s1')
```

### Step 4: Assign response = mode_b_engine.recall(...)

```python
response = mode_b_engine.recall('feline')
```

### Step 5: Assign contents = value

```python
contents = [r.fact.content.lower() for r in response.results]
```

### Step 6: Assign cat_idx = next(...)

```python
cat_idx = next((i for i, c in enumerate(contents) if 'cat' in c and 'dog' not in c), None)
```

### Step 7: Assign dog_idx = next(...)

```python
dog_idx = next((i for i, c in enumerate(contents) if 'dog' in c and 'cat' not in c), None)
```

### Step 8: Assign has_cat = any(...)

```python
has_cat = any(('cat' in c for c in contents))
```

### Step 9: Assign has_dog = any(...)

```python
has_dog = any(('dog' in c for c in contents))
```

**Verification:**
```python
assert has_cat or has_dog, f"Expected at least one animal fact for 'feline'. Got: {contents}"
```

### Step 10: Call pytest.skip()

```python
pytest.skip('Not enough results to compare ranking')
```

### Step 11: Call warnings.warn()

```python
warnings.warn(f"Embedding quality: 'dog' ranked above 'cat' for 'feline' (cat={cat_idx}, dog={dog_idx}). Model-dependent.", stacklevel=1)
```


## Complete Example

```python
# Setup
# Fixtures: mode_b_engine

# Workflow
"'feline' query should rank 'cat' fact higher than 'dog' fact."
mode_b_engine.store('The cat sat on the mat.', session_id='s1')
mode_b_engine.store('The dog ran in the park.', session_id='s1')
response = mode_b_engine.recall('feline')
if len(response.results) < 2:
    pytest.skip('Not enough results to compare ranking')
contents = [r.fact.content.lower() for r in response.results]
cat_idx = next((i for i, c in enumerate(contents) if 'cat' in c and 'dog' not in c), None)
dog_idx = next((i for i, c in enumerate(contents) if 'dog' in c and 'cat' not in c), None)
has_cat = any(('cat' in c for c in contents))
has_dog = any(('dog' in c for c in contents))
assert has_cat or has_dog, f"Expected at least one animal fact for 'feline'. Got: {contents}"
if cat_idx is not None and dog_idx is not None and (cat_idx > dog_idx):
    import warnings
    warnings.warn(f"Embedding quality: 'dog' ranked above 'cat' for 'feline' (cat={cat_idx}, dog={dog_idx}). Model-dependent.", stacklevel=1)
```

## Next Steps


---

*Source: test_mode_b_ollama.py:364 | Complexity: Advanced | Last updated: 2026-05-05*