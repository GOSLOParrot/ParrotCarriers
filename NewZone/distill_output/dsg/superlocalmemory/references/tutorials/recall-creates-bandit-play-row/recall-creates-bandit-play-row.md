# How To: Recall Creates Bandit Play Row

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: A full recall path creates one bandit_plays row and returns response.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `sqlite3`
- `dataclasses`
- `pathlib`
- `pytest`
- `superlocalmemory.learning.arm_catalog`
- `superlocalmemory.retrieval.engine`
- `superlocalmemory.storage.migration_runner`
- `superlocalmemory.storage.models`
- `superlocalmemory.core.recall_pipeline`
- `superlocalmemory.core.recall_pipeline`
- `superlocalmemory.core.recall_pipeline`
- `superlocalmemory.core.recall_pipeline`
- `superlocalmemory.core.recall_pipeline`

**Setup Required:**
```python
# Fixtures: bandit_db, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'A full recall path creates one bandit_plays row and returns response.'

```python
'A full recall path creates one bandit_plays row and returns response.'
```

**Verification:**
```python
assert len(out.results) == 5
```

### Step 2: Assign response = _mk_response(...)

```python
response = _mk_response(5)
```

**Verification:**
```python
assert n == 1
```

### Step 3: Assign out = apply_v2_bandit_ensemble(...)

```python
out = apply_v2_bandit_ensemble(response, query='hello', profile_id='px', query_id='qid-1', learning_db_path=bandit_db)
```

**Verification:**
```python
assert len(out.results) == 5
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(bandit_db))
```

**Verification:**
```python
assert n == 1
```

### Step 5: Assign n = value

```python
n = conn.execute('SELECT COUNT(*) FROM bandit_plays WHERE profile_id = ?', ('px',)).fetchone()[0]
```

### Step 6: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: bandit_db, monkeypatch

# Workflow
'A full recall path creates one bandit_plays row and returns response.'
from superlocalmemory.core.recall_pipeline import apply_v2_bandit_ensemble
response = _mk_response(5)
out = apply_v2_bandit_ensemble(response, query='hello', profile_id='px', query_id='qid-1', learning_db_path=bandit_db)
assert len(out.results) == 5
conn = sqlite3.connect(str(bandit_db))
try:
    n = conn.execute('SELECT COUNT(*) FROM bandit_plays WHERE profile_id = ?', ('px',)).fetchone()[0]
finally:
    conn.close()
assert n == 1
```

## Next Steps


---

*Source: test_bandit_in_recall.py:112 | Complexity: Advanced | Last updated: 2026-05-05*