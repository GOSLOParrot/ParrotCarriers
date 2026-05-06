# How To: Store Forwards Http Post

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test store forwards http post

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `types`
- `pytest`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.mcp._pool_adapter`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.core.worker_pool`
- `superlocalmemory.mcp._daemon_proxy`
- `superlocalmemory.core.worker_pool`

**Setup Required:**
```python
# Fixtures: monkeypatch
```

## Step-by-Step Guide

### Step 1: Assign captured = value

```python
captured = {}
```

**Verification:**
```python
assert out['fact_ids'] == ['f1', 'f2']
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(mod.urllib.request, 'urlopen', _fake_urlopen)
```

**Verification:**
```python
assert captured['url'].endswith('/remember')
```

### Step 3: Assign proxy = DaemonPoolProxy(...)

```python
proxy = DaemonPoolProxy(port=9999)
```

**Verification:**
```python
assert body['content'] == 'hello'
```

### Step 4: Assign out = proxy.store(...)

```python
out = proxy.store('hello', metadata={'tags': 'tag1'})
```

**Verification:**
```python
assert body['tags'] == 'tag1'
```

### Step 5: Assign body = json.loads(...)

```python
body = json.loads(captured['body'].decode())
```

**Verification:**
```python
assert body['content'] == 'hello'
```

### Step 6: Assign unknown = value

```python
captured['url'] = req.full_url
```

### Step 7: Assign unknown = value

```python
captured['body'] = req.data
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
captured = {}

def _fake_urlopen(req, timeout=30):
    captured['url'] = req.full_url
    captured['body'] = req.data
    return _FakeResp(json.dumps({'ok': True, 'fact_ids': ['f1', 'f2'], 'count': 2}).encode())
import superlocalmemory.mcp._daemon_proxy as mod
monkeypatch.setattr(mod.urllib.request, 'urlopen', _fake_urlopen)
proxy = DaemonPoolProxy(port=9999)
out = proxy.store('hello', metadata={'tags': 'tag1'})
assert out['fact_ids'] == ['f1', 'f2']
assert captured['url'].endswith('/remember')
body = json.loads(captured['body'].decode())
assert body['content'] == 'hello'
assert body['tags'] == 'tag1'
```

## Next Steps


---

*Source: test_mcp_daemon_proxy.py:76 | Complexity: Intermediate | Last updated: 2026-05-05*