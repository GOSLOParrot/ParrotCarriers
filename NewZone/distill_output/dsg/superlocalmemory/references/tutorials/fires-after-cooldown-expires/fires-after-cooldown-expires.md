# How To: Fires After Cooldown Expires

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: After 5 minutes, same file should trigger observe again.

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
# Fixtures: mock_daemon_post, capsys, _clean_rate_locks
```

## Step-by-Step Guide

### Step 1: 'After 5 minutes, same file should trigger observe again.'

```python
'After 5 minutes, same file should trigger observe again.'
```

**Verification:**
```python
assert exc_info.value.code == 0
```

### Step 2: Assign file_path = '/project/src/expired_test.py'

```python
file_path = '/project/src/expired_test.py'
```

**Verification:**
```python
assert '[SLM-AUTO]' in out
```

### Step 3: Assign file_hash = _safe_hash(...)

```python
file_hash = _safe_hash(file_path)
```

### Step 4: Assign lock_file = os.path.join(...)

```python
lock_file = os.path.join(tempfile.gettempdir(), f'slm-obs-{file_hash}')
```

### Step 5: Assign old_ts = value

```python
old_ts = int(time.time()) - (_OBSERVE_COOLDOWN + 60)
```

### Step 6: Assign stdin_data = json.dumps(...)

```python
stdin_data = json.dumps({'tool_input': {'file_path': file_path}})
```

**Verification:**
```python
assert exc_info.value.code == 0
```

### Step 7: Call mock_daemon_post.assert_called()

```python
mock_daemon_post.assert_called()
```

### Step 8: Assign out = value

```python
out = capsys.readouterr().out
```

**Verification:**
```python
assert '[SLM-AUTO]' in out
```

### Step 9: Call f.write()

```python
f.write(str(old_ts))
```

### Step 10: Call handle_hook()

```python
handle_hook('checkpoint')
```


## Complete Example

```python
# Setup
# Fixtures: mock_daemon_post, capsys, _clean_rate_locks

# Workflow
'After 5 minutes, same file should trigger observe again.'
file_path = '/project/src/expired_test.py'
file_hash = _safe_hash(file_path)
lock_file = os.path.join(tempfile.gettempdir(), f'slm-obs-{file_hash}')
old_ts = int(time.time()) - (_OBSERVE_COOLDOWN + 60)
with open(lock_file, 'w') as f:
    f.write(str(old_ts))
stdin_data = json.dumps({'tool_input': {'file_path': file_path}})
with patch('sys.stdin', io.StringIO(stdin_data)):
    with patch('sys.stdin.isatty', return_value=False):
        with pytest.raises(SystemExit) as exc_info:
            handle_hook('checkpoint')
assert exc_info.value.code == 0
mock_daemon_post.assert_called()
out = capsys.readouterr().out
assert '[SLM-AUTO]' in out
```

## Next Steps


---

*Source: test_hook_handlers.py:536 | Complexity: Advanced | Last updated: 2026-05-05*