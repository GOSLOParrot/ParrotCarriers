# How To: Drain Once Drops When Retry Exhausted

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: _drain_once bumps signal_dropped_total when _write_with_retry gives up.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `queue`
- `sqlite3`
- `threading`
- `time`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.signal_worker`
- `superlocalmemory.learning.signals`
- `tests.test_learning._signal_fixtures`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: '_drain_once bumps signal_dropped_total when _write_with_retry gives up.'

```python
'_drain_once bumps signal_dropped_total when _write_with_retry gives up.'
```

**Verification:**
```python
assert written == 0
```

### Step 2: Assign db = make_db_with_migrations(...)

```python
db = make_db_with_migrations(tmp_path)
```

**Verification:**
```python
assert get_counters()['signal_dropped_total'] >= 1
```

### Step 3: Assign worker = SignalWorker(...)

```python
worker = SignalWorker(db._db_path, batch_size=2, interval_ms=10)
```

### Step 4: Call enqueue()

```python
enqueue(make_batch(query_id='q-drop', n_candidates=1))
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr(worker_mod, '_write_with_retry', lambda conn, batch, attempts=3: False)
```

### Step 6: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(db._db_path, isolation_level=None)
```

### Step 7: Call reset_counters()

```python
reset_counters()
```

### Step 8: Assign written = worker._drain_once(...)

```python
written = worker._drain_once(conn)
```

### Step 9: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert written == 0
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'_drain_once bumps signal_dropped_total when _write_with_retry gives up.'
from superlocalmemory.learning import signal_worker as worker_mod
db = make_db_with_migrations(tmp_path)
worker = SignalWorker(db._db_path, batch_size=2, interval_ms=10)
enqueue(make_batch(query_id='q-drop', n_candidates=1))
monkeypatch.setattr(worker_mod, '_write_with_retry', lambda conn, batch, attempts=3: False)
conn = sqlite3.connect(db._db_path, isolation_level=None)
reset_counters()
written = worker._drain_once(conn)
conn.close()
assert written == 0
assert get_counters()['signal_dropped_total'] >= 1
```

## Next Steps


---

*Source: test_signal_worker.py:196 | Complexity: Advanced | Last updated: 2026-05-05*