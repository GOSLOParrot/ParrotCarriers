# How To: Includes Modified Files From Activity Log

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test includes modified files from activity log

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `io`
- `json`
- `os`
- `sys`
- `tempfile`
- `time`
- `unittest.mock`
- `pytest`
- `superlocalmemory.hooks.hook_handlers`

**Setup Required:**
```python
# Fixtures: mock_run, mock_daemon, mock_consolidate, monkeypatch
```

## Step-by-Step Guide

### Step 1: Call monkeypatch.setenv()

```python
monkeypatch.setenv('CLAUDE_PROJECT_DIR', '/proj')
```

**Verification:**
```python
assert 'config.py' in summary
```

### Step 2: Assign mock_daemon.return_value = True

```python
mock_daemon.return_value = True
```

**Verification:**
```python
assert 'engine.py' in summary
```

### Step 3: Assign now = int(...)

```python
now = int(time.time())
```

### Step 4: Assign mock_run.return_value = MagicMock(...)

```python
mock_run.return_value = MagicMock(stdout='', returncode=0)
```

### Step 5: Assign observe_call = value

```python
observe_call = mock_daemon.call_args_list[0]
```

### Step 6: Assign summary = value

```python
summary = observe_call[0][1]['content']
```

**Verification:**
```python
assert 'config.py' in summary
```

### Step 7: Call f.write()

```python
f.write(f'{now}|engine.py\n{now}|config.py\n{now}|engine.py\n')
```

### Step 8: Call handle_hook()

```python
handle_hook('stop')
```


## Complete Example

```python
# Setup
# Fixtures: mock_run, mock_daemon, mock_consolidate, monkeypatch

# Workflow
monkeypatch.setenv('CLAUDE_PROJECT_DIR', '/proj')
mock_daemon.return_value = True
now = int(time.time())
with open(_ACTIVITY_LOG, 'w') as f:
    f.write(f'{now}|engine.py\n{now}|config.py\n{now}|engine.py\n')
mock_run.return_value = MagicMock(stdout='', returncode=0)
with pytest.raises(SystemExit):
    handle_hook('stop')
observe_call = mock_daemon.call_args_list[0]
summary = observe_call[0][1]['content']
assert 'config.py' in summary
assert 'engine.py' in summary
```

## Next Steps


---

*Source: test_hook_handlers.py:785 | Complexity: Advanced | Last updated: 2026-05-05*