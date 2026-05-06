# How To: Updates Signature After Migration

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: V3.3.4+: signature is model_name::dimension (no provider).

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

### Step 1: 'V3.3.4+: signature is model_name::dimension (no provider).'

```python
'V3.3.4+: signature is model_name::dimension (no provider).'
```

**Verification:**
```python
assert 'test-model::512' in stored
```

### Step 2: Assign cfg = _make_config(...)

```python
cfg = _make_config(tmp_path, provider='new-provider', model_name='test-model', dimension=512)
```

### Step 3: Assign db = _make_mock_db(...)

```python
db = _make_mock_db(facts=[])
```

### Step 4: Assign emb = _make_mock_embedder(...)

```python
emb = _make_mock_embedder()
```

### Step 5: Call run_embedding_migration()

```python
run_embedding_migration(cfg, db, emb)
```

### Step 6: Assign stored = _read_stored_signature(...)

```python
stored = _read_stored_signature(tmp_path)
```

**Verification:**
```python
assert 'test-model::512' in stored
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'V3.3.4+: signature is model_name::dimension (no provider).'
cfg = _make_config(tmp_path, provider='new-provider', model_name='test-model', dimension=512)
db = _make_mock_db(facts=[])
emb = _make_mock_embedder()
run_embedding_migration(cfg, db, emb)
stored = _read_stored_signature(tmp_path)
assert 'test-model::512' in stored
```

## Next Steps


---

*Source: test_embedding_migrator.py:259 | Complexity: Intermediate | Last updated: 2026-05-05*