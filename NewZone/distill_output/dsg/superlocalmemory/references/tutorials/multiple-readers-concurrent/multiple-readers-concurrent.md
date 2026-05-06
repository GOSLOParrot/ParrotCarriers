# How To: Multiple Readers Concurrent

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test multiple readers concurrent

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
assert not errors, f'Reader thread raised: {errors}'
```

### Step 2: Assign lock = EngineRWLock(...)

```python
lock = EngineRWLock()
```

### Step 3: Assign inside_barrier = threading.Barrier(...)

```python
inside_barrier = threading.Barrier(3, timeout=2.0)
```

### Step 4: Assign exit_event = threading.Event(...)

```python
exit_event = threading.Event()
```

### Step 5: Assign threads = value

```python
threads = [threading.Thread(target=reader) for _ in range(3)]
```

### Step 6: Call time.sleep()

```python
time.sleep(0.2)
```

### Step 7: Call exit_event.set()

```python
exit_event.set()
```

**Verification:**
```python
assert not errors, f'Reader thread raised: {errors}'
```

### Step 8: Call t.start()

```python
t.start()
```

### Step 9: Call t.join()

```python
t.join(timeout=2.0)
```

### Step 10: Call inside_barrier.wait()

```python
inside_barrier.wait()
```

### Step 11: Call exit_event.wait()

```python
exit_event.wait(timeout=2.0)
```

### Step 12: Call errors.append()

```python
errors.append(exc)
```


## Complete Example

```python
# Workflow
EngineRWLock = _import_lock()
lock = EngineRWLock()
inside_barrier = threading.Barrier(3, timeout=2.0)
exit_event = threading.Event()
errors: list[BaseException] = []

def reader() -> None:
    try:
        with lock.read():
            inside_barrier.wait()
            exit_event.wait(timeout=2.0)
    except BaseException as exc:
        errors.append(exc)
threads = [threading.Thread(target=reader) for _ in range(3)]
for t in threads:
    t.start()
time.sleep(0.2)
exit_event.set()
for t in threads:
    t.join(timeout=2.0)
assert not errors, f'Reader thread raised: {errors}'
```

## Next Steps


---

*Source: test_engine_lock.py:23 | Complexity: Advanced | Last updated: 2026-05-05*