# How To: Disabled Channels Skipped

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Channels in disabled_channels list are not called.

## Prerequisites

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.models`


## Step-by-Step Guide

### Step 1: 'Channels in disabled_channels list are not called.'

```python
'Channels in disabled_channels list are not called.'
```

### Step 2: Assign facts = value

```python
facts = [_make_fact('f_sem', 'Semantic channel fact with detailed architecture content'), _make_fact('f_bm25', 'BM25 channel fact about keyword matching and relevance')]
```

### Step 3: Assign db = _mock_db(...)

```python
db = _mock_db(facts)
```

### Step 4: Assign config = RetrievalConfig(...)

```python
config = RetrievalConfig(disabled_channels=['bm25'])
```

### Step 5: Assign sem_ch = _mock_channel(...)

```python
sem_ch = _mock_channel([('f_sem', 0.9)])
```

### Step 6: Assign bm25_ch = _mock_channel(...)

```python
bm25_ch = _mock_channel([('f_bm25', 0.8)])
```

### Step 7: Assign engine = RetrievalEngine(...)

```python
engine = RetrievalEngine(db=db, config=config, channels={'semantic': sem_ch, 'bm25': bm25_ch}, embedder=_mock_embedder())
```

### Step 8: Call engine.recall()

```python
engine.recall('q', 'default')
```

### Step 9: Call bm25_ch.search.assert_not_called()

```python
bm25_ch.search.assert_not_called()
```

### Step 10: Call sem_ch.search.assert_called_once()

```python
sem_ch.search.assert_called_once()
```


## Complete Example

```python
# Workflow
'Channels in disabled_channels list are not called.'
facts = [_make_fact('f_sem', 'Semantic channel fact with detailed architecture content'), _make_fact('f_bm25', 'BM25 channel fact about keyword matching and relevance')]
db = _mock_db(facts)
config = RetrievalConfig(disabled_channels=['bm25'])
sem_ch = _mock_channel([('f_sem', 0.9)])
bm25_ch = _mock_channel([('f_bm25', 0.8)])
engine = RetrievalEngine(db=db, config=config, channels={'semantic': sem_ch, 'bm25': bm25_ch}, embedder=_mock_embedder())
engine.recall('q', 'default')
bm25_ch.search.assert_not_called()
sem_ch.search.assert_called_once()
```

## Next Steps


---

*Source: test_retrieval_integration.py:203 | Complexity: Advanced | Last updated: 2026-05-05*