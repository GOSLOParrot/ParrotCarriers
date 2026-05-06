# How To: Skip Active Process

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Do NOT flag a process whose parent is alive.

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
# Fixtures: default_reaper_config, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Do NOT flag a process whose parent is alive.'

```python
'Do NOT flag a process whose parent is alive.'
```

**Verification:**
```python
assert len(orphans) == 0
```

### Step 2: Assign active_proc = SlmProcessInfo(...)

```python
active_proc = SlmProcessInfo(pid=12345, ppid=os.getppid(), start_time=time.time() - 3600, command='python -m superlocalmemory.mcp.server', is_orphan=False, parent_name='node', age_hours=1.0)
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.infra.process_reaper.find_slm_processes', lambda: [active_proc])
```

### Step 4: Assign orphans = find_orphans(...)

```python
orphans = find_orphans(default_reaper_config)
```

**Verification:**
```python
assert len(orphans) == 0
```


## Complete Example

```python
# Setup
# Fixtures: default_reaper_config, monkeypatch

# Workflow
'Do NOT flag a process whose parent is alive.'
from superlocalmemory.infra.process_reaper import SlmProcessInfo, find_orphans
active_proc = SlmProcessInfo(pid=12345, ppid=os.getppid(), start_time=time.time() - 3600, command='python -m superlocalmemory.mcp.server', is_orphan=False, parent_name='node', age_hours=1.0)
monkeypatch.setattr('superlocalmemory.infra.process_reaper.find_slm_processes', lambda: [active_proc])
orphans = find_orphans(default_reaper_config)
assert len(orphans) == 0
```

## Next Steps


---

*Source: test_process_reaper.py:61 | Complexity: Intermediate | Last updated: 2026-05-05*