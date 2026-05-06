# How To: Shown Flip Not Fake Positive

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test shown flip not fake positive

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
assert by_fid['fact-000'] == 'shown'
```

### Step 2: Assign conn = open_conn(...)

```python
conn = open_conn(db)
```

**Verification:**
```python
assert by_fid['fact-001'] == 'not_shown'
```

### Step 3: Assign batch = make_batch(...)

```python
batch = make_batch(n_candidates=3, query_id='q-honest')
```

**Verification:**
```python
assert by_fid['fact-002'] == 'candidate'
```

### Step 4: Call record_signal_batch()

```python
record_signal_batch(conn, batch)
```

**Verification:**
```python
assert all((dict(r)['label'] == 0.0 for r in feat))
```

### Step 5: Assign shown_batch = SignalBatch(...)

```python
shown_batch = SignalBatch(profile_id='', query_id='q-honest', query_text='', candidates=(), query_context={'_shown_flip': {'fact_id': 'fact-000', 'shown': True}})
```

### Step 6: Call record_signal_batch()

```python
record_signal_batch(conn, shown_batch)
```

### Step 7: Assign not_shown_batch = SignalBatch(...)

```python
not_shown_batch = SignalBatch(profile_id='', query_id='q-honest', query_text='', candidates=(), query_context={'_shown_flip': {'fact_id': 'fact-001', 'shown': False}})
```

### Step 8: Call record_signal_batch()

```python
record_signal_batch(conn, not_shown_batch)
```

### Step 9: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute("SELECT fact_id, signal_type FROM learning_signals WHERE query_id = 'q-honest' ORDER BY position").fetchall()
```

### Step 10: Assign by_fid = value

```python
by_fid = {dict(r)['fact_id']: dict(r)['signal_type'] for r in rows}
```

**Verification:**
```python
assert by_fid['fact-000'] == 'shown'
```

### Step 11: Assign feat = conn.execute.fetchall(...)

```python
feat = conn.execute('SELECT label FROM learning_features').fetchall()
```

**Verification:**
```python
assert all((dict(r)['label'] == 0.0 for r in feat))
```

### Step 12: Call conn.close()

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
batch = make_batch(n_candidates=3, query_id='q-honest')
record_signal_batch(conn, batch)
shown_batch = SignalBatch(profile_id='', query_id='q-honest', query_text='', candidates=(), query_context={'_shown_flip': {'fact_id': 'fact-000', 'shown': True}})
record_signal_batch(conn, shown_batch)
not_shown_batch = SignalBatch(profile_id='', query_id='q-honest', query_text='', candidates=(), query_context={'_shown_flip': {'fact_id': 'fact-001', 'shown': False}})
record_signal_batch(conn, not_shown_batch)
rows = conn.execute("SELECT fact_id, signal_type FROM learning_signals WHERE query_id = 'q-honest' ORDER BY position").fetchall()
by_fid = {dict(r)['fact_id']: dict(r)['signal_type'] for r in rows}
assert by_fid['fact-000'] == 'shown'
assert by_fid['fact-001'] == 'not_shown'
assert by_fid['fact-002'] == 'candidate'
feat = conn.execute('SELECT label FROM learning_features').fetchall()
assert all((dict(r)['label'] == 0.0 for r in feat))
conn.close()
```

## Next Steps


---

*Source: test_signals_pipeline.py:223 | Complexity: Advanced | Last updated: 2026-05-05*