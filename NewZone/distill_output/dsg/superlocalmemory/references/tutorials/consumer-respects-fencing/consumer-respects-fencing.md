# How To: Consumer Respects Fencing

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Consumer uses fenced writes; stale received value is rejected.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `asyncio`
- `json`
- `time`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.recall_queue`
- `superlocalmemory.core.queue_consumer`
- `importlib`
- `sys`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Consumer uses fenced writes; stale received value is rejected.'

```python
'Consumer uses fenced writes; stale received value is rejected.'
```

**Verification:**
```python
assert c1 is not None
```

### Step 2: Assign q = _make_queue(...)

```python
q = _make_queue(tmp_path)
```

**Verification:**
```python
assert c2 is not None
```

### Step 3: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='fenced', limit_n=3, mode='B', agent_id='hook', session_id='s1')
```

**Verification:**
```python
assert n == 0, 'Stale write should be fenced out'
```

### Step 4: Assign c1 = q.claim_pending(...)

```python
c1 = q.claim_pending(priority='high', stall_timeout_s=0.01)
```

**Verification:**
```python
assert n == 1
```

### Step 5: Call time.sleep()

```python
time.sleep(0.02)
```

### Step 6: Assign c2 = q.claim_pending(...)

```python
c2 = q.claim_pending(priority='high', stall_timeout_s=25.0)
```

**Verification:**
```python
assert c2 is not None
```

### Step 7: Assign n = q.complete(...)

```python
n = q.complete(rid, received=1, result_json=json.dumps({'stale': True}))
```

**Verification:**
```python
assert n == 0, 'Stale write should be fenced out'
```

### Step 8: Assign n = q.complete(...)

```python
n = q.complete(rid, received=2, result_json=json.dumps({'ok': True}))
```

**Verification:**
```python
assert n == 1
```

### Step 9: Call q.close()

```python
q.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Consumer uses fenced writes; stale received value is rejected.'
q = _make_queue(tmp_path)
rid = q.enqueue(query='fenced', limit_n=3, mode='B', agent_id='hook', session_id='s1')
c1 = q.claim_pending(priority='high', stall_timeout_s=0.01)
assert c1 is not None
time.sleep(0.02)
c2 = q.claim_pending(priority='high', stall_timeout_s=25.0)
assert c2 is not None
n = q.complete(rid, received=1, result_json=json.dumps({'stale': True}))
assert n == 0, 'Stale write should be fenced out'
n = q.complete(rid, received=2, result_json=json.dumps({'ok': True}))
assert n == 1
q.close()
```

## Next Steps


---

*Source: test_queue_consumer.py:255 | Complexity: Advanced | Last updated: 2026-05-05*