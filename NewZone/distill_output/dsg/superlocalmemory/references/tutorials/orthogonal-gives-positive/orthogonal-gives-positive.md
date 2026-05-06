# How To: Orthogonal Gives Positive

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test orthogonal gives positive

## Prerequisites

**Required Modules:**
- `__future__`
- `json`
- `dataclasses`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.math.sheaf`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign emb_a = np.array(...)

```python
emb_a = np.array([1.0, 0.0])
```

**Verification:**
```python
assert severity > 0.0
```

### Step 2: Assign emb_b = np.array(...)

```python
emb_b = np.array([0.0, 1.0])
```

### Step 3: Assign R = np.eye(...)

```python
R = np.eye(2)
```

### Step 4: Assign severity = coboundary_norm(...)

```python
severity = coboundary_norm(emb_a, emb_b, R, R)
```

**Verification:**
```python
assert severity > 0.0
```


## Complete Example

```python
# Workflow
emb_a = np.array([1.0, 0.0])
emb_b = np.array([0.0, 1.0])
R = np.eye(2)
severity = coboundary_norm(emb_a, emb_b, R, R)
assert severity > 0.0
```

## Next Steps


---

*Source: test_sheaf.py:124 | Complexity: Intermediate | Last updated: 2026-05-05*