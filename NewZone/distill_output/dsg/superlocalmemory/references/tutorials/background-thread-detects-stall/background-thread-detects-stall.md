# How To: Background Thread Detects Stall

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test background thread detects stall

## Prerequisites

**Required Modules:**
- `__future__`
- `threading`
- `time`
- `superlocalmemory.core`


## Step-by-Step Guide

### Step 1: Assign lw = _imports(...)

```python
lw = _imports()
```

**Verification:**
```python
assert len(events) >= 1
```

### Step 2: Assign events = value

```python
events = []
```

### Step 3: Assign w = lw.LoopWatchdog(...)

```python
w = lw.LoopWatchdog(stale_threshold_s=0.05, on_stale=lambda age: events.append(age))
```

### Step 4: Call w.tick()

```python
w.tick()
```

### Step 5: Assign stop = threading.Event(...)

```python
stop = threading.Event()
```

### Step 6: Assign thread = threading.Thread(...)

```python
thread = threading.Thread(target=w.run_forever, args=(stop, 0.02), daemon=True)
```

### Step 7: Call thread.start()

```python
thread.start()
```

### Step 8: Call time.sleep()

```python
time.sleep(0.15)
```

### Step 9: Call stop.set()

```python
stop.set()
```

### Step 10: Call thread.join()

```python
thread.join(timeout=1.0)
```

**Verification:**
```python
assert len(events) >= 1
```


## Complete Example

```python
# Workflow
lw = _imports()
events = []
w = lw.LoopWatchdog(stale_threshold_s=0.05, on_stale=lambda age: events.append(age))
w.tick()
stop = threading.Event()
thread = threading.Thread(target=w.run_forever, args=(stop, 0.02), daemon=True)
thread.start()
time.sleep(0.15)
stop.set()
thread.join(timeout=1.0)
assert len(events) >= 1
```

## Next Steps


---

*Source: test_loop_watchdog.py:53 | Complexity: Advanced | Last updated: 2026-05-05*