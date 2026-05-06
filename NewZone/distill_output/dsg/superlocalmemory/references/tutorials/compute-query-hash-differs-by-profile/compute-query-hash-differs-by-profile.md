# How To: Compute Query Hash Differs By Profile

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Different profile produces different hash.

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

### Step 1: 'Different profile produces different hash.'

```python
'Different profile produces different hash.'
```

**Verification:**
```python
assert h1 != h2
```

### Step 2: Assign sa = SpreadingActivation(...)

```python
sa = SpreadingActivation(mock_db, mock_vector_store)
```

### Step 3: Assign vec = np.array(...)

```python
vec = np.array([1.0, 2.0, 3.0], dtype=np.float32)
```

### Step 4: Assign h1 = sa._compute_query_hash(...)

```python
h1 = sa._compute_query_hash(vec, 'profile_a')
```

### Step 5: Assign h2 = sa._compute_query_hash(...)

```python
h2 = sa._compute_query_hash(vec, 'profile_b')
```

**Verification:**
```python
assert h1 != h2
```


## Complete Example

```python
# Setup
# Fixtures: mock_db, mock_vector_store

# Workflow
'Different profile produces different hash.'
sa = SpreadingActivation(mock_db, mock_vector_store)
vec = np.array([1.0, 2.0, 3.0], dtype=np.float32)
h1 = sa._compute_query_hash(vec, 'profile_a')
h2 = sa._compute_query_hash(vec, 'profile_b')
assert h1 != h2
```

## Next Steps


---

*Source: test_spreading_activation.py:206 | Complexity: Intermediate | Last updated: 2026-05-05*