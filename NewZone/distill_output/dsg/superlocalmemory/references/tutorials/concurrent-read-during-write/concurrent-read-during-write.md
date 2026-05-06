# How To: Concurrent Read During Write

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Reads should not block during writes (WAL mode).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `threading`
- `time`
- `pathlib`
- `concurrent.futures`
- `pytest`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: 'Reads should not block during writes (WAL mode).'

```python
'Reads should not block during writes (WAL mode).'
```

**Verification:**
```python
assert len(read_results) > 0
```

### Step 2: Assign write_done = threading.Event(...)

```python
write_done = threading.Event()
```

**Verification:**
```python
assert db.get_fact_count('default') == 15
```

### Step 3: Assign read_done = threading.Event(...)

```python
read_done = threading.Event()
```

### Step 4: Assign w = threading.Thread(...)

```python
w = threading.Thread(target=_writer)
```

### Step 5: Assign r = threading.Thread(...)

```python
r = threading.Thread(target=_reader)
```

### Step 6: Call r.start()

```python
r.start()
```

### Step 7: Call w.start()

```python
w.start()
```

### Step 8: Call w.join()

```python
w.join(timeout=30)
```

### Step 9: Call r.join()

```python
r.join(timeout=5)
```

**Verification:**
```python
assert len(read_results) > 0
```

### Step 10: Call _store_fact_with_parent()

```python
_store_fact_with_parent(db, n=i)
```

### Step 11: Call write_done.set()

```python
write_done.set()
```

### Step 12: Call read_done.set()

```python
read_done.set()
```

### Step 13: Call _store_fact_with_parent()

```python
_store_fact_with_parent(db, n=i)
```

### Step 14: Call time.sleep()

```python
time.sleep(0.01)
```

### Step 15: Assign facts = db.get_all_facts(...)

```python
facts = db.get_all_facts('default')
```

### Step 16: Call read_results.append()

```python
read_results.append(len(facts))
```

### Step 17: Call time.sleep()

```python
time.sleep(0.005)
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
'Reads should not block during writes (WAL mode).'
for i in range(5):
    _store_fact_with_parent(db, n=i)
read_results: list[int] = []
write_done = threading.Event()
read_done = threading.Event()

def _writer() -> None:
    for i in range(5, 15):
        _store_fact_with_parent(db, n=i)
        time.sleep(0.01)
    write_done.set()

def _reader() -> None:
    while not write_done.is_set():
        facts = db.get_all_facts('default')
        read_results.append(len(facts))
        time.sleep(0.005)
    read_done.set()
w = threading.Thread(target=_writer)
r = threading.Thread(target=_reader)
r.start()
w.start()
w.join(timeout=30)
r.join(timeout=5)
assert len(read_results) > 0
assert db.get_fact_count('default') == 15
```

## Next Steps


---

*Source: test_concurrent_db.py:121 | Complexity: Advanced | Last updated: 2026-05-05*