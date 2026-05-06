# How To: No Facts Returns Zero

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test no facts returns zero

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

### Step 1: Assign cfg = _make_config(...)

```python
cfg = _make_config(tmp_path)
```

**Verification:**
```python
assert result == 0
```

### Step 2: Assign db = _make_mock_db(...)

```python
db = _make_mock_db(facts=[])
```

### Step 3: Assign emb = _make_mock_embedder(...)

```python
emb = _make_mock_embedder()
```

### Step 4: Assign result = run_embedding_migration(...)

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
cfg = _make_config(tmp_path)
db = _make_mock_db(facts=[])
emb = _make_mock_embedder()
result = run_embedding_migration(cfg, db, emb)
assert result == 0
```

## Next Steps


---

*Source: test_embedding_migrator.py:224 | Complexity: Intermediate | Last updated: 2026-05-05*