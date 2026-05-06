# How To: No Recall Reminder Within Interval

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Within 15 minutes, no recall reminder.

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

### Step 1: 'Within 15 minutes, no recall reminder.'

```python
'Within 15 minutes, no recall reminder.'
```

**Verification:**
```python
assert 'context refresh' not in out
```

### Step 2: Assign recall_lock = os.path.join(...)

```python
recall_lock = os.path.join(tempfile.gettempdir(), 'slm-recall-reminder')
```

### Step 3: Assign recent_ts = value

```python
recent_ts = int(time.time()) - 60
```

### Step 4: Assign learn_lock = os.path.join(...)

```python
learn_lock = os.path.join(tempfile.gettempdir(), 'slm-learn-reminder')
```

### Step 5: Assign stdin_data = json.dumps(...)

```python
stdin_data = json.dumps({'tool_input': {}})
```

### Step 6: Assign out = value

```python
out = capsys.readouterr().out
```

**Verification:**
```python
assert 'context refresh' not in out
```

### Step 7: Call f.write()

```python
f.write(str(recent_ts))
```

### Step 8: Call f.write()

```python
f.write(str(recent_ts))
```

### Step 9: Call handle_hook()

```python
handle_hook('checkpoint')
```


## Complete Example

```python
# Setup
# Fixtures: mock_daemon_post, capsys, _clean_rate_locks

# Workflow
'Within 15 minutes, no recall reminder.'
recall_lock = os.path.join(tempfile.gettempdir(), 'slm-recall-reminder')
recent_ts = int(time.time()) - 60
with open(recall_lock, 'w') as f:
    f.write(str(recent_ts))
learn_lock = os.path.join(tempfile.gettempdir(), 'slm-learn-reminder')
with open(learn_lock, 'w') as f:
    f.write(str(recent_ts))
stdin_data = json.dumps({'tool_input': {}})
with patch('sys.stdin', io.StringIO(stdin_data)):
    with patch('sys.stdin.isatty', return_value=False):
        with pytest.raises(SystemExit):
            handle_hook('checkpoint')
out = capsys.readouterr().out
assert 'context refresh' not in out
```

## Next Steps


---

*Source: test_hook_handlers.py:615 | Complexity: Advanced | Last updated: 2026-05-05*