# How To: Flush On Shutdown Persists Pending

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test flush on shutdown persists pending

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
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign db = make_db_with_migrations(...)

```python
db = make_db_with_migrations(tmp_path)
```

**Verification:**
```python
assert dropped == 0
```

### Step 2: Assign worker = SignalWorker(...)

```python
worker = SignalWorker(db._db_path, batch_size=50, interval_ms=20)
```

**Verification:**
```python
assert n == 200
```

### Step 3: Call worker.start()

```python
worker.start()
```

**Verification:**
```python
assert dropped == 0
```

### Step 4: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(db._db_path)
```

### Step 5: Assign n = value

```python
n = conn.execute('SELECT COUNT(*) FROM learning_signals').fetchone()[0]
```

### Step 6: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert n == 200
```

### Step 7: Assign deadline = value

```python
deadline = time.monotonic() + 5.0
```

### Step 8: Assign dropped = worker.stop(...)

```python
dropped = worker.stop(timeout=5.0)
```

### Step 9: Call enqueue()

```python
enqueue(make_batch(query_id=f'q-{i:04d}', n_candidates=2))
```

### Step 10: Call time.sleep()

```python
time.sleep(0.02)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
db = make_db_with_migrations(tmp_path)
worker = SignalWorker(db._db_path, batch_size=50, interval_ms=20)
worker.start()
try:
    for i in range(100):
        enqueue(make_batch(query_id=f'q-{i:04d}', n_candidates=2))
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and _SIGNAL_QUEUE.qsize() > 0:
        time.sleep(0.02)
finally:
    dropped = worker.stop(timeout=5.0)
assert dropped == 0
conn = sqlite3.connect(db._db_path)
n = conn.execute('SELECT COUNT(*) FROM learning_signals').fetchone()[0]
conn.close()
assert n == 200
```

## Next Steps


---

*Source: test_signal_worker.py:48 | Complexity: Advanced | Last updated: 2026-05-05*