# How To: Kill Orphan Permission Error On Probe

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: PermissionError on os.kill(pid, 0) returns refused.

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
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: 'PermissionError on os.kill(pid, 0) returns refused.'

```python
'PermissionError on os.kill(pid, 0) returns refused.'
```

**Verification:**
```python
assert result['killed'] is False
```

### Step 2: Assign real_pid = os.getpid(...)

```python
real_pid = os.getpid()
```

**Verification:**
```python
assert result['method'] == 'refused'
```

### Step 3: Assign real_ppid = os.getppid(...)

```python
real_ppid = os.getppid()
```

**Verification:**
```python
assert 'Permission denied' in result['error']
```

### Step 4: Assign fake_pid = value

```python
fake_pid = real_pid + 10000
```

### Step 5: Call monkeypatch.setattr()

```python
monkeypatch.setattr('os.kill', mock_kill)
```

### Step 6: Call monkeypatch.setattr()

```python
monkeypatch.setattr('os.getpid', lambda: real_pid)
```

### Step 7: Call monkeypatch.setattr()

```python
monkeypatch.setattr('os.getppid', lambda: real_ppid)
```

### Step 8: Assign result = kill_orphan(...)

```python
result = kill_orphan(fake_pid)
```

**Verification:**
```python
assert result['killed'] is False
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
'PermissionError on os.kill(pid, 0) returns refused.'
from superlocalmemory.infra.process_reaper import kill_orphan
real_pid = os.getpid()
real_ppid = os.getppid()
fake_pid = real_pid + 10000

def mock_kill(pid, sig):
    if sig == 0:
        raise PermissionError('Operation not permitted')
    raise AssertionError('Should not reach SIGTERM')
monkeypatch.setattr('os.kill', mock_kill)
monkeypatch.setattr('os.getpid', lambda: real_pid)
monkeypatch.setattr('os.getppid', lambda: real_ppid)
result = kill_orphan(fake_pid)
assert result['killed'] is False
assert result['method'] == 'refused'
assert 'Permission denied' in result['error']
```

## Next Steps


---

*Source: test_process_reaper.py:835 | Complexity: Advanced | Last updated: 2026-05-05*