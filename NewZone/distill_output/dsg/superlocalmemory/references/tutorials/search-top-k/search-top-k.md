# How To: Search Top K

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test search top k

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

### Step 1: Assign tokens_map = value

```python
tokens_map = {f'f{i}': ['common', 'word'] for i in range(20)}
```

**Verification:**
```python
assert len(results) <= 5
```

### Step 2: Assign db = self._mock_db(...)

```python
db = self._mock_db(tokens_map=tokens_map)
```

### Step 3: Assign ch = BM25Channel(...)

```python
ch = BM25Channel(db)
```

### Step 4: Assign results = ch.search(...)

```python
results = ch.search('common word', 'default', top_k=5)
```

**Verification:**
```python
assert len(results) <= 5
```


## Complete Example

```python
# Workflow
tokens_map = {f'f{i}': ['common', 'word'] for i in range(20)}
db = self._mock_db(tokens_map=tokens_map)
ch = BM25Channel(db)
results = ch.search('common word', 'default', top_k=5)
assert len(results) <= 5
```

## Next Steps


---

*Source: test_bm25_channel.py:163 | Complexity: Intermediate | Last updated: 2026-05-05*