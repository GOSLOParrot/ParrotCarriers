# How To: Migration Runner Calls Post Ddl Hook After Successful Ddl

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: C3+H-DATA-01 plumbing: the runner must invoke a migration's
``post_ddl_hook`` exactly once after the DDL commits.

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

### Step 1: "C3+H-DATA-01 plumbing: the runner must invoke a migration's\n    ``post_ddl_hook`` exactly once after the DDL commits."

```python
"C3+H-DATA-01 plumbing: the runner must invoke a migration's\n    ``post_ddl_hook`` exactly once after the DDL commits."
```

**Verification:**
```python
assert 'M002_model_state_history' in result['applied']
```

### Step 2: Assign learning_db = value

```python
learning_db = tmp_path / 'learning.db'
```

**Verification:**
```python
assert len(sha) == 64, f'profile {pid} missing sha backfill'
```

### Step 3: Assign memory_db = value

```python
memory_db = tmp_path / 'memory.db'
```

### Step 4: Call _seed_v3419_learning_db()

```python
_seed_v3419_learning_db(learning_db, [('p1', b'model-p1' * 128), ('p2', b'model-p2' * 128)])
```

### Step 5: Assign result = migration_runner.apply_all(...)

```python
result = migration_runner.apply_all(learning_db, memory_db)
```

**Verification:**
```python
assert 'M002_model_state_history' in result['applied']
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(learning_db)
```

### Step 7: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT profile_id, bytes_sha256 FROM learning_model_state').fetchall()
```

### Step 8: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert len(sha) == 64, f'profile {pid} missing sha backfill'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
"C3+H-DATA-01 plumbing: the runner must invoke a migration's\n    ``post_ddl_hook`` exactly once after the DDL commits."
learning_db = tmp_path / 'learning.db'
memory_db = tmp_path / 'memory.db'
_seed_v3419_learning_db(learning_db, [('p1', b'model-p1' * 128), ('p2', b'model-p2' * 128)])
result = migration_runner.apply_all(learning_db, memory_db)
assert 'M002_model_state_history' in result['applied']
conn = sqlite3.connect(learning_db)
try:
    rows = conn.execute('SELECT profile_id, bytes_sha256 FROM learning_model_state').fetchall()
finally:
    conn.close()
for pid, sha in rows:
    assert len(sha) == 64, f'profile {pid} missing sha backfill'
```

## Next Steps


---

*Source: test_s9_w1_data_integrity.py:192 | Complexity: Advanced | Last updated: 2026-05-05*