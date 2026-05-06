# How To: M002 Post Ddl Hook Backfills Sha256 For Legacy Rows

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: H-DATA-01: M002 post-DDL hook computes sha256 for each copied row.

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

### Step 1: 'H-DATA-01: M002 post-DDL hook computes sha256 for each copied row.'

```python
'H-DATA-01: M002 post-DDL hook computes sha256 for each copied row.'
```

**Verification:**
```python
assert by_profile['default'] == hashlib.sha256(blob_a).hexdigest()
```

### Step 2: Assign db = value

```python
db = tmp_path / 'learning.db'
```

**Verification:**
```python
assert by_profile['work'] == hashlib.sha256(blob_b).hexdigest()
```

### Step 3: Assign blob_a = value

```python
blob_a = b'learned-ranker-model-A' * 32
```

**Verification:**
```python
assert all((len(v) == 64 for v in by_profile.values()))
```

### Step 4: Assign blob_b = value

```python
blob_b = b'learned-ranker-model-B' * 32
```

### Step 5: Call _seed_v3419_learning_db()

```python
_seed_v3419_learning_db(db, [('default', blob_a), ('work', blob_b)])
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(db)
```

### Step 7: Assign by_profile = value

```python
by_profile = {pid: sha for pid, sha in rows}
```

**Verification:**
```python
assert by_profile['default'] == hashlib.sha256(blob_a).hexdigest()
```

### Step 8: Call conn.executescript()

```python
conn.executescript(M002.DDL)
```

### Step 9: Call M002.post_ddl_hook()

```python
M002.post_ddl_hook(conn)
```

### Step 10: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT profile_id, bytes_sha256 FROM learning_model_state').fetchall()
```

### Step 11: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'H-DATA-01: M002 post-DDL hook computes sha256 for each copied row.'
db = tmp_path / 'learning.db'
blob_a = b'learned-ranker-model-A' * 32
blob_b = b'learned-ranker-model-B' * 32
_seed_v3419_learning_db(db, [('default', blob_a), ('work', blob_b)])
conn = sqlite3.connect(db)
try:
    conn.executescript(M002.DDL)
    M002.post_ddl_hook(conn)
    rows = conn.execute('SELECT profile_id, bytes_sha256 FROM learning_model_state').fetchall()
finally:
    conn.close()
by_profile = {pid: sha for pid, sha in rows}
assert by_profile['default'] == hashlib.sha256(blob_a).hexdigest()
assert by_profile['work'] == hashlib.sha256(blob_b).hexdigest()
assert all((len(v) == 64 for v in by_profile.values()))
```

## Next Steps


---

*Source: test_s9_w1_data_integrity.py:66 | Complexity: Advanced | Last updated: 2026-05-05*