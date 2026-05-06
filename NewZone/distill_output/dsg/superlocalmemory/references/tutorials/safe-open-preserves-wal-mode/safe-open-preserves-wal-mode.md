# How To: Safe Open Preserves Wal Mode

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test safe open preserves wal mode

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
assert mode.lower() == 'wal'
```

### Step 2: Assign db = value

```python
db = tmp_path / 't.db'
```

**Verification:**
```python
assert conn2.execute('SELECT x FROM t').fetchone()[0] == 42
```

### Step 3: Assign conn = sf._safe_open_db(...)

```python
conn = sf._safe_open_db(db)
```

### Step 4: Assign conn2 = sf._safe_open_db(...)

```python
conn2 = sf._safe_open_db(db)
```

### Step 5: Assign mode = value

```python
mode = conn.execute('PRAGMA journal_mode=WAL').fetchone()[0]
```

**Verification:**
```python
assert mode.lower() == 'wal'
```

### Step 6: Call conn.execute()

```python
conn.execute('CREATE TABLE t (x INTEGER)')
```

### Step 7: Call conn.execute()

```python
conn.execute('INSERT INTO t VALUES (42)')
```

### Step 8: Call conn.commit()

```python
conn.commit()
```

### Step 9: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert conn2.execute('SELECT x FROM t').fetchone()[0] == 42
```

### Step 10: Call conn2.close()

```python
conn2.close()
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
    mode = conn.execute('PRAGMA journal_mode=WAL').fetchone()[0]
    assert mode.lower() == 'wal'
    conn.execute('CREATE TABLE t (x INTEGER)')
    conn.execute('INSERT INTO t VALUES (42)')
    conn.commit()
finally:
    conn.close()
conn2 = sf._safe_open_db(db)
try:
    assert conn2.execute('SELECT x FROM t').fetchone()[0] == 42
finally:
    conn2.close()
```

## Next Steps


---

*Source: test_safe_fs.py:43 | Complexity: Advanced | Last updated: 2026-05-05*