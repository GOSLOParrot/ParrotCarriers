# How To: Heartbeat Detects Dead Parent

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test heartbeat detects dead parent

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

### Step 1: Assign proc = subprocess.Popen(...)

```python
proc = subprocess.Popen(['true'])
```

**Verification:**
```python
assert callback_called.wait(timeout=5.0), 'Callback was not called within 5 seconds'
```

### Step 2: Call proc.wait()

```python
proc.wait()
```

### Step 3: Assign dead_pid = value

```python
dead_pid = proc.pid
```

### Step 4: Assign callback_called = threading.Event(...)

```python
callback_called = threading.Event()
```

### Step 5: Assign monitor = HeartbeatMonitor(...)

```python
monitor = HeartbeatMonitor(dead_pid, interval_seconds=1, shutdown_callback=on_parent_dead)
```

### Step 6: Call monitor.start()

```python
monitor.start()
```

### Step 7: Call callback_called.set()

```python
callback_called.set()
```

**Verification:**
```python
assert callback_called.wait(timeout=5.0), 'Callback was not called within 5 seconds'
```

### Step 8: Call monitor.stop()

```python
monitor.stop()
```


## Complete Example

```python
# Workflow
from superlocalmemory.infra.heartbeat_monitor import HeartbeatMonitor
proc = subprocess.Popen(['true'])
proc.wait()
dead_pid = proc.pid
callback_called = threading.Event()

def on_parent_dead() -> None:
    callback_called.set()
monitor = HeartbeatMonitor(dead_pid, interval_seconds=1, shutdown_callback=on_parent_dead)
monitor.start()
try:
    assert callback_called.wait(timeout=5.0), 'Callback was not called within 5 seconds'
finally:
    monitor.stop()
```

## Next Steps


---

*Source: test_heartbeat_monitor.py:23 | Complexity: Advanced | Last updated: 2026-05-05*