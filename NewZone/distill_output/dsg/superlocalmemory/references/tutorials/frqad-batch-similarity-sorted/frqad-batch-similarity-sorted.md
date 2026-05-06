# How To: Frqad Batch Similarity Sorted

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: batch_similarity returns results sorted descending by score.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.math.fisher`
- `superlocalmemory.math.fisher_quantized`

**Setup Required:**
```python
# Fixtures: frqad
```

## Step-by-Step Guide

### Step 1: 'batch_similarity returns results sorted descending by score.'

```python
'batch_similarity returns results sorted descending by score.'
```

**Verification:**
```python
assert len(results) == 4
```

### Step 2: Assign rng = np.random.default_rng(...)

```python
rng = np.random.default_rng(77)
```

**Verification:**
```python
assert scores[i] >= scores[i + 1], f'Not sorted descending at index {i}: {scores[i]} < {scores[i + 1]}'
```

### Step 3: Assign query_mu = rng.standard_normal(...)

```python
query_mu = rng.standard_normal(8)
```

### Step 4: Assign query_mu = value

```python
query_mu = query_mu / np.linalg.norm(query_mu)
```

### Step 5: Assign query_var = np.full(...)

```python
query_var = np.full(8, 0.5)
```

### Step 6: Assign candidates = value

```python
candidates = []
```

### Step 7: Assign results = frqad.batch_similarity(...)

```python
results = frqad.batch_similarity(query_mu, query_var, 32, candidates)
```

**Verification:**
```python
assert len(results) == 4
```

### Step 8: Assign scores = value

```python
scores = [score for _, score in results]
```

### Step 9: Assign mu = rng.standard_normal(...)

```python
mu = rng.standard_normal(8)
```

### Step 10: Assign mu = value

```python
mu = mu / np.linalg.norm(mu)
```

### Step 11: Assign var = np.full(...)

```python
var = np.full(8, 0.5)
```

### Step 12: Call candidates.append()

```python
candidates.append((f'fact_{i}', mu, var, bw))
```

**Verification:**
```python
assert scores[i] >= scores[i + 1], f'Not sorted descending at index {i}: {scores[i]} < {scores[i + 1]}'
```


## Complete Example

```python
# Setup
# Fixtures: frqad

# Workflow
'batch_similarity returns results sorted descending by score.'
rng = np.random.default_rng(77)
query_mu = rng.standard_normal(8)
query_mu = query_mu / np.linalg.norm(query_mu)
query_var = np.full(8, 0.5)
candidates = []
for i, bw in enumerate([2, 4, 8, 32]):
    mu = rng.standard_normal(8)
    mu = mu / np.linalg.norm(mu)
    var = np.full(8, 0.5)
    candidates.append((f'fact_{i}', mu, var, bw))
results = frqad.batch_similarity(query_mu, query_var, 32, candidates)
assert len(results) == 4
scores = [score for _, score in results]
for i in range(len(scores) - 1):
    assert scores[i] >= scores[i + 1], f'Not sorted descending at index {i}: {scores[i]} < {scores[i + 1]}'
```

## Next Steps


---

*Source: test_fisher_quantized.py:331 | Complexity: Advanced | Last updated: 2026-05-05*