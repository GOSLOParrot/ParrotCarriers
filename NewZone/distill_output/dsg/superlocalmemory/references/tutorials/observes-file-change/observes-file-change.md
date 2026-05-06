# How To: Observes File Change

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: First checkpoint for a file should trigger observe via daemon HTTP.

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

### Step 1: 'First checkpoint for a file should trigger observe via daemon HTTP.'

```python
'First checkpoint for a file should trigger observe via daemon HTTP.'
```

**Verification:**
```python
assert exc_info.value.code == 0
```

### Step 2: Assign mock_daemon_post.return_value = True

```python
mock_daemon_post.return_value = True
```

**Verification:**
```python
assert call_args[0][0] == '/observe'
```

### Step 3: Assign stdin_data = json.dumps(...)

```python
stdin_data = json.dumps({'tool_input': {'file_path': '/project/src/main.py'}})
```

**Verification:**
```python
assert 'main.py' in call_args[0][1]['content']
```

### Step 4: Call mock_daemon_post.assert_called()

```python
mock_daemon_post.assert_called()
```

**Verification:**
```python
assert '[SLM-AUTO]' in out
```

### Step 5: Assign call_args = value

```python
call_args = mock_daemon_post.call_args
```

**Verification:**
```python
assert 'main.py' in out
```

### Step 6: Assign out = value

```python
out = capsys.readouterr().out
```

**Verification:**
```python
assert '[SLM-AUTO]' in out
```

### Step 7: Call handle_hook()

```python
handle_hook('checkpoint')
```


## Complete Example

```python
# Setup
# Fixtures: mock_daemon_post, capsys, _clean_rate_locks

# Workflow
'First checkpoint for a file should trigger observe via daemon HTTP.'
mock_daemon_post.return_value = True
stdin_data = json.dumps({'tool_input': {'file_path': '/project/src/main.py'}})
with patch('sys.stdin', io.StringIO(stdin_data)):
    with patch('sys.stdin.isatty', return_value=False):
        with pytest.raises(SystemExit) as exc_info:
            handle_hook('checkpoint')
assert exc_info.value.code == 0
mock_daemon_post.assert_called()
call_args = mock_daemon_post.call_args
assert call_args[0][0] == '/observe'
assert 'main.py' in call_args[0][1]['content']
out = capsys.readouterr().out
assert '[SLM-AUTO]' in out
assert 'main.py' in out
```

## Next Steps


---

*Source: test_hook_handlers.py:487 | Complexity: Intermediate | Last updated: 2026-05-05*