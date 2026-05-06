# How To: Check Parent Ps Subprocess Error

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When ps -p fails with SubprocessError, parent_name stays empty.

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

### Step 1: 'When ps -p fails with SubprocessError, parent_name stays empty.'

```python
'When ps -p fails with SubprocessError, parent_name stays empty.'
```

**Verification:**
```python
assert is_orphan is False
```

### Step 2: Assign original_kill = value

```python
original_kill = os.kill
```

**Verification:**
```python
assert name == ''
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr('os.kill', mock_kill)
```

### Step 4: Call monkeypatch.setattr()

```python
monkeypatch.setattr('subprocess.run', MagicMock(side_effect=subprocess.SubprocessError('mocked ps fail')))
```

### Step 5: Assign unknown = _check_parent(...)

```python
is_orphan, name = _check_parent(54321)
```

**Verification:**
```python
assert is_orphan is False
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
'When ps -p fails with SubprocessError, parent_name stays empty.'
from superlocalmemory.infra.process_reaper import _check_parent
original_kill = os.kill

def mock_kill(pid, sig):
    if pid == 54321 and sig == 0:
        return None
    return original_kill(pid, sig)
monkeypatch.setattr('os.kill', mock_kill)
monkeypatch.setattr('subprocess.run', MagicMock(side_effect=subprocess.SubprocessError('mocked ps fail')))
is_orphan, name = _check_parent(54321)
assert is_orphan is False
assert name == ''
```

## Next Steps


---

*Source: test_process_reaper.py:682 | Complexity: Intermediate | Last updated: 2026-05-05*