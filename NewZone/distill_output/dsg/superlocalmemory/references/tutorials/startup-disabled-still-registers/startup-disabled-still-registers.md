# How To: Startup Disabled Still Registers

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: When reaper is disabled, still register current PID.

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
# Fixtures: tmp_pid_file
```

## Step-by-Step Guide

### Step 1: 'When reaper is disabled, still register current PID.'

```python
'When reaper is disabled, still register current PID.'
```

**Verification:**
```python
assert os.getpid() in pids
```

### Step 2: Assign config = ReaperConfig(...)

```python
config = ReaperConfig(enabled=False)
```

**Verification:**
```python
assert result['registered_pid'] == os.getpid()
```

### Step 3: Assign mgr = PidManager(...)

```python
mgr = PidManager(tmp_pid_file)
```

### Step 4: Assign result = reap_stale_on_startup(...)

```python
result = reap_stale_on_startup(config, mgr)
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
assert os.getpid() in pids
```


## Complete Example

```python
# Setup
# Fixtures: tmp_pid_file

# Workflow
'When reaper is disabled, still register current PID.'
from superlocalmemory.infra.pid_manager import PidManager
from superlocalmemory.infra.process_reaper import ReaperConfig, reap_stale_on_startup
config = ReaperConfig(enabled=False)
mgr = PidManager(tmp_pid_file)
result = reap_stale_on_startup(config, mgr)
records = mgr.read_all()
pids = [r.pid for r in records]
assert os.getpid() in pids
assert result['registered_pid'] == os.getpid()
```

## Next Steps


---

*Source: test_process_reaper.py:289 | Complexity: Intermediate | Last updated: 2026-05-05*