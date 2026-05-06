# How To: Kill Orphan Process Dies During Sigterm

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Process dies between probe and SIGTERM (ProcessLookupError).

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

### Step 1: 'Process dies between probe and SIGTERM (ProcessLookupError).'

```python
'Process dies between probe and SIGTERM (ProcessLookupError).'
```

**Verification:**
```python
assert result['killed'] is False
```

### Step 2: Assign call_count = 0

```python
call_count = 0
```

**Verification:**
```python
assert result['method'] == 'already_dead'
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('os.kill', mock_kill)
```

**Verification:**
```python
assert result['error'] is None
```

### Step 4: Assign fake_pid = value

```python
fake_pid = os.getpid() + 10000
```

### Step 5: Assign result = kill_orphan(...)

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
'Process dies between probe and SIGTERM (ProcessLookupError).'
from superlocalmemory.infra.process_reaper import kill_orphan
call_count = 0

def mock_kill(pid, sig):
    nonlocal call_count
    call_count += 1
    if sig == 0:
        return None
    if sig == signal.SIGTERM:
        raise ProcessLookupError('No such process')
    raise AssertionError('Unexpected signal')
monkeypatch.setattr('os.kill', mock_kill)
fake_pid = os.getpid() + 10000
result = kill_orphan(fake_pid)
assert result['killed'] is False
assert result['method'] == 'already_dead'
assert result['error'] is None
```

## Next Steps


---

*Source: test_process_reaper.py:865 | Complexity: Intermediate | Last updated: 2026-05-05*