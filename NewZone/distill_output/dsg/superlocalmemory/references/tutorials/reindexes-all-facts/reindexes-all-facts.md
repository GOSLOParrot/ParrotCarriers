# How To: Reindexes All Facts

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test reindexes all facts

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
facts = [('fact-1', 'Alice went to Paris'), ('fact-2', 'Bob likes pizza'), ('fact-3', 'Weather is sunny')]
```

**Verification:**
```python
assert result == 3
```

### Step 2: Assign cfg = _make_config(...)

```python
cfg = _make_config(tmp_path)
```

### Step 3: Assign db = _make_mock_db(...)

```python
db = _make_mock_db(facts=facts)
```

### Step 4: Assign call_count = value

```python
call_count = [0]
```

### Step 5: Assign original_return = value

```python
original_return = db.execute.return_value
```

### Step 6: Assign db.execute.side_effect = _side_effect

```python
db.execute.side_effect = _side_effect
```

### Step 7: Assign emb = _make_mock_embedder(...)

```python
emb = _make_mock_embedder()
```

### Step 8: Assign result = run_embedding_migration(...)

```python
result = run_embedding_migration(cfg, db, emb)
```

**Verification:**
```python
assert result == 3
```

### Step 9: Call emb.embed_batch.assert_called_once()

```python
emb.embed_batch.assert_called_once()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
facts = [('fact-1', 'Alice went to Paris'), ('fact-2', 'Bob likes pizza'), ('fact-3', 'Weather is sunny')]
cfg = _make_config(tmp_path)
db = _make_mock_db(facts=facts)
call_count = [0]
original_return = db.execute.return_value

def _side_effect(sql, params=()):
    call_count[0] += 1
    if call_count[0] == 1:
        return original_return
    return []
db.execute.side_effect = _side_effect
emb = _make_mock_embedder()
result = run_embedding_migration(cfg, db, emb)
assert result == 3
emb.embed_batch.assert_called_once()
```

## Next Steps


---

*Source: test_embedding_migrator.py:231 | Complexity: Advanced | Last updated: 2026-05-05*