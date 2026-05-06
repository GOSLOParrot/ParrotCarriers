# How To: Stale Received Rejected

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test stale received rejected

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `os`
- `random`
- `collections`
- `dataclasses`
- `pathlib`
- `pytest`
- `superlocalmemory.core.recall_queue`

**Setup Required:**
```python
# Fixtures: queue
```

## Step-by-Step Guide

### Step 1: Assign unknown = _seeded_rng(...)

```python
rng, seed = _seeded_rng()
```

**Verification:**
```python
assert claimed1 is not None and claimed1['request_id'] == rid
```

### Step 2: Assign log = _TraceLog(...)

```python
log = _TraceLog(seed=seed, ops=[])
```

**Verification:**
```python
assert claimed2 is not None and claimed2['request_id'] == rid
```

### Step 3: Call log.ops.append()

```python
log.ops.append(f'round-{i}')
```

**Verification:**
```python
assert stale_rowcount == 0, log.fail('stale complete() landed')
```

### Step 4: Assign rid = _enqueue_unique(...)

```python
rid = _enqueue_unique(queue, rng, f'p1-{i}')
```

**Verification:**
```python
assert fresh_rowcount == 1
```

### Step 5: Assign claimed1 = queue.claim_pending(...)

```python
claimed1 = queue.claim_pending(priority='high', stall_timeout_s=0.0)
```

**Verification:**
```python
assert again == 0
```

### Step 6: Call queue._conn.execute()

```python
queue._conn.execute('UPDATE recall_requests SET claim_expires_at = 0 WHERE request_id = ?', (rid,))
```

### Step 7: Assign claimed2 = queue.claim_pending(...)

```python
claimed2 = queue.claim_pending(priority='high', stall_timeout_s=0.05)
```

**Verification:**
```python
assert claimed2 is not None and claimed2['request_id'] == rid
```

### Step 8: Assign stale_rowcount = queue.complete(...)

```python
stale_rowcount = queue.complete(rid, received=claimed1['received'], result_json=json.dumps({'stale': True}))
```

**Verification:**
```python
assert stale_rowcount == 0, log.fail('stale complete() landed')
```

### Step 9: Assign fresh_rowcount = queue.complete(...)

```python
fresh_rowcount = queue.complete(rid, received=claimed2['received'], result_json=json.dumps({'fresh': True}))
```

**Verification:**
```python
assert fresh_rowcount == 1
```

### Step 10: Assign again = queue.complete(...)

```python
again = queue.complete(rid, received=claimed2['received'], result_json=json.dumps({'replay': True}))
```

**Verification:**
```python
assert again == 0
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
rng, seed = _seeded_rng()
log = _TraceLog(seed=seed, ops=[])
for i in range(20):
    log.ops.append(f'round-{i}')
    rid = _enqueue_unique(queue, rng, f'p1-{i}')
    claimed1 = queue.claim_pending(priority='high', stall_timeout_s=0.0)
    assert claimed1 is not None and claimed1['request_id'] == rid
    queue._conn.execute('UPDATE recall_requests SET claim_expires_at = 0 WHERE request_id = ?', (rid,))
    claimed2 = queue.claim_pending(priority='high', stall_timeout_s=0.05)
    assert claimed2 is not None and claimed2['request_id'] == rid
    stale_rowcount = queue.complete(rid, received=claimed1['received'], result_json=json.dumps({'stale': True}))
    assert stale_rowcount == 0, log.fail('stale complete() landed')
    fresh_rowcount = queue.complete(rid, received=claimed2['received'], result_json=json.dumps({'fresh': True}))
    assert fresh_rowcount == 1
    again = queue.complete(rid, received=claimed2['received'], result_json=json.dumps({'replay': True}))
    assert again == 0
```

## Next Steps


---

*Source: test_queue_invariants.py:229 | Complexity: Advanced | Last updated: 2026-05-05*