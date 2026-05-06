# How To: Chaos 4 Stop Cont Worker

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: A stalled worker (pretending to STOP) must have its claim
re-claimed after the stall_timeout. When it wakes up (CONT) and
tries to complete with its stale received, the fence rejects.

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

### Step 1: 'A stalled worker (pretending to STOP) must have its claim\n    re-claimed after the stall_timeout. When it wakes up (CONT) and\n    tries to complete with its stale received, the fence rejects.'

```python
'A stalled worker (pretending to STOP) must have its claim\n    re-claimed after the stall_timeout. When it wakes up (CONT) and\n    tries to complete with its stale received, the fence rejects.'
```

**Verification:**
```python
assert claimed2 is not None
```

### Step 2: Assign rid = queue.enqueue(...)

```python
rid = queue.enqueue(query='stop-cont', limit_n=3, mode='a', agent_id='chaos4', session_id='s', stall_timeout_s=0.05)
```

**Verification:**
```python
assert landed_stale == 0, 'stale STOPped worker must be fenced out'
```

### Step 3: Assign claimed1 = queue.claim_pending(...)

```python
claimed1 = queue.claim_pending(priority='high', stall_timeout_s=0.05)
```

**Verification:**
```python
assert landed_fresh == 1
```

### Step 4: Call time.sleep()

```python
time.sleep(0.1)
```

### Step 5: Assign claimed2 = queue.claim_pending(...)

```python
claimed2 = queue.claim_pending(priority='high', stall_timeout_s=0.5)
```

**Verification:**
```python
assert claimed2 is not None
```

### Step 6: Assign landed_stale = queue.complete(...)

```python
landed_stale = queue.complete(rid, received=claimed1['received'], result_json=json.dumps({'stale': True}))
```

**Verification:**
```python
assert landed_stale == 0, 'stale STOPped worker must be fenced out'
```

### Step 7: Assign landed_fresh = queue.complete(...)

```python
landed_fresh = queue.complete(rid, received=claimed2['received'], result_json=json.dumps({'fresh': True}))
```

**Verification:**
```python
assert landed_fresh == 1
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
'A stalled worker (pretending to STOP) must have its claim\n    re-claimed after the stall_timeout. When it wakes up (CONT) and\n    tries to complete with its stale received, the fence rejects.'
rid = queue.enqueue(query='stop-cont', limit_n=3, mode='a', agent_id='chaos4', session_id='s', stall_timeout_s=0.05)
claimed1 = queue.claim_pending(priority='high', stall_timeout_s=0.05)
time.sleep(0.1)
claimed2 = queue.claim_pending(priority='high', stall_timeout_s=0.5)
assert claimed2 is not None
landed_stale = queue.complete(rid, received=claimed1['received'], result_json=json.dumps({'stale': True}))
assert landed_stale == 0, 'stale STOPped worker must be fenced out'
landed_fresh = queue.complete(rid, received=claimed2['received'], result_json=json.dumps({'fresh': True}))
assert landed_fresh == 1
```

## Next Steps


---

*Source: test_chaos_queue.py:192 | Complexity: Intermediate | Last updated: 2026-05-05*