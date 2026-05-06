# How To: Recall Bandit Disabled Env Skips

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: SLM_BANDIT_DISABLED=1 → identity; no play row created.

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

### Step 1: 'SLM_BANDIT_DISABLED=1 → identity; no play row created.'

```python
'SLM_BANDIT_DISABLED=1 → identity; no play row created.'
```

**Verification:**
```python
assert out is response
```

### Step 2: Call monkeypatch.setenv()

```python
monkeypatch.setenv('SLM_BANDIT_DISABLED', '1')
```

**Verification:**
```python
assert n == 0
```

### Step 3: Assign response = _mk_response(...)

```python
response = _mk_response(3)
```

### Step 4: Assign out = apply_v2_bandit_ensemble(...)

```python
out = apply_v2_bandit_ensemble(response, query='q', profile_id='off', query_id='qid-off', learning_db_path=bandit_db)
```

**Verification:**
```python
assert out is response
```

### Step 5: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(bandit_db))
```

**Verification:**
```python
assert n == 0
```

### Step 6: Assign n = value

```python
n = conn.execute('SELECT COUNT(*) FROM bandit_plays').fetchone()[0]
```

### Step 7: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: bandit_db, monkeypatch

# Workflow
'SLM_BANDIT_DISABLED=1 → identity; no play row created.'
from superlocalmemory.core.recall_pipeline import apply_v2_bandit_ensemble
monkeypatch.setenv('SLM_BANDIT_DISABLED', '1')
response = _mk_response(3)
out = apply_v2_bandit_ensemble(response, query='q', profile_id='off', query_id='qid-off', learning_db_path=bandit_db)
assert out is response
conn = sqlite3.connect(str(bandit_db))
try:
    n = conn.execute('SELECT COUNT(*) FROM bandit_plays').fetchone()[0]
finally:
    conn.close()
assert n == 0
```

## Next Steps


---

*Source: test_bandit_in_recall.py:135 | Complexity: Advanced | Last updated: 2026-05-05*