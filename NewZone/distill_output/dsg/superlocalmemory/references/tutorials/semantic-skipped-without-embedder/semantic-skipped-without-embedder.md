# How To: Semantic Skipped Without Embedder

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test semantic skipped without embedder

## Prerequisites

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.retrieval.fusion`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: Assign facts = value

```python
facts = [_make_fact('f1')]
```

### Step 2: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 3: Assign sem_ch = _mock_channel(...)

```python
sem_ch = _mock_channel([('f1', 0.9)])
```

### Step 4: Assign engine = RetrievalEngine(...)

```python
engine = RetrievalEngine(db=db, config=RetrievalConfig(), channels={'semantic': sem_ch}, embedder=None)
```

### Step 5: Assign response = engine.recall(...)

```python
response = engine.recall('q', 'default')
```

### Step 6: Call sem_ch.search.assert_not_called()

```python
sem_ch.search.assert_not_called()
```


## Complete Example

```python
# Workflow
facts = [_make_fact('f1')]
db = _mock_db(facts)
sem_ch = _mock_channel([('f1', 0.9)])
engine = RetrievalEngine(db=db, config=RetrievalConfig(), channels={'semantic': sem_ch}, embedder=None)
response = engine.recall('q', 'default')
sem_ch.search.assert_not_called()
```

## Next Steps


---

*Source: test_engine.py:338 | Complexity: Intermediate | Last updated: 2026-05-05*