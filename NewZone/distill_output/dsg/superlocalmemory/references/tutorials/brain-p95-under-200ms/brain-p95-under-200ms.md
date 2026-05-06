# How To: Brain P95 Under 200Ms

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test brain p95 under 200ms

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `tempfile`
- `pathlib`
- `typing`
- `pytest`
- `fastapi`
- `fastapi.testclient`
- `superlocalmemory.core`
- `superlocalmemory.server.middleware.security_headers`
- `superlocalmemory.server.routes`
- `superlocalmemory.learning.database`
- `json`
- `superlocalmemory.learning.features`
- `time`
- `superlocalmemory.learning.database`
- `sqlite3`
- `importlib`
- `superlocalmemory.server.routes`
- `sys`
- `types`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes`
- `sqlite3`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes.brain`
- `sqlite3`
- `superlocalmemory.server.routes`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `superlocalmemory.server.routes`
- `superlocalmemory.learning.database`
- `sys`
- `types`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `sqlite3`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `datetime`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `datetime`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.learning.database`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes.brain`
- `superlocalmemory.server.routes`
- `superlocalmemory.cli.context_commands`
- `superlocalmemory.server.routes`
- `superlocalmemory.server.routes`
- `pathlib`
- `datetime`
- `superlocalmemory.learning.database`

**Setup Required:**
```python
# Fixtures: client, install_token
```

## Step-by-Step Guide

### Step 1: Assign samples = value

```python
samples = []
```

**Verification:**
```python
assert r.status_code == 200
```

### Step 2: Call samples.sort()

```python
samples.sort()
```

**Verification:**
```python
assert p95_ms <= 500.0, f'p95 too slow: {p95_ms:.2f} ms'
```

### Step 3: Assign p95_idx = max(...)

```python
p95_idx = max(0, int(0.95 * len(samples)) - 1)
```

### Step 4: Assign p95_ms = value

```python
p95_ms = samples[p95_idx]
```

**Verification:**
```python
assert p95_ms <= 500.0, f'p95 too slow: {p95_ms:.2f} ms'
```

### Step 5: Assign t0 = time.perf_counter(...)

```python
t0 = time.perf_counter()
```

### Step 6: Assign r = client.get(...)

```python
r = client.get('/api/v3/brain', headers={'X-Install-Token': install_token})
```

### Step 7: Call samples.append()

```python
samples.append((time.perf_counter() - t0) * 1000.0)
```

**Verification:**
```python
assert r.status_code == 200
```


## Complete Example

```python
# Setup
# Fixtures: client, install_token

# Workflow
import time
samples = []
for _ in range(20):
    t0 = time.perf_counter()
    r = client.get('/api/v3/brain', headers={'X-Install-Token': install_token})
    samples.append((time.perf_counter() - t0) * 1000.0)
    assert r.status_code == 200
samples.sort()
p95_idx = max(0, int(0.95 * len(samples)) - 1)
p95_ms = samples[p95_idx]
assert p95_ms <= 500.0, f'p95 too slow: {p95_ms:.2f} ms'
```

## Next Steps


---

*Source: test_brain_endpoint.py:284 | Complexity: Intermediate | Last updated: 2026-05-05*