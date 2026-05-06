# How To: Learn Reminder After 30 Min

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: After 30 minutes, should print learn reminder.

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

### Step 1: 'After 30 minutes, should print learn reminder.'

```python
'After 30 minutes, should print learn reminder.'
```

**Verification:**
```python
assert 'learned_patterns' in out or 'learn' in out.lower()
```

### Step 2: Assign learn_lock = os.path.join(...)

```python
learn_lock = os.path.join(tempfile.gettempdir(), 'slm-learn-reminder')
```

### Step 3: Assign old_ts = value

```python
old_ts = int(time.time()) - (_LEARN_INTERVAL + 60)
```

### Step 4: Assign stdin_data = json.dumps(...)

```python
stdin_data = json.dumps({'tool_input': {}})
```

### Step 5: Assign out = value

```python
out = capsys.readouterr().out
```

**Verification:**
```python
assert 'learned_patterns' in out or 'learn' in out.lower()
```

### Step 6: Call f.write()

```python
f.write(str(old_ts))
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
'After 30 minutes, should print learn reminder.'
learn_lock = os.path.join(tempfile.gettempdir(), 'slm-learn-reminder')
old_ts = int(time.time()) - (_LEARN_INTERVAL + 60)
with open(learn_lock, 'w') as f:
    f.write(str(old_ts))
stdin_data = json.dumps({'tool_input': {}})
with patch('sys.stdin', io.StringIO(stdin_data)):
    with patch('sys.stdin.isatty', return_value=False):
        with pytest.raises(SystemExit):
            handle_hook('checkpoint')
out = capsys.readouterr().out
assert 'learned_patterns' in out or 'learn' in out.lower()
```

## Next Steps


---

*Source: test_hook_handlers.py:598 | Complexity: Intermediate | Last updated: 2026-05-05*