# How To: Writer Excludes Readers

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test writer excludes readers

## Prerequisites

**Required Modules:**
- `__future__`
- `threading`
- `time`
- `pytest`
- `superlocalmemory.core.engine_lock`


## Step-by-Step Guide

### Step 1: Assign EngineRWLock = _import_lock(...)

```python
EngineRWLock = _import_lock()
```

**Verification:**
```python
assert writer_in.wait(timeout=1.0), 'Writer did not acquire'
```

### Step 2: Assign lock = EngineRWLock(...)

```python
lock = EngineRWLock()
```

**Verification:**
```python
assert not reader_in.wait(timeout=0.2), 'Reader entered during writer'
```

### Step 3: Assign writer_in = threading.Event(...)

```python
writer_in = threading.Event()
```

**Verification:**
```python
assert reader_in.is_set(), 'Reader never got in after writer released'
```

### Step 4: Assign reader_in = threading.Event(...)

```python
reader_in = threading.Event()
```

### Step 5: Assign writer_hold = threading.Event(...)

```python
writer_hold = threading.Event()
```

### Step 6: Assign w = threading.Thread(...)

```python
w = threading.Thread(target=writer)
```

### Step 7: Call w.start()

```python
w.start()
```

**Verification:**
```python
assert writer_in.wait(timeout=1.0), 'Writer did not acquire'
```

### Step 8: Assign r = threading.Thread(...)

```python
r = threading.Thread(target=reader)
```

### Step 9: Call r.start()

```python
r.start()
```

**Verification:**
```python
assert not reader_in.wait(timeout=0.2), 'Reader entered during writer'
```

### Step 10: Call writer_hold.set()

```python
writer_hold.set()
```

### Step 11: Call r.join()

```python
r.join(timeout=1.0)
```

### Step 12: Call w.join()

```python
w.join(timeout=1.0)
```

**Verification:**
```python
assert reader_in.is_set(), 'Reader never got in after writer released'
```

### Step 13: Call writer_in.set()

```python
writer_in.set()
```

### Step 14: Call writer_hold.wait()

```python
writer_hold.wait(timeout=2.0)
```

### Step 15: Call reader_in.set()

```python
reader_in.set()
```


## Complete Example

```python
# Workflow
EngineRWLock = _import_lock()
lock = EngineRWLock()
writer_in = threading.Event()
reader_in = threading.Event()
writer_hold = threading.Event()

def writer() -> None:
    with lock.write():
        writer_in.set()
        writer_hold.wait(timeout=2.0)

def reader() -> None:
    with lock.read():
        reader_in.set()
w = threading.Thread(target=writer)
w.start()
assert writer_in.wait(timeout=1.0), 'Writer did not acquire'
r = threading.Thread(target=reader)
r.start()
assert not reader_in.wait(timeout=0.2), 'Reader entered during writer'
writer_hold.set()
r.join(timeout=1.0)
w.join(timeout=1.0)
assert reader_in.is_set(), 'Reader never got in after writer released'
```

## Next Steps


---

*Source: test_engine_lock.py:49 | Complexity: Advanced | Last updated: 2026-05-05*