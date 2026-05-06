# How To: Safe Open Creates Db With Mode 0600

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test safe open creates db with mode 0600

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `stat`
- `sqlite3`
- `sys`
- `pathlib`
- `pytest`
- `superlocalmemory.core.safe_fs`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign sf = _import_module(...)

```python
sf = _import_module()
```

**Verification:**
```python
assert cur.fetchone()[0] == 1
```

### Step 2: Assign db = value

```python
db = tmp_path / 't.db'
```

**Verification:**
```python
assert db.exists()
```

### Step 3: Assign conn = sf._safe_open_db(...)

```python
conn = sf._safe_open_db(db)
```

**Verification:**
```python
assert stat.S_IMODE(st.st_mode) == 384, f'Mode is {oct(st.st_mode)}'
```

### Step 4: Assign st = db.stat(...)

```python
st = db.stat()
```

**Verification:**
```python
assert stat.S_IMODE(st.st_mode) == 384, f'Mode is {oct(st.st_mode)}'
```

### Step 5: Call conn.execute()

```python
conn.execute('CREATE TABLE t (x INTEGER)')
```

### Step 6: Call conn.execute()

```python
conn.execute('INSERT INTO t VALUES (1)')
```

### Step 7: Assign cur = conn.execute(...)

```python
cur = conn.execute('SELECT x FROM t')
```

**Verification:**
```python
assert cur.fetchone()[0] == 1
```

### Step 8: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
sf = _import_module()
db = tmp_path / 't.db'
conn = sf._safe_open_db(db)
try:
    conn.execute('CREATE TABLE t (x INTEGER)')
    conn.execute('INSERT INTO t VALUES (1)')
    cur = conn.execute('SELECT x FROM t')
    assert cur.fetchone()[0] == 1
finally:
    conn.close()
assert db.exists()
st = db.stat()
assert stat.S_IMODE(st.st_mode) == 384, f'Mode is {oct(st.st_mode)}'
```

## Next Steps


---

*Source: test_safe_fs.py:27 | Complexity: Advanced | Last updated: 2026-05-05*