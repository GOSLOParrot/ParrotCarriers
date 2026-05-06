# How To: Post Tool Async Sends Install Token

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test post tool async sends install token

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

### Step 1: Assign token = sp.ensure_install_token(...)

```python
token = sp.ensure_install_token()
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
assert json.loads(out) == {'async': True}
```

### Step 3: Assign unknown = _run_hook(...)

```python
rc, out = _run_hook(post_tool_async_hook.main, json.dumps({'session_id': 's', 'tool_name': 'Read', 'tool_input': {'file_path': '/x'}, 'tool_response': 'some content'}), monkeypatch)
```

**Verification:**
```python
assert captured['token'] == token
```

### Step 4: Assign body = json.loads(...)

```python
body = json.loads(captured['body'].decode('utf-8'))
```

**Verification:**
```python
assert isinstance(captured['body'], bytes)
```

### Step 5: Assign unknown = value

```python
captured['url'] = req.full_url
```

**Verification:**
```python
assert body['session_id'] == 's'
```

### Step 6: Assign unknown = value

```python
captured['token'] = req.headers.get('X-slm-hook-token') or req.headers.get('X-Slm-Hook-Token')
```

**Verification:**
```python
assert body['tool_name'] == 'Read'
```

### Step 7: Assign unknown = value

```python
captured['body'] = req.data
```


## Complete Example

```python
# Setup
# Fixtures: home, monkeypatch

# Workflow
token = sp.ensure_install_token()
captured: dict = {}

def fake_urlopen(req, timeout=0.5):
    captured['url'] = req.full_url
    captured['token'] = req.headers.get('X-slm-hook-token') or req.headers.get('X-Slm-Hook-Token')
    captured['body'] = req.data

    class _R:

        def read(self) -> bytes:
            return b'{}'

        def close(self) -> None:
            return None
    return _R()
import urllib.request as _ur
monkeypatch.setattr(_ur, 'urlopen', fake_urlopen)
rc, out = _run_hook(post_tool_async_hook.main, json.dumps({'session_id': 's', 'tool_name': 'Read', 'tool_input': {'file_path': '/x'}, 'tool_response': 'some content'}), monkeypatch)
assert rc == 0
assert json.loads(out) == {'async': True}
assert captured['token'] == token
assert isinstance(captured['body'], bytes)
body = json.loads(captured['body'].decode('utf-8'))
assert body['session_id'] == 's'
assert body['tool_name'] == 'Read'
```

## Next Steps


---

*Source: test_hook_handlers.py:259 | Complexity: Advanced | Last updated: 2026-05-05*