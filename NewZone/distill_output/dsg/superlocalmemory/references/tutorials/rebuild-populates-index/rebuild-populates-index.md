# How To: Rebuild Populates Index

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test rebuild populates index

## Prerequisites

**Required Modules:**
- `__future__`
- `math`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.ann_index`


## Step-by-Step Guide

### Step 1: Assign idx = ANNIndex(...)

```python
idx = ANNIndex(dimension=4)
```

**Verification:**
```python
assert count == 3
```

### Step 2: Assign ids = value

```python
ids = ['a', 'b', 'c']
```

**Verification:**
```python
assert idx.size == 3
```

### Step 3: Assign embs = value

```python
embs = [_unit_vec(4, 0), _unit_vec(4, 1), _unit_vec(4, 2)]
```

### Step 4: Assign count = idx.rebuild(...)

```python
count = idx.rebuild(ids, embs)
```

**Verification:**
```python
assert count == 3
```


## Complete Example

```python
# Workflow
idx = ANNIndex(dimension=4)
ids = ['a', 'b', 'c']
embs = [_unit_vec(4, 0), _unit_vec(4, 1), _unit_vec(4, 2)]
count = idx.rebuild(ids, embs)
assert count == 3
assert idx.size == 3
```

## Next Steps


---

*Source: test_ann_index.py:188 | Complexity: Intermediate | Last updated: 2026-05-05*