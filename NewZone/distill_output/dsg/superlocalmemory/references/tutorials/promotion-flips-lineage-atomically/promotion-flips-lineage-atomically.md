# How To: Promotion Flips Lineage Atomically

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Promotion MUST flip (active→previous) + (candidate→active) in a
single BEGIN IMMEDIATE transaction. The partial unique index
``idx_model_active_one`` prevents double-active; ``idx_model_candidate_one``
prevents double-candidate.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `sqlite3`
- `time`
- `uuid`
- `datetime`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.model_rollback`
- `superlocalmemory.learning.consolidation_worker`
- `superlocalmemory.learning.model_rollback`
- `logging`
- `superlocalmemory.learning.model_rollback`
- `numpy`
- `numpy`

**Setup Required:**
```python
# Fixtures: learning_db
```

## Step-by-Step Guide

### Step 1: 'Promotion MUST flip (active→previous) + (candidate→active) in a\n    single BEGIN IMMEDIATE transaction. The partial unique index\n    ``idx_model_active_one`` prevents double-active; ``idx_model_candidate_one``\n    prevents double-candidate.'

```python
'Promotion MUST flip (active→previous) + (candidate→active) in a\n    single BEGIN IMMEDIATE transaction. The partial unique index\n    ``idx_model_active_one`` prevents double-active; ``idx_model_candidate_one``\n    prevents double-candidate.'
```

**Verification:**
```python
assert len(rows) == 2
```

### Step 2: Assign active_id = _seed_active_model(...)

```python
active_id = _seed_active_model(learning_db, profile_id='p', new_outcomes=0, state_bytes=b'active-state')
```

**Verification:**
```python
assert prev_row[1] == 0 and prev_row[2] == 1 and (prev_row[3] == 0)
```

### Step 3: Call _promote_candidate()

```python
_promote_candidate(str(learning_db), profile_id='p', candidate_id=cand_id)
```

**Verification:**
```python
assert new_active[1] == 1
```

### Step 4: Assign cur = conn.execute(...)

```python
cur = conn.execute('INSERT INTO learning_model_state (profile_id, state_bytes, bytes_sha256, is_active, is_candidate, trained_at, updated_at) VALUES (?, ?, ?, 0, 1, ?, ?)', ('p', b'cand-state', '0' * 64, _now_iso(), _now_iso()))
```

**Verification:**
```python
assert new_active[2] == 0
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

**Verification:**
```python
assert new_active[3] == 0
```

### Step 6: Assign cand_id = int(...)

```python
cand_id = int(cur.lastrowid or 0)
```

**Verification:**
```python
assert new_active[4] is not None
```

### Step 7: Assign rows = list(...)

```python
rows = list(conn.execute("SELECT id, is_active, is_previous, is_candidate, promoted_at FROM learning_model_state WHERE profile_id='p' ORDER BY id"))
```

**Verification:**
```python
assert n_active == 1
```

### Step 8: Assign prev_row = value

```python
prev_row = [r for r in rows if r[0] == active_id][0]
```

**Verification:**
```python
assert n_cand == 0
```

### Step 9: Assign new_active = value

```python
new_active = [r for r in rows if r[0] == cand_id][0]
```

**Verification:**
```python
assert prev_row[1] == 0 and prev_row[2] == 1 and (prev_row[3] == 0)
```

### Step 10: Assign n_active = value

```python
n_active = conn.execute("SELECT COUNT(*) FROM learning_model_state WHERE profile_id='p' AND is_active=1").fetchone()[0]
```

**Verification:**
```python
assert n_active == 1
```

### Step 11: Assign n_cand = value

```python
n_cand = conn.execute("SELECT COUNT(*) FROM learning_model_state WHERE profile_id='p' AND is_candidate=1").fetchone()[0]
```

**Verification:**
```python
assert n_cand == 0
```

### Step 12: Call conn.execute()

```python
conn.execute("INSERT INTO learning_model_state (profile_id, state_bytes, bytes_sha256, is_active,  trained_at, updated_at) VALUES ('p', ?, ?, 1, ?, ?)", (b'boom', '0' * 64, _now_iso(), _now_iso()))
```

### Step 13: Call conn.commit()

```python
conn.commit()
```


## Complete Example

```python
# Setup
# Fixtures: learning_db

# Workflow
'Promotion MUST flip (active→previous) + (candidate→active) in a\n    single BEGIN IMMEDIATE transaction. The partial unique index\n    ``idx_model_active_one`` prevents double-active; ``idx_model_candidate_one``\n    prevents double-candidate.'
from superlocalmemory.learning.consolidation_worker import _promote_candidate
active_id = _seed_active_model(learning_db, profile_id='p', new_outcomes=0, state_bytes=b'active-state')
with sqlite3.connect(learning_db) as conn:
    cur = conn.execute('INSERT INTO learning_model_state (profile_id, state_bytes, bytes_sha256, is_active, is_candidate, trained_at, updated_at) VALUES (?, ?, ?, 0, 1, ?, ?)', ('p', b'cand-state', '0' * 64, _now_iso(), _now_iso()))
    conn.commit()
    cand_id = int(cur.lastrowid or 0)
_promote_candidate(str(learning_db), profile_id='p', candidate_id=cand_id)
with sqlite3.connect(learning_db) as conn:
    rows = list(conn.execute("SELECT id, is_active, is_previous, is_candidate, promoted_at FROM learning_model_state WHERE profile_id='p' ORDER BY id"))
    assert len(rows) == 2
    prev_row = [r for r in rows if r[0] == active_id][0]
    new_active = [r for r in rows if r[0] == cand_id][0]
    assert prev_row[1] == 0 and prev_row[2] == 1 and (prev_row[3] == 0)
    assert new_active[1] == 1
    assert new_active[2] == 0
    assert new_active[3] == 0
    assert new_active[4] is not None
    n_active = conn.execute("SELECT COUNT(*) FROM learning_model_state WHERE profile_id='p' AND is_active=1").fetchone()[0]
    assert n_active == 1
    n_cand = conn.execute("SELECT COUNT(*) FROM learning_model_state WHERE profile_id='p' AND is_candidate=1").fetchone()[0]
    assert n_cand == 0
with pytest.raises(sqlite3.IntegrityError):
    with sqlite3.connect(learning_db) as conn:
        conn.execute("INSERT INTO learning_model_state (profile_id, state_bytes, bytes_sha256, is_active,  trained_at, updated_at) VALUES ('p', ?, ?, 1, ?, ?)", (b'boom', '0' * 64, _now_iso(), _now_iso()))
        conn.commit()
```

## Next Steps


---

*Source: test_online_retrain.py:459 | Complexity: Advanced | Last updated: 2026-05-05*