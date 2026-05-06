# How To: Two Channels Disjoint Docs

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test two channels disjoint docs

## Prerequisites

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.retrieval.fusion`


## Step-by-Step Guide

### Step 1: Assign channels = value

```python
channels = {'sem': [('f1', 0.9)], 'bm25': [('f2', 0.8)]}
```

**Verification:**
```python
assert len(results) == 2
```

### Step 2: Assign weights = value

```python
weights = {'sem': 1.0, 'bm25': 1.0}
```

**Verification:**
```python
assert set(ids) == {'f1', 'f2'}
```

### Step 3: Assign results = weighted_rrf(...)

```python
results = weighted_rrf(channels, weights, k=20)
```

**Verification:**
```python
assert len(results) == 2
```

### Step 4: Assign ids = _ids(...)

```python
ids = _ids(results)
```

**Verification:**
```python
assert set(ids) == {'f1', 'f2'}
```


## Complete Example

```python
# Workflow
channels = {'sem': [('f1', 0.9)], 'bm25': [('f2', 0.8)]}
weights = {'sem': 1.0, 'bm25': 1.0}
results = weighted_rrf(channels, weights, k=20)
assert len(results) == 2
ids = _ids(results)
assert set(ids) == {'f1', 'f2'}
```

## Next Steps


---

*Source: test_fusion.py:66 | Complexity: Intermediate | Last updated: 2026-05-05*