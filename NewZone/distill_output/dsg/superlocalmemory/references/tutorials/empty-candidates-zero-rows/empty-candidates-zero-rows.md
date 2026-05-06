# How To: Empty Candidates Zero Rows

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test empty candidates zero rows

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `threading`
- `time`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `queue`
- `superlocalmemory.learning.features`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db = make_db_with_migrations(...)

```python
db = make_db_with_migrations(tmp_path)
```

**Verification:**
```python
assert result == []
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

**Verification:**
```python
assert n == 0
```

### Step 3: Assign batch = make_batch(...)

```python
batch = make_batch(n_candidates=0)
```

**Verification:**
```python
assert n == 0
```

### Step 4: Assign result = record_signal_batch(...)

```python
result = record_signal_batch(conn, batch)
```

**Verification:**
```python
assert result == []
```

### Step 5: Assign n = value

```python
n = conn.execute('SELECT COUNT(*) FROM learning_signals').fetchone()[0]
```

**Verification:**
```python
assert n == 0
```

### Step 6: Assign n = value

```python
n = conn.execute('SELECT COUNT(*) FROM learning_features').fetchone()[0]
```

**Verification:**
```python
assert n == 0
```

### Step 7: Call conn.close()

```python
conn.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
conn = open_conn(db)
batch = make_batch(n_candidates=0)
result = record_signal_batch(conn, batch)
assert result == []
n = conn.execute('SELECT COUNT(*) FROM learning_signals').fetchone()[0]
assert n == 0
n = conn.execute('SELECT COUNT(*) FROM learning_features').fetchone()[0]
assert n == 0
conn.close()
```

## Next Steps


---

*Source: test_signals_pipeline.py:115 | Complexity: Intermediate | Last updated: 2026-05-05*