# How To: Write Is Atomic On Feature Insert Failure

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test write is atomic on feature insert failure

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
assert n == 0
```

### Step 2: Assign real_conn = open_conn(...)

```python
real_conn = open_conn(db)
```

**Verification:**
```python
assert n == 0
```

### Step 3: Assign wrapped = _FailingConnWrapper(...)

```python
wrapped = _FailingConnWrapper(real_conn)
```

### Step 4: Assign batch = make_batch(...)

```python
batch = make_batch(n_candidates=3)
```

### Step 5: Assign n = value

```python
n = real_conn.execute('SELECT COUNT(*) FROM learning_signals').fetchone()[0]
```

**Verification:**
```python
assert n == 0
```

### Step 6: Assign n = value

```python
n = real_conn.execute('SELECT COUNT(*) FROM learning_features').fetchone()[0]
```

**Verification:**
```python
assert n == 0
```

### Step 7: Call real_conn.close()

```python
real_conn.close()
```

### Step 8: Call record_signal_batch()

```python
record_signal_batch(wrapped, batch)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
real_conn = open_conn(db)
wrapped = _FailingConnWrapper(real_conn)
batch = make_batch(n_candidates=3)
with pytest.raises(sqlite3.OperationalError):
    record_signal_batch(wrapped, batch)
n = real_conn.execute('SELECT COUNT(*) FROM learning_signals').fetchone()[0]
assert n == 0
n = real_conn.execute('SELECT COUNT(*) FROM learning_features').fetchone()[0]
assert n == 0
real_conn.close()
```

## Next Steps


---

*Source: test_signals_pipeline.py:164 | Complexity: Advanced | Last updated: 2026-05-05*