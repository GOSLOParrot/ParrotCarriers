# How To: Empty Disabled All Channels Run

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: An empty disabled_channels list means all channels are active.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'An empty disabled_channels list means all channels are active.'

```python
'An empty disabled_channels list means all channels are active.'
```

### Step 2: Assign facts = value

```python
facts = [_make_fact('f1', 'Semantic result about the enterprise architecture discussion'), _make_fact('f2', 'BM25 result about the code review process and findings')]
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 4: Assign config = RetrievalConfig(...)

```python
config = RetrievalConfig(disabled_channels=[])
```

### Step 5: Assign sem_ch = _mock_channel(...)

```python
sem_ch = _mock_channel([('f1', 0.9)])
```

### Step 6: Assign bm25_ch = _mock_channel(...)

```python
bm25_ch = _mock_channel([('f2', 0.8)])
```

### Step 7: Assign engine = RetrievalEngine(...)

```python
engine = RetrievalEngine(db=db, config=config, channels={'semantic': sem_ch, 'bm25': bm25_ch}, embedder=_mock_embedder())
```

### Step 8: Call engine.recall()

```python
engine.recall('q', 'default')
```

### Step 9: Call sem_ch.search.assert_called_once()

```python
sem_ch.search.assert_called_once()
```

### Step 10: Call bm25_ch.search.assert_called_once()

```python
bm25_ch.search.assert_called_once()
```


## Complete Example

```python
# Workflow
'An empty disabled_channels list means all channels are active.'
facts = [_make_fact('f1', 'Semantic result about the enterprise architecture discussion'), _make_fact('f2', 'BM25 result about the code review process and findings')]
db = _mock_db(facts)
config = RetrievalConfig(disabled_channels=[])
sem_ch = _mock_channel([('f1', 0.9)])
bm25_ch = _mock_channel([('f2', 0.8)])
engine = RetrievalEngine(db=db, config=config, channels={'semantic': sem_ch, 'bm25': bm25_ch}, embedder=_mock_embedder())
engine.recall('q', 'default')
sem_ch.search.assert_called_once()
bm25_ch.search.assert_called_once()
```

## Next Steps


---

*Source: test_retrieval_integration.py:223 | Complexity: Advanced | Last updated: 2026-05-05*