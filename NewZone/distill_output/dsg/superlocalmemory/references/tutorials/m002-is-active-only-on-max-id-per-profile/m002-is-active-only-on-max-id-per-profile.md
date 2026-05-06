# How To: M002 Is Active Only On Max Id Per Profile

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Dev-build path: multiple rows per profile_id must land with only
the MAX(id) row marked active; the partial unique index must hold.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `sqlite3`
- `pathlib`
- `pytest`
- `superlocalmemory.storage`
- `superlocalmemory.storage.migrations`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Dev-build path: multiple rows per profile_id must land with only\n    the MAX(id) row marked active; the partial unique index must hold.'

```python
'Dev-build path: multiple rows per profile_id must land with only\n    the MAX(id) row marked active; the partial unique index must hold.'
```

**Verification:**
```python
assert total == 3, 'all three rows should be copied forward'
```

### Step 2: Assign db = value

```python
db = tmp_path / 'learning.db'
```

**Verification:**
```python
assert active_count == 1, 'partial unique index requires 1 active'
```

### Step 3: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(db)
```

**Verification:**
```python
assert active_id == 3, 'the newest (MAX(id)) row should be active'
```

### Step 4: Call conn.executescript()

```python
conn.executescript('\n            CREATE TABLE learning_model_state (\n                id          INTEGER PRIMARY KEY AUTOINCREMENT,\n                profile_id  TEXT NOT NULL,\n                state_bytes BLOB NOT NULL,\n                updated_at  TEXT NOT NULL\n            );\n        ')
```

### Step 5: Call conn.commit()

```python
conn.commit()
```

### Step 6: Call conn.executescript()

```python
conn.executescript(M002.DDL)
```

### Step 7: Call M002.post_ddl_hook()

```python
M002.post_ddl_hook(conn)
```

### Step 8: Assign active_count = value

```python
active_count = conn.execute('SELECT COUNT(*) FROM learning_model_state WHERE is_active = 1').fetchone()[0]
```

### Step 9: Assign total = value

```python
total = conn.execute('SELECT COUNT(*) FROM learning_model_state').fetchone()[0]
```

### Step 10: Assign active_id = value

```python
active_id = conn.execute('SELECT id FROM learning_model_state WHERE is_active = 1').fetchone()[0]
```

### Step 11: Call conn.close()

```python
conn.close()
```

### Step 12: Call conn.execute()

```python
conn.execute('INSERT INTO learning_model_state (profile_id, state_bytes, updated_at) VALUES (?, ?, ?)', ('default', f'blob-{i}'.encode() * 64, f'2026-04-{i + 1:02d}T00:00:00Z'))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Dev-build path: multiple rows per profile_id must land with only\n    the MAX(id) row marked active; the partial unique index must hold.'
db = tmp_path / 'learning.db'
conn = sqlite3.connect(db)
try:
    conn.executescript('\n            CREATE TABLE learning_model_state (\n                id          INTEGER PRIMARY KEY AUTOINCREMENT,\n                profile_id  TEXT NOT NULL,\n                state_bytes BLOB NOT NULL,\n                updated_at  TEXT NOT NULL\n            );\n        ')
    for i in range(3):
        conn.execute('INSERT INTO learning_model_state (profile_id, state_bytes, updated_at) VALUES (?, ?, ?)', ('default', f'blob-{i}'.encode() * 64, f'2026-04-{i + 1:02d}T00:00:00Z'))
    conn.commit()
    conn.executescript(M002.DDL)
    M002.post_ddl_hook(conn)
    active_count = conn.execute('SELECT COUNT(*) FROM learning_model_state WHERE is_active = 1').fetchone()[0]
    total = conn.execute('SELECT COUNT(*) FROM learning_model_state').fetchone()[0]
    active_id = conn.execute('SELECT id FROM learning_model_state WHERE is_active = 1').fetchone()[0]
finally:
    conn.close()
assert total == 3, 'all three rows should be copied forward'
assert active_count == 1, 'partial unique index requires 1 active'
assert active_id == 3, 'the newest (MAX(id)) row should be active'
```

## Next Steps


---

*Source: test_s9_w1_data_integrity.py:140 | Complexity: Advanced | Last updated: 2026-05-05*