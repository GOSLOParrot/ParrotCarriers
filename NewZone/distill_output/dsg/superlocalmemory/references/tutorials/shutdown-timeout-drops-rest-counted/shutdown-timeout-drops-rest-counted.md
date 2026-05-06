# How To: Shutdown Timeout Drops Rest Counted

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test shutdown timeout drops rest counted

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

### Step 1: Call monkeypatch.setattr()

```python
monkeypatch.setattr(signals_mod, '_Q', big_q)
```

**Verification:**
```python
assert dropped >= 1
```

### Step 2: Call reset_counters()

```python
reset_counters()
```

**Verification:**
```python
assert counters['signal_drop_on_flush_total'] == dropped
```

### Step 3: Assign db = make_db_with_migrations(...)

```python
db = make_db_with_migrations(tmp_path)
```

### Step 4: Assign worker = SignalWorker(...)

```python
worker = SignalWorker(db._db_path, batch_size=1, interval_ms=10)
```

### Step 5: Call worker.start()

```python
worker.start()
```

### Step 6: Assign dropped = worker.stop(...)

```python
dropped = worker.stop(timeout=0.1)
```

### Step 7: Assign counters = get_counters(...)

```python
counters = get_counters()
```

**Verification:**
```python
assert dropped >= 1
```

### Step 8: Call enqueue()

```python
enqueue(make_batch(query_id=f'q-{i}', n_candidates=0))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
big_q: 'queue.Queue' = queue.Queue(maxsize=20000)
monkeypatch.setattr(signals_mod, '_Q', big_q)
reset_counters()
db = make_db_with_migrations(tmp_path)
worker = SignalWorker(db._db_path, batch_size=1, interval_ms=10)
for i in range(10000):
    enqueue(make_batch(query_id=f'q-{i}', n_candidates=0))
worker.start()
dropped = worker.stop(timeout=0.1)
counters = get_counters()
assert dropped >= 1
assert counters['signal_drop_on_flush_total'] == dropped
```

## Next Steps


---

*Source: test_signal_worker.py:77 | Complexity: Advanced | Last updated: 2026-05-05*