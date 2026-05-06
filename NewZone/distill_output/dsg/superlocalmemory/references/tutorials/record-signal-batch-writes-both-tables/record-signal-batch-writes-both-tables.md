# How To: Record Signal Batch Writes Both Tables

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test record signal batch writes both tables

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
assert len(ids) == 5
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

**Verification:**
```python
assert all((isinstance(i, int) for i in ids))
```

### Step 3: Assign batch = make_batch(...)

```python
batch = make_batch(n_candidates=5)
```

**Verification:**
```python
assert len(sig_rows) == 5
```

### Step 4: Assign ids = record_signal_batch(...)

```python
ids = record_signal_batch(conn, batch)
```

**Verification:**
```python
assert d['position'] == i
```

### Step 5: Assign sig_rows = conn.execute.fetchall(...)

```python
sig_rows = conn.execute('SELECT id, fact_id, query_id, position, signal_type, query,        query_text_hash, channel_scores, cross_encoder FROM learning_signals ORDER BY id').fetchall()
```

**Verification:**
```python
assert d['signal_type'] == 'candidate'
```

### Step 6: Assign feat_rows = conn.execute.fetchall(...)

```python
feat_rows = conn.execute('SELECT signal_id, features_json, is_synthetic FROM learning_features ORDER BY id').fetchall()
```

**Verification:**
```python
assert len(feat_rows) == 5
```

### Step 7: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert {dict(r)['signal_id'] for r in feat_rows} == set(ids)
```

### Step 8: Assign d = dict(...)

```python
d = dict(r)
```

**Verification:**
```python
assert len(parsed) == 20
```

### Step 9: Assign parsed = json.loads(...)

```python
parsed = json.loads(dict(r)['features_json'])
```

**Verification:**
```python
assert dict(r)['is_synthetic'] == 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
conn = open_conn(db)
batch = make_batch(n_candidates=5)
ids = record_signal_batch(conn, batch)
assert len(ids) == 5
assert all((isinstance(i, int) for i in ids))
sig_rows = conn.execute('SELECT id, fact_id, query_id, position, signal_type, query,        query_text_hash, channel_scores, cross_encoder FROM learning_signals ORDER BY id').fetchall()
assert len(sig_rows) == 5
for i, r in enumerate(sig_rows):
    d = dict(r)
    assert d['position'] == i
    assert d['signal_type'] == 'candidate'
feat_rows = conn.execute('SELECT signal_id, features_json, is_synthetic FROM learning_features ORDER BY id').fetchall()
assert len(feat_rows) == 5
assert {dict(r)['signal_id'] for r in feat_rows} == set(ids)
for r in feat_rows:
    parsed = json.loads(dict(r)['features_json'])
    assert len(parsed) == 20
    assert dict(r)['is_synthetic'] == 0
conn.close()
```

## Next Steps


---

*Source: test_signals_pipeline.py:52 | Complexity: Advanced | Last updated: 2026-05-05*