# How To: Callback Exception Handled

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Heartbeat handles callback exceptions gracefully.

## Prerequisites

**Required Modules:**
- `__future__`
- `subprocess`
- `threading`
- `os`
- `pytest`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `superlocalmemory.infra.heartbeat_monitor`
- `unittest.mock`
- `superlocalmemory.infra.heartbeat_monitor`
- `unittest.mock`


## Step-by-Step Guide

### Step 1: 'Heartbeat handles callback exceptions gracefully.'

```python
'Heartbeat handles callback exceptions gracefully.'
```

**Verification:**
```python
assert callback_ran.wait(timeout=5.0), 'Callback should have run'
```

### Step 2: Assign proc = subprocess.Popen(...)

```python
proc = subprocess.Popen(['true'])
```

### Step 3: Call proc.wait()

```python
proc.wait()
```

### Step 4: Assign dead_pid = value

```python
dead_pid = proc.pid
```

### Step 5: Assign callback_ran = threading.Event(...)

```python
callback_ran = threading.Event()
```

### Step 6: Assign monitor = HeartbeatMonitor(...)

```python
monitor = HeartbeatMonitor(dead_pid, interval_seconds=1, shutdown_callback=bad_callback)
```

### Step 7: Call monitor.start()

```python
monitor.start()
```

### Step 8: Call callback_ran.set()

```python
callback_ran.set()
```

**Verification:**
```python
assert callback_ran.wait(timeout=5.0), 'Callback should have run'
```

### Step 9: Call monitor.stop()

```python
monitor.stop()
```


## Complete Example

```python
# Workflow
'Heartbeat handles callback exceptions gracefully.'
from superlocalmemory.infra.heartbeat_monitor import HeartbeatMonitor
proc = subprocess.Popen(['true'])
proc.wait()
dead_pid = proc.pid
callback_ran = threading.Event()

def bad_callback() -> None:
    callback_ran.set()
    raise RuntimeError('Simulated callback failure')
monitor = HeartbeatMonitor(dead_pid, interval_seconds=1, shutdown_callback=bad_callback)
monitor.start()
try:
    assert callback_ran.wait(timeout=5.0), 'Callback should have run'
finally:
    monitor.stop()
```

## Next Steps


---

*Source: test_heartbeat_monitor.py:109 | Complexity: Advanced | Last updated: 2026-05-05*