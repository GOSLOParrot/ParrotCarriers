# How To: Cleanup Dead Permission Error Keeps Record

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: PermissionError on kill check keeps the record alive.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.pid_manager`

**Setup Required:**
```python
# Fixtures: tmp_pid_file
```

## Step-by-Step Guide

### Step 1: 'PermissionError on kill check keeps the record alive.'

```python
'PermissionError on kill check keeps the record alive.'
```

**Verification:**
```python
assert removed == 0
```

### Step 2: Assign mgr = PidManager(...)

```python
mgr = PidManager(tmp_pid_file)
```

**Verification:**
```python
assert 55555 in pids
```

### Step 3: Call mgr.register()

```python
mgr.register(55555, 11111)
```

### Step 4: Assign original_kill = value

```python
original_kill = os.kill
```

**Verification:**
```python
assert removed == 0
```

### Step 5: Assign records = mgr.read_all(...)

```python
records = mgr.read_all()
```

### Step 6: Assign pids = value

```python
pids = [r.pid for r in records]
```

**Verification:**
```python
assert 55555 in pids
```

### Step 7: Assign removed = mgr.cleanup_dead(...)

```python
removed = mgr.cleanup_dead()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_pid_file

# Workflow
'PermissionError on kill check keeps the record alive.'
from superlocalmemory.infra.pid_manager import PidManager
mgr = PidManager(tmp_pid_file)
mgr.register(55555, 11111)
original_kill = os.kill

def mock_kill(pid, sig):
    if pid == 55555 and sig == 0:
        raise PermissionError('Operation not permitted')
    return original_kill(pid, sig)
with patch('os.kill', side_effect=mock_kill):
    removed = mgr.cleanup_dead()
assert removed == 0
records = mgr.read_all()
pids = [r.pid for r in records]
assert 55555 in pids
```

## Next Steps


---

*Source: test_pid_manager.py:266 | Complexity: Intermediate | Last updated: 2026-05-05*