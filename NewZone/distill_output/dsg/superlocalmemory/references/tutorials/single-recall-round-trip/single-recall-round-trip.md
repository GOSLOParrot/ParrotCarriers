# How To: Single Recall Round Trip

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test single recall round trip

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `threading`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign disp = _make_dispatcher(...)

```python
disp = _make_dispatcher(tmp_path)
```

**Verification:**
```python
assert out['hits'] == 3
```

### Step 2: Assign t = threading.Thread(...)

```python
t = threading.Thread(target=worker, daemon=True)
```

**Verification:**
```python
assert out['q'] == 'hello'
```

### Step 3: Call t.start()

```python
t.start()
```

### Step 4: Assign out = disp.dispatch(...)

```python
out = disp.dispatch(query='hello', limit_n=10, mode='B', agent_id='a', session_id='s', timeout_s=3.0)
```

### Step 5: Call t.join()

```python
t.join(timeout=2.0)
```

**Verification:**
```python
assert out['hits'] == 3
```

### Step 6: Call disp.close()

```python
disp.close()
```

### Step 7: Assign claim = disp.queue.claim_pending(...)

```python
claim = disp.queue.claim_pending(priority='high', stall_timeout_s=5.0)
```

### Step 8: Call disp.queue.complete()

```python
disp.queue.complete(claim['request_id'], received=claim['received'], result_json=json.dumps({'hits': 3, 'q': claim['query']}))
```

### Step 9: Call time.sleep()

```python
time.sleep(0.01)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
disp = _make_dispatcher(tmp_path)
results: list[dict] = []

def worker() -> None:
    for _ in range(20):
        claim = disp.queue.claim_pending(priority='high', stall_timeout_s=5.0)
        if claim is None:
            time.sleep(0.01)
            continue
        disp.queue.complete(claim['request_id'], received=claim['received'], result_json=json.dumps({'hits': 3, 'q': claim['query']}))
        return
t = threading.Thread(target=worker, daemon=True)
t.start()
out = disp.dispatch(query='hello', limit_n=10, mode='B', agent_id='a', session_id='s', timeout_s=3.0)
t.join(timeout=2.0)
assert out['hits'] == 3
assert out['q'] == 'hello'
disp.close()
```

## Next Steps


---

*Source: test_queue_dispatcher.py:27 | Complexity: Advanced | Last updated: 2026-05-05*