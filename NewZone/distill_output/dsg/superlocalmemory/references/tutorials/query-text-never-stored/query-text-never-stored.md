# How To: Query Text Never Stored

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test query text never stored

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
assert d['query'] == ''
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

**Verification:**
```python
assert len(d['query_text_hash']) == 32
```

### Step 3: Assign secret = 'AKIAsecretthatmustnotleak12345'

```python
secret = 'AKIAsecretthatmustnotleak12345'
```

**Verification:**
```python
assert d['query_text_hash'] == _hash_query(secret)
```

### Step 4: Assign batch = make_batch(...)

```python
batch = make_batch(query_text=secret, n_candidates=2)
```

**Verification:**
```python
assert secret not in d['query_text_hash']
```

### Step 5: Call record_signal_batch()

```python
record_signal_batch(conn, batch)
```

### Step 6: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT query, query_text_hash FROM learning_signals').fetchall()
```

### Step 7: Call conn.close()

```python
conn.close()
```

### Step 8: Assign d = dict(...)

```python
d = dict(r)
```

**Verification:**
```python
assert d['query'] == ''
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
conn = open_conn(db)
secret = 'AKIAsecretthatmustnotleak12345'
batch = make_batch(query_text=secret, n_candidates=2)
record_signal_batch(conn, batch)
rows = conn.execute('SELECT query, query_text_hash FROM learning_signals').fetchall()
for r in rows:
    d = dict(r)
    assert d['query'] == ''
    assert len(d['query_text_hash']) == 32
    assert d['query_text_hash'] == _hash_query(secret)
    assert secret not in d['query_text_hash']
conn.close()
```

## Next Steps


---

*Source: test_signals_pipeline.py:90 | Complexity: Advanced | Last updated: 2026-05-05*