# How To: Recall Forwards Http Request

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test recall forwards http request

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
assert out['ok'] is True
```

### Step 2: Call monkeypatch.setattr()

```python
monkeypatch.setattr(mod.urllib.request, 'urlopen', _fake_urlopen)
```

**Verification:**
```python
assert 'q=what+did+we+ship' in captured['url'] or 'q=what%20did%20we%20ship' in captured['url']
```

### Step 3: Assign proxy = DaemonPoolProxy(...)

```python
proxy = DaemonPoolProxy(port=9999)
```

**Verification:**
```python
assert 'limit=3' in captured['url']
```

### Step 4: Assign out = proxy.recall(...)

```python
out = proxy.recall('what did we ship', limit=3, session_id='s-1')
```

**Verification:**
```python
assert 'session_id=s-1' in captured['url']
```

### Step 5: Assign unknown = getattr(...)

```python
captured['url'] = getattr(req, 'full_url', req)
```


## Complete Example

```python
# Setup
# Fixtures: monkeypatch

# Workflow
captured = {}

def _fake_urlopen(req, timeout=30):
    captured['url'] = getattr(req, 'full_url', req)
    return _FakeResp(json.dumps({'ok': True, 'results': [{'fact_id': 'f1', 'content': 'hi', 'score': 0.8}], 'query_type': 'semantic'}).encode())
import superlocalmemory.mcp._daemon_proxy as mod
monkeypatch.setattr(mod.urllib.request, 'urlopen', _fake_urlopen)
proxy = DaemonPoolProxy(port=9999)
out = proxy.recall('what did we ship', limit=3, session_id='s-1')
assert out['ok'] is True
assert 'q=what+did+we+ship' in captured['url'] or 'q=what%20did%20we%20ship' in captured['url']
assert 'limit=3' in captured['url']
assert 'session_id=s-1' in captured['url']
```

## Next Steps


---

*Source: test_mcp_daemon_proxy.py:54 | Complexity: Intermediate | Last updated: 2026-05-05*