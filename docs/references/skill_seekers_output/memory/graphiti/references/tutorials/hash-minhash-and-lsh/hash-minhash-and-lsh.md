# How To: Hash Minhash And Lsh

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test hash minhash and lsh

## Prerequisites

**Required Modules:**
- `logging`
- `collections`
- `unittest.mock`
- `pytest`
- `graphiti_core.graphiti_types`
- `graphiti_core.nodes`
- `graphiti_core.search.search_config`
- `graphiti_core.utils.datetime_utils`
- `graphiti_core.utils.maintenance.dedup_helpers`
- `graphiti_core.utils.maintenance.node_operations`
- `graphiti_core.edges`
- `graphiti_core.utils.text_utils`


## Step-by-Step Guide

### Step 1: Assign shingles = value

```python
shingles = {'abc', 'bcd', 'cde'}
```

**Verification:**
```python
assert len(signature) == 32
```

### Step 2: Assign signature = _minhash_signature(...)

```python
signature = _minhash_signature(shingles)
```

**Verification:**
```python
assert all((len(band) == 4 for band in bands))
```

### Step 3: Assign bands = _lsh_bands(...)

```python
bands = _lsh_bands(signature)
```

**Verification:**
```python
assert len(hashed) == len(shingles)
```

### Step 4: Assign hashed = value

```python
hashed = {_hash_shingle(s, 0) for s in shingles}
```

**Verification:**
```python
assert len(hashed) == len(shingles)
```


## Complete Example

```python
# Workflow
shingles = {'abc', 'bcd', 'cde'}
signature = _minhash_signature(shingles)
assert len(signature) == 32
bands = _lsh_bands(signature)
assert all((len(band) == 4 for band in bands))
hashed = {_hash_shingle(s, 0) for s in shingles}
assert len(hashed) == len(shingles)
```

## Next Steps


---

*Source: test_node_operations.py:219 | Complexity: Intermediate | Last updated: 2026-04-12*