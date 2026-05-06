# How To: Search Returns Matching Docs

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test search returns matching docs

## Prerequisites

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.retrieval.bm25_channel`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign db = self._mock_db(...)

```python
db = self._mock_db(tokens_map={'f1': ['alice', 'engineer'], 'f2': ['bob', 'doctor']})
```

**Verification:**
```python
assert len(results) > 0
```

### Step 2: Assign ch = BM25Channel(...)

```python
ch = BM25Channel(db)
```

**Verification:**
```python
assert 'f1' in fact_ids
```

### Step 3: Assign results = ch.search(...)

```python
results = ch.search('alice engineer', 'default')
```

**Verification:**
```python
assert len(results) > 0
```

### Step 4: Assign fact_ids = value

```python
fact_ids = [r[0] for r in results]
```

**Verification:**
```python
assert 'f1' in fact_ids
```


## Complete Example

```python
# Workflow
db = self._mock_db(tokens_map={'f1': ['alice', 'engineer'], 'f2': ['bob', 'doctor']})
ch = BM25Channel(db)
results = ch.search('alice engineer', 'default')
assert len(results) > 0
fact_ids = [r[0] for r in results]
assert 'f1' in fact_ids
```

## Next Steps


---

*Source: test_bm25_channel.py:133 | Complexity: Intermediate | Last updated: 2026-05-05*