# How To: No Dual Terminal States

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test no dual terminal states

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
assert active <= 1, log.fail(f'row has {active} terminal flags: {dict(r)}')
```

### Step 2: Assign log = _TraceLog(...)

```python
log = _TraceLog(seed=seed, ops=[])
```

### Step 3: Assign rows = queue._conn.execute.fetchall(...)

```python
rows = queue._conn.execute('SELECT completed, cancelled, dead_letter FROM recall_requests').fetchall()
```

### Step 4: Assign op = rng.choice(...)

```python
op = rng.choice(['enqueue_claim_complete', 'enqueue_then_cancel', 'enqueue_then_dlq'])
```

### Step 5: Call log.ops.append()

```python
log.ops.append(op)
```

### Step 6: Assign rid = _enqueue_unique(...)

```python
rid = _enqueue_unique(queue, rng, f'p9-{i}')
```

### Step 7: Assign claimed = queue.claim_pending(...)

```python
claimed = queue.claim_pending(priority='high', stall_timeout_s=0.5)
```

### Step 8: Assign active = value

```python
active = int(bool(r['completed'])) + int(bool(r['cancelled'])) + int(bool(r['dead_letter']))
```

**Verification:**
```python
assert active <= 1, log.fail(f'row has {active} terminal flags: {dict(r)}')
```

### Step 9: Call queue.complete()

```python
queue.complete(rid, received=claimed['received'], result_json=json.dumps({'ok': True}))
```

### Step 10: Call queue._force_cancelled()

```python
queue._force_cancelled(rid)
```

### Step 11: Call queue.mark_dead_letter()

```python
queue.mark_dead_letter(rid, reason='synthetic')
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
rng, seed = _seeded_rng()
log = _TraceLog(seed=seed, ops=[])
for i in range(50):
    op = rng.choice(['enqueue_claim_complete', 'enqueue_then_cancel', 'enqueue_then_dlq'])
    log.ops.append(op)
    rid = _enqueue_unique(queue, rng, f'p9-{i}')
    claimed = queue.claim_pending(priority='high', stall_timeout_s=0.5)
    if op == 'enqueue_claim_complete':
        queue.complete(rid, received=claimed['received'], result_json=json.dumps({'ok': True}))
    elif op == 'enqueue_then_cancel':
        queue._force_cancelled(rid)
    else:
        queue.mark_dead_letter(rid, reason='synthetic')
rows = queue._conn.execute('SELECT completed, cancelled, dead_letter FROM recall_requests').fetchall()
for r in rows:
    active = int(bool(r['completed'])) + int(bool(r['cancelled'])) + int(bool(r['dead_letter']))
    assert active <= 1, log.fail(f'row has {active} terminal flags: {dict(r)}')
```

## Next Steps


---

*Source: test_queue_invariants.py:303 | Complexity: Advanced | Last updated: 2026-05-05*