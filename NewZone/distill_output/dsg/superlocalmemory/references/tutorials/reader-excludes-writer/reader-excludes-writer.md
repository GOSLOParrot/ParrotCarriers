# How To: Reader Excludes Writer

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test reader excludes writer

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
assert reader_in.wait(timeout=1.0)
```

### Step 2: Assign lock = EngineRWLock(...)

```python
lock = EngineRWLock()
```

**Verification:**
```python
assert not writer_in.wait(timeout=0.2), 'Writer entered during reader'
```

### Step 3: Assign reader_in = threading.Event(...)

```python
reader_in = threading.Event()
```

**Verification:**
```python
assert writer_in.is_set(), 'Writer never got in after reader released'
```

### Step 4: Assign writer_in = threading.Event(...)

```python
writer_in = threading.Event()
```

### Step 5: Assign reader_hold = threading.Event(...)

```python
reader_hold = threading.Event()
```

### Step 6: Assign r = threading.Thread(...)

```python
r = threading.Thread(target=reader)
```

### Step 7: Call r.start()

```python
r.start()
```

**Verification:**
```python
assert reader_in.wait(timeout=1.0)
```

### Step 8: Assign w = threading.Thread(...)

```python
w = threading.Thread(target=writer)
```

### Step 9: Call w.start()

```python
w.start()
```

**Verification:**
```python
assert not writer_in.wait(timeout=0.2), 'Writer entered during reader'
```

### Step 10: Call reader_hold.set()

```python
reader_hold.set()
```

### Step 11: Call w.join()

```python
w.join(timeout=1.0)
```

### Step 12: Call r.join()

```python
r.join(timeout=1.0)
```

**Verification:**
```python
assert writer_in.is_set(), 'Writer never got in after reader released'
```

### Step 13: Call reader_in.set()

```python
reader_in.set()
```

### Step 14: Call reader_hold.wait()

```python
reader_hold.wait(timeout=2.0)
```

### Step 15: Call writer_in.set()

```python
writer_in.set()
```


## Complete Example

```python
# Workflow
EngineRWLock = _import_lock()
lock = EngineRWLock()
reader_in = threading.Event()
writer_in = threading.Event()
reader_hold = threading.Event()

def reader() -> None:
    with lock.read():
        reader_in.set()
        reader_hold.wait(timeout=2.0)

def writer() -> None:
    with lock.write():
        writer_in.set()
r = threading.Thread(target=reader)
r.start()
assert reader_in.wait(timeout=1.0)
w = threading.Thread(target=writer)
w.start()
assert not writer_in.wait(timeout=0.2), 'Writer entered during reader'
reader_hold.set()
w.join(timeout=1.0)
r.join(timeout=1.0)
assert writer_in.is_set(), 'Writer never got in after reader released'
```

## Next Steps


---

*Source: test_engine_lock.py:77 | Complexity: Advanced | Last updated: 2026-05-05*