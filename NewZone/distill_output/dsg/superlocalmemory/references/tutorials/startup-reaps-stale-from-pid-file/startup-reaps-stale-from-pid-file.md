# How To: Startup Reaps Stale From Pid File

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test startup reaps stale from pid file

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `os`
- `signal`
- `subprocess`
- `sys`
- `time`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `json`
- `datetime`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `json`
- `datetime`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `json`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.pid_manager`
- `superlocalmemory.infra.process_reaper`
- `superlocalmemory.infra.process_reaper`

**Setup Required:**
```python
# Fixtures: tmp_pid_file, default_reaper_config
```

## Step-by-Step Guide

### Step 1: Assign mgr = PidManager(...)

```python
mgr = PidManager(tmp_pid_file)
```

**Verification:**
```python
assert 99999 not in pids
```

### Step 2: Call mgr.register()

```python
mgr.register(99999, 88888)
```

**Verification:**
```python
assert os.getpid() in pids
```

### Step 3: Assign result = reap_stale_on_startup(...)

```python
result = reap_stale_on_startup(default_reaper_config, mgr)
```

**Verification:**
```python
assert result['registered_pid'] == os.getpid()
```

### Step 4: Assign records = mgr.read_all(...)

```python
records = mgr.read_all()
```

### Step 5: Assign pids = value

```python
pids = [r.pid for r in records]
```

**Verification:**
```python
assert 99999 not in pids
```


## Complete Example

```python
# Setup
# Fixtures: tmp_pid_file, default_reaper_config

# Workflow
from superlocalmemory.infra.pid_manager import PidManager
from superlocalmemory.infra.process_reaper import reap_stale_on_startup
mgr = PidManager(tmp_pid_file)
mgr.register(99999, 88888)
result = reap_stale_on_startup(default_reaper_config, mgr)
records = mgr.read_all()
pids = [r.pid for r in records]
assert 99999 not in pids
assert os.getpid() in pids
assert result['registered_pid'] == os.getpid()
```

## Next Steps


---

*Source: test_process_reaper.py:271 | Complexity: Intermediate | Last updated: 2026-05-05*