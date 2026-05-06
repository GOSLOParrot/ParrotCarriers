# How To: Different Files Have Independent Cooldowns

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Two different files should have independent rate limits.

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

### Step 1: 'Two different files should have independent rate limits.'

```python
'Two different files should have independent rate limits.'
```

**Verification:**
```python
assert 'b.py' in out
```

### Step 2: Assign now = int(...)

```python
now = int(time.time())
```

### Step 3: Assign file_a = '/project/src/a.py'

```python
file_a = '/project/src/a.py'
```

### Step 4: Assign hash_a = _safe_hash(...)

```python
hash_a = _safe_hash(file_a)
```

### Step 5: Assign lock_a = os.path.join(...)

```python
lock_a = os.path.join(tempfile.gettempdir(), f'slm-obs-{hash_a}')
```

### Step 6: Assign file_b = '/project/src/b.py'

```python
file_b = '/project/src/b.py'
```

### Step 7: Assign stdin_data = json.dumps(...)

```python
stdin_data = json.dumps({'tool_input': {'file_path': file_b}})
```

### Step 8: Call mock_daemon_post.assert_called()

```python
mock_daemon_post.assert_called()
```

### Step 9: Assign out = value

```python
out = capsys.readouterr().out
```

**Verification:**
```python
assert 'b.py' in out
```

### Step 10: Call f.write()

```python
f.write(str(now))
```

### Step 11: Assign lock = os.path.join(...)

```python
lock = os.path.join(tempfile.gettempdir(), name)
```

### Step 12: Call f.write()

```python
f.write(str(now))
```

### Step 13: Call handle_hook()

```python
handle_hook('checkpoint')
```


## Complete Example

```python
# Setup
# Fixtures: mock_daemon_post, capsys, _clean_rate_locks

# Workflow
'Two different files should have independent rate limits.'
now = int(time.time())
file_a = '/project/src/a.py'
hash_a = _safe_hash(file_a)
lock_a = os.path.join(tempfile.gettempdir(), f'slm-obs-{hash_a}')
with open(lock_a, 'w') as f:
    f.write(str(now))
for name in ('slm-recall-reminder', 'slm-learn-reminder'):
    lock = os.path.join(tempfile.gettempdir(), name)
    with open(lock, 'w') as f:
        f.write(str(now))
file_b = '/project/src/b.py'
stdin_data = json.dumps({'tool_input': {'file_path': file_b}})
with patch('sys.stdin', io.StringIO(stdin_data)):
    with patch('sys.stdin.isatty', return_value=False):
        with pytest.raises(SystemExit):
            handle_hook('checkpoint')
mock_daemon_post.assert_called()
out = capsys.readouterr().out
assert 'b.py' in out
```

## Next Steps


---

*Source: test_hook_handlers.py:674 | Complexity: Advanced | Last updated: 2026-05-05*