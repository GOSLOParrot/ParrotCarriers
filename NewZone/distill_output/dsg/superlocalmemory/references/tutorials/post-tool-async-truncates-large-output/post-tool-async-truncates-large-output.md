# How To: Post Tool Async Truncates Large Output

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test post tool async truncates large output

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

### Step 1: Call sp.ensure_install_token()

```python
sp.ensure_install_token()
```

**Verification:**
```python
assert rc == 0
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(_ur, 'urlopen', fake_urlopen)
```

**Verification:**
```python
assert len(body['output_summary']) <= 4000
```

### Step 3: Assign big = value

```python
big = 'y' * 20000
```

**Verification:**
```python
assert len(body['input_summary']) <= 2000
```

### Step 4: Assign unknown = _run_hook(...)

```python
rc, out = _run_hook(post_tool_async_hook.main, json.dumps({'session_id': 's', 'tool_name': 'X', 'tool_input': {'arg': 'a' * 5000}, 'tool_response': big}), monkeypatch)
```

**Verification:**
```python
assert rc == 0
```

### Step 5: Assign body = json.loads(...)

```python
body = json.loads(captured['body'])
```

**Verification:**
```python
assert len(body['output_summary']) <= 4000
```

### Step 6: Assign unknown = value

```python
captured['body'] = req.data
```


## Complete Example

```python
# Setup
# Fixtures: home, monkeypatch

# Workflow
sp.ensure_install_token()
captured: dict = {}

def fake_urlopen(req, timeout=0.5):
    captured['body'] = req.data

    class _R:

        def read(self) -> bytes:
            return b'{}'

        def close(self) -> None:
            return None
    return _R()
import urllib.request as _ur
monkeypatch.setattr(_ur, 'urlopen', fake_urlopen)
big = 'y' * 20000
rc, out = _run_hook(post_tool_async_hook.main, json.dumps({'session_id': 's', 'tool_name': 'X', 'tool_input': {'arg': 'a' * 5000}, 'tool_response': big}), monkeypatch)
assert rc == 0
body = json.loads(captured['body'])
assert len(body['output_summary']) <= 4000
assert len(body['input_summary']) <= 2000
```

## Next Steps


---

*Source: test_hook_handlers.py:472 | Complexity: Advanced | Last updated: 2026-05-05*