# How To: Middleware Strips Existing Owned Headers

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: If a downstream app already set CSP, middleware must replace it.

## Prerequisites

**Required Modules:**
- `__future__`
- `re`
- `tempfile`
- `pathlib`
- `typing`
- `pytest`
- `fastapi`
- `fastapi.responses`
- `fastapi.testclient`
- `superlocalmemory.core`
- `superlocalmemory.server.middleware.security_headers`
- `superlocalmemory.server.routes`
- `asyncio`
- `asyncio`
- `superlocalmemory.learning.database`


## Step-by-Step Guide

### Step 1: 'If a downstream app already set CSP, middleware must replace it.'

```python
'If a downstream app already set CSP, middleware must replace it.'
```

**Verification:**
```python
assert len(csp_values) == 1, 'must have exactly one CSP header'
```

### Step 2: Assign mw = SecurityHeadersMiddleware(...)

```python
mw = SecurityHeadersMiddleware(inner_app)
```

**Verification:**
```python
assert csp_values[0] != b'default-src *'
```

### Step 3: Call asyncio.run()

```python
asyncio.run(mw({'type': 'http', 'path': '/api/v3/brain', 'raw_path': b'/api/v3/brain'}, receive, send))
```

**Verification:**
```python
assert b"default-src 'self'" in csp_values[0]
```

### Step 4: Assign start = value

```python
start = sent[0]
```

**Verification:**
```python
assert ct_values == [b'text/plain']
```

### Step 5: Assign csp_values = value

```python
csp_values = [v for n, v in start['headers'] if n == b'content-security-policy']
```

**Verification:**
```python
assert len(csp_values) == 1, 'must have exactly one CSP header'
```

### Step 6: Assign ct_values = value

```python
ct_values = [v for n, v in start['headers'] if n == b'content-type']
```

**Verification:**
```python
assert ct_values == [b'text/plain']
```

### Step 7: await send({'type': 'http.response.start', 'status': 200, 'headers': [(b'content-security-policy', b'default-src *'), (b'content-type', b'text/plain')]})

```python
await send({'type': 'http.response.start', 'status': 200, 'headers': [(b'content-security-policy', b'default-src *'), (b'content-type', b'text/plain')]})
```

### Step 8: await send({'type': 'http.response.body', 'body': b'ok', 'more_body': False})

```python
await send({'type': 'http.response.body', 'body': b'ok', 'more_body': False})
```

### Step 9: Call sent.append()

```python
sent.append(msg)
```


## Complete Example

```python
# Workflow
'If a downstream app already set CSP, middleware must replace it.'
import asyncio

async def inner_app(scope, receive, send):
    await send({'type': 'http.response.start', 'status': 200, 'headers': [(b'content-security-policy', b'default-src *'), (b'content-type', b'text/plain')]})
    await send({'type': 'http.response.body', 'body': b'ok', 'more_body': False})
mw = SecurityHeadersMiddleware(inner_app)
sent: list[dict] = []

async def receive():
    return {'type': 'http.request'}

async def send(msg):
    sent.append(msg)
asyncio.run(mw({'type': 'http', 'path': '/api/v3/brain', 'raw_path': b'/api/v3/brain'}, receive, send))
start = sent[0]
csp_values = [v for n, v in start['headers'] if n == b'content-security-policy']
assert len(csp_values) == 1, 'must have exactly one CSP header'
assert csp_values[0] != b'default-src *'
assert b"default-src 'self'" in csp_values[0]
ct_values = [v for n, v in start['headers'] if n == b'content-type']
assert ct_values == [b'text/plain']
```

## Next Steps


---

*Source: test_headers.py:282 | Complexity: Advanced | Last updated: 2026-05-05*