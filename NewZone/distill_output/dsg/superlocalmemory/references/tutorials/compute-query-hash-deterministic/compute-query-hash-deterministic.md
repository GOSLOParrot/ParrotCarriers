# How To: Compute Query Hash Deterministic

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Same input produces same hash.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `math`
- `sqlite3`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.retrieval.spreading_activation`
- `superlocalmemory.storage.schema_v32`

**Setup Required:**
```python
# Fixtures: mock_db, mock_vector_store
```

## Step-by-Step Guide

### Step 1: 'Same input produces same hash.'

```python
'Same input produces same hash.'
```

**Verification:**
```python
assert h1 == h2
```

### Step 2: Assign sa = SpreadingActivation(...)

```python
sa = SpreadingActivation(mock_db, mock_vector_store)
```

**Verification:**
```python
assert len(h1) == 16
```

### Step 3: Assign vec = np.array(...)

```python
vec = np.array([1.0, 2.0, 3.0], dtype=np.float32)
```

### Step 4: Assign h1 = sa._compute_query_hash(...)

```python
h1 = sa._compute_query_hash(vec, 'default')
```

### Step 5: Assign h2 = sa._compute_query_hash(...)

```python
h2 = sa._compute_query_hash(vec, 'default')
```

**Verification:**
```python
assert h1 == h2
```


## Complete Example

```python
# Setup
# Fixtures: mock_db, mock_vector_store

# Workflow
'Same input produces same hash.'
sa = SpreadingActivation(mock_db, mock_vector_store)
vec = np.array([1.0, 2.0, 3.0], dtype=np.float32)
h1 = sa._compute_query_hash(vec, 'default')
h2 = sa._compute_query_hash(vec, 'default')
assert h1 == h2
assert len(h1) == 16
```

## Next Steps


---

*Source: test_spreading_activation.py:196 | Complexity: Intermediate | Last updated: 2026-05-05*