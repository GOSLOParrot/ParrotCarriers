# How To: Detect Orphan Process

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Detect a process whose parent PID is dead.

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

### Step 1: 'Detect a process whose parent PID is dead.'

```python
'Detect a process whose parent PID is dead.'
```

**Verification:**
```python
assert len(orphans) == 1
```

### Step 2: Assign config = ReaperConfig(...)

```python
config = ReaperConfig(orphan_age_threshold_hours=0.0)
```

**Verification:**
```python
assert orphans[0].pid == 12345
```

### Step 3: Assign fake_orphan = SlmProcessInfo(...)

```python
fake_orphan = SlmProcessInfo(pid=12345, ppid=99999, start_time=time.time() - 7200, command='python -m superlocalmemory.mcp.server', is_orphan=True, parent_name='', age_hours=2.0)
```

**Verification:**
```python
assert orphans[0].is_orphan is True
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.infra.process_reaper.find_slm_processes', lambda: [fake_orphan])
```

### Step 5: Assign orphans = find_orphans(...)

```python
orphans = find_orphans(config)
```

**Verification:**
```python
assert len(orphans) == 1
```


## Complete Example

```python
# Setup
# Fixtures: default_reaper_config, monkeypatch

# Workflow
'Detect a process whose parent PID is dead.'
from superlocalmemory.infra.process_reaper import ReaperConfig, SlmProcessInfo, find_orphans, find_slm_processes
config = ReaperConfig(orphan_age_threshold_hours=0.0)
fake_orphan = SlmProcessInfo(pid=12345, ppid=99999, start_time=time.time() - 7200, command='python -m superlocalmemory.mcp.server', is_orphan=True, parent_name='', age_hours=2.0)
monkeypatch.setattr('superlocalmemory.infra.process_reaper.find_slm_processes', lambda: [fake_orphan])
orphans = find_orphans(config)
assert len(orphans) == 1
assert orphans[0].pid == 12345
assert orphans[0].is_orphan is True
```

## Next Steps


---

*Source: test_process_reaper.py:30 | Complexity: Intermediate | Last updated: 2026-05-05*