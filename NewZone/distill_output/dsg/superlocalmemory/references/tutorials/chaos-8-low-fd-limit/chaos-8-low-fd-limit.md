# How To: Chaos 8 Low Fd Limit

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Connection pool backpressure; no FD leak.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `sys`
- `tempfile`
- `threading`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core.recall_queue`
- `resource`

**Setup Required:**
```python
# Fixtures: queue
```

## Step-by-Step Guide

### Step 1: 'Connection pool backpressure; no FD leak.'

```python
'Connection pool backpressure; no FD leak.'
```

**Verification:**
```python
assert len(errors) < 50, f'too many FD failures: {len(errors)}'
```

### Step 2: Assign unknown = resource.getrlimit(...)

```python
soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
```

### Step 3: Assign threads = value

```python
threads = [threading.Thread(target=_worker, args=(i,)) for i in range(10)]
```

**Verification:**
```python
assert len(errors) < 50, f'too many FD failures: {len(errors)}'
```

### Step 4: Call resource.setrlimit()

```python
resource.setrlimit(resource.RLIMIT_NOFILE, (min(64, hard), hard))
```

### Step 5: Call resource.setrlimit()

```python
resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
```

### Step 6: Call pytest.skip()

```python
pytest.skip('resource module unavailable (likely Windows)')
```

### Step 7: Call pytest.skip()

```python
pytest.skip('cannot lower FD limit in this environment')
```

### Step 8: Call t.start()

```python
t.start()
```

### Step 9: Call t.join()

```python
t.join(timeout=60)
```

### Step 10: Assign rid = queue.enqueue(...)

```python
rid = queue.enqueue(query=f'c8-{tag}-{i}', limit_n=3, mode='a', agent_id=f'c8-{tag}', session_id='s')
```

### Step 11: Assign claimed = queue.claim_pending(...)

```python
claimed = queue.claim_pending(priority='high', stall_timeout_s=1.0)
```

### Step 12: Call errors.append()

```python
errors.append(exc)
```

### Step 13: Call queue.complete()

```python
queue.complete(claimed['request_id'], received=claimed['received'], result_json=json.dumps({'c8': True}))
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
'Connection pool backpressure; no FD leak.'
try:
    import resource
except ImportError:
    pytest.skip('resource module unavailable (likely Windows)')
soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
try:
    resource.setrlimit(resource.RLIMIT_NOFILE, (min(64, hard), hard))
except (ValueError, OSError):
    pytest.skip('cannot lower FD limit in this environment')
errors: list[Exception] = []

def _worker(tag):
    try:
        for i in range(20):
            rid = queue.enqueue(query=f'c8-{tag}-{i}', limit_n=3, mode='a', agent_id=f'c8-{tag}', session_id='s')
            claimed = queue.claim_pending(priority='high', stall_timeout_s=1.0)
            if claimed:
                queue.complete(claimed['request_id'], received=claimed['received'], result_json=json.dumps({'c8': True}))
    except Exception as exc:
        errors.append(exc)
threads = [threading.Thread(target=_worker, args=(i,)) for i in range(10)]
try:
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
finally:
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
assert len(errors) < 50, f'too many FD failures: {len(errors)}'
```

## Next Steps


---

*Source: test_chaos_queue.py:328 | Complexity: Advanced | Last updated: 2026-05-05*