# How To: No False Kills Safety

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Active processes with living parents are NEVER killed.

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

### Step 1: 'Active processes with living parents are NEVER killed.'

```python
'Active processes with living parents are NEVER killed.'
```

**Verification:**
```python
assert 11111 in killed_pids
```

### Step 2: Assign config = ReaperConfig(...)

```python
config = ReaperConfig(orphan_age_threshold_hours=0.0)
```

**Verification:**
```python
assert 22222 not in killed_pids
```

### Step 3: Assign orphan = SlmProcessInfo(...)

```python
orphan = SlmProcessInfo(pid=11111, ppid=99999, start_time=time.time() - 7200, command='python -m superlocalmemory.mcp.server', is_orphan=True, parent_name='', age_hours=2.0)
```

**Verification:**
```python
assert result['skipped'] >= 1
```

### Step 4: Assign active = SlmProcessInfo(...)

```python
active = SlmProcessInfo(pid=22222, ppid=os.getppid(), start_time=time.time() - 3600, command='python -m superlocalmemory.mcp.server', is_orphan=False, parent_name='node', age_hours=1.0)
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.infra.process_reaper.find_slm_processes', lambda: [orphan, active])
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr('superlocalmemory.infra.process_reaper.kill_orphan', mock_kill)
```

### Step 7: Assign result = cleanup_all_orphans(...)

```python
result = cleanup_all_orphans(config)
```

**Verification:**
```python
assert 11111 in killed_pids
```

### Step 8: Call killed_pids.append()

```python
killed_pids.append(pid)
```


## Complete Example

```python
# Setup
# Fixtures: default_reaper_config, monkeypatch

# Workflow
'Active processes with living parents are NEVER killed.'
from superlocalmemory.infra.process_reaper import ReaperConfig, SlmProcessInfo, cleanup_all_orphans
config = ReaperConfig(orphan_age_threshold_hours=0.0)
orphan = SlmProcessInfo(pid=11111, ppid=99999, start_time=time.time() - 7200, command='python -m superlocalmemory.mcp.server', is_orphan=True, parent_name='', age_hours=2.0)
active = SlmProcessInfo(pid=22222, ppid=os.getppid(), start_time=time.time() - 3600, command='python -m superlocalmemory.mcp.server', is_orphan=False, parent_name='node', age_hours=1.0)
monkeypatch.setattr('superlocalmemory.infra.process_reaper.find_slm_processes', lambda: [orphan, active])
killed_pids: list[int] = []

def mock_kill(pid: int, **kwargs) -> dict:
    killed_pids.append(pid)
    return {'pid': pid, 'killed': True, 'method': 'sigterm', 'error': None}
monkeypatch.setattr('superlocalmemory.infra.process_reaper.kill_orphan', mock_kill)
result = cleanup_all_orphans(config)
assert 11111 in killed_pids
assert 22222 not in killed_pids
assert result['skipped'] >= 1
```

## Next Steps


---

*Source: test_process_reaper.py:345 | Complexity: Advanced | Last updated: 2026-05-05*