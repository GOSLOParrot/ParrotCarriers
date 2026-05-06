# How To: Batch Returns Fact Ids

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Each result tuple contains (fact_id, score).

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

### Step 1: 'Each result tuple contains (fact_id, score).'

```python
'Each result tuple contains (fact_id, score).'
```

**Verification:**
```python
assert results[0][0] == 'fact_abc'
```

### Step 2: Assign mu = np.array(...)

```python
mu = np.array([1.0, 0.0, 0.0, 0.0])
```

**Verification:**
```python
assert isinstance(results[0][1], float)
```

### Step 3: Assign var = np.full(...)

```python
var = np.full(4, 0.5)
```

### Step 4: Assign candidates = value

```python
candidates = [('fact_abc', mu.copy(), var.copy(), 32)]
```

### Step 5: Assign results = frqad.batch_similarity(...)

```python
results = frqad.batch_similarity(mu, var, 32, candidates)
```

**Verification:**
```python
assert results[0][0] == 'fact_abc'
```


## Complete Example

```python
# Setup
# Fixtures: frqad

# Workflow
'Each result tuple contains (fact_id, score).'
mu = np.array([1.0, 0.0, 0.0, 0.0])
var = np.full(4, 0.5)
candidates = [('fact_abc', mu.copy(), var.copy(), 32)]
results = frqad.batch_similarity(mu, var, 32, candidates)
assert results[0][0] == 'fact_abc'
assert isinstance(results[0][1], float)
```

## Next Steps


---

*Source: test_fisher_quantized.py:357 | Complexity: Intermediate | Last updated: 2026-05-05*