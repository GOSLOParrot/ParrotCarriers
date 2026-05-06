# How To: Cleanup Dead Pids

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test cleanup dead pids

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

### Step 1: Assign mgr = PidManager(...)

```python
mgr = PidManager(tmp_pid_file)
```

**Verification:**
```python
assert removed == 2
```

### Step 2: Assign my_pid = os.getpid(...)

```python
my_pid = os.getpid()
```

**Verification:**
```python
assert my_pid in pids
```

### Step 3: Call mgr.register()

```python
mgr.register(my_pid, os.getppid())
```

**Verification:**
```python
assert 99998 not in pids
```

### Step 4: Call mgr.register()

```python
mgr.register(99998, 88888)
```

**Verification:**
```python
assert 99999 not in pids
```

### Step 5: Call mgr.register()

```python
mgr.register(99999, 88889)
```

### Step 6: Assign removed = mgr.cleanup_dead(...)

```python
removed = mgr.cleanup_dead()
```

**Verification:**
```python
assert removed == 2
```

### Step 7: Assign records = mgr.read_all(...)

```python
records = mgr.read_all()
```

### Step 8: Assign pids = value

```python
pids = [r.pid for r in records]
```

**Verification:**
```python
assert my_pid in pids
```


## Complete Example

```python
# Setup
# Fixtures: tmp_pid_file

# Workflow
from superlocalmemory.infra.pid_manager import PidManager
mgr = PidManager(tmp_pid_file)
my_pid = os.getpid()
mgr.register(my_pid, os.getppid())
mgr.register(99998, 88888)
mgr.register(99999, 88889)
removed = mgr.cleanup_dead()
assert removed == 2
records = mgr.read_all()
pids = [r.pid for r in records]
assert my_pid in pids
assert 99998 not in pids
assert 99999 not in pids
```

## Next Steps


---

*Source: test_pid_manager.py:118 | Complexity: Advanced | Last updated: 2026-05-05*