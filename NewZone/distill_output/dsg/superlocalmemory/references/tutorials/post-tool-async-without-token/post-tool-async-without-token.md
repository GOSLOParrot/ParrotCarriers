# How To: Post Tool Async Without Token

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test post tool async without token

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `io`
- `json`
- `sys`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.core`
- `superlocalmemory.hooks`
- `superlocalmemory.core.topic_signature`
- `urllib.request`
- `superlocalmemory.hooks`
- `superlocalmemory.hooks`
- `superlocalmemory.core.topic_signature`
- `urllib.request`
- `urllib.request`
- `urllib.request`

**Setup Required:**
```python
# Fixtures: home, monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign token_path = value

```python
token_path = home / '.install_token'
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Assign called = value

```python
called = {'count': 0}
```

**Verification:**
```python
assert json.loads(out) == {'async': True}
```

### Step 3: Call monkeypatch.setattr()

```python
monkeypatch.setattr(_ur, 'urlopen', fake_urlopen)
```

**Verification:**
```python
assert called['count'] == 0
```

### Step 4: Assign unknown = _run_hook(...)

```python
rc, out = _run_hook(post_tool_async_hook.main, json.dumps({'session_id': 's', 'tool_name': 'Read'}), monkeypatch)
```

**Verification:**
```python
assert rc == 0
```

### Step 5: Call token_path.unlink()

```python
token_path.unlink()
```


## Complete Example

```python
# Setup
# Fixtures: home, monkeypatch

# Workflow
token_path = home / '.install_token'
if token_path.exists():
    token_path.unlink()
called = {'count': 0}

def fake_urlopen(*args, **kwargs):
    called['count'] += 1
    raise AssertionError('urlopen should not be called without token')
import urllib.request as _ur
monkeypatch.setattr(_ur, 'urlopen', fake_urlopen)
rc, out = _run_hook(post_tool_async_hook.main, json.dumps({'session_id': 's', 'tool_name': 'Read'}), monkeypatch)
assert rc == 0
assert json.loads(out) == {'async': True}
assert called['count'] == 0
```

## Next Steps


---

*Source: test_hook_handlers.py:415 | Complexity: Advanced | Last updated: 2026-05-05*