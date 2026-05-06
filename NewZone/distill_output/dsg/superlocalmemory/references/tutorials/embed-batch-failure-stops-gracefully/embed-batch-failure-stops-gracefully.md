# How To: Embed Batch Failure Stops Gracefully

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test embed batch failure stops gracefully

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.storage.embedding_migrator`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`
- `superlocalmemory.core.config`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign facts = value

```python
facts = [('f1', 'content 1')]
```

**Verification:**
```python
assert result == 0
```

### Step 2: Assign cfg = _make_config(...)

```python
cfg = _make_config(tmp_path)
```

### Step 3: Assign db = _make_mock_db(...)

```python
db = _make_mock_db(facts=facts)
```

### Step 4: Assign emb = _make_mock_embedder(...)

```python
emb = _make_mock_embedder()
```

### Step 5: Assign emb.embed_batch.side_effect = RuntimeError(...)

```python
emb.embed_batch.side_effect = RuntimeError('GPU exploded')
```

### Step 6: Assign result = run_embedding_migration(...)

```python
result = run_embedding_migration(cfg, db, emb)
```

**Verification:**
```python
assert result == 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
facts = [('f1', 'content 1')]
cfg = _make_config(tmp_path)
db = _make_mock_db(facts=facts)
emb = _make_mock_embedder()
emb.embed_batch.side_effect = RuntimeError('GPU exploded')
result = run_embedding_migration(cfg, db, emb)
assert result == 0
```

## Next Steps


---

*Source: test_embedding_migrator.py:268 | Complexity: Intermediate | Last updated: 2026-05-05*