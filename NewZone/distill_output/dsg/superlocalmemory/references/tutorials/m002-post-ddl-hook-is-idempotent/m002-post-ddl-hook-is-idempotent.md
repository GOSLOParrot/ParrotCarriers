# How To: M002 Post Ddl Hook Is Idempotent

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Re-running the hook on already-populated rows is a no-op.

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

### Step 1: 'Re-running the hook on already-populated rows is a no-op.'

```python
'Re-running the hook on already-populated rows is a no-op.'
```

**Verification:**
```python
assert first == second
```

### Step 2: Assign db = value

```python
db = tmp_path / 'learning.db'
```

**Verification:**
```python
assert first == hashlib.sha256(b'x' * 256).hexdigest()
```

### Step 3: Call _seed_v3419_learning_db()

```python
_seed_v3419_learning_db(db, [('solo', b'x' * 256)])
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(db)
```

**Verification:**
```python
assert first == second
```

### Step 5: Call conn.executescript()

```python
conn.executescript(M002.DDL)
```

### Step 6: Call M002.post_ddl_hook()

```python
M002.post_ddl_hook(conn)
```

### Step 7: Assign first = value

```python
first = conn.execute('SELECT bytes_sha256 FROM learning_model_state').fetchone()[0]
```

### Step 8: Call M002.post_ddl_hook()

```python
M002.post_ddl_hook(conn)
```

### Step 9: Assign second = value

```python
second = conn.execute('SELECT bytes_sha256 FROM learning_model_state').fetchone()[0]
```

### Step 10: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Re-running the hook on already-populated rows is a no-op.'
db = tmp_path / 'learning.db'
_seed_v3419_learning_db(db, [('solo', b'x' * 256)])
conn = sqlite3.connect(db)
try:
    conn.executescript(M002.DDL)
    M002.post_ddl_hook(conn)
    first = conn.execute('SELECT bytes_sha256 FROM learning_model_state').fetchone()[0]
    M002.post_ddl_hook(conn)
    second = conn.execute('SELECT bytes_sha256 FROM learning_model_state').fetchone()[0]
finally:
    conn.close()
assert first == second
assert first == hashlib.sha256(b'x' * 256).hexdigest()
```

## Next Steps


---

*Source: test_s9_w1_data_integrity.py:92 | Complexity: Advanced | Last updated: 2026-05-05*