# How To: Cancelled Rows Never Completed

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test cancelled rows never completed

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
assert claimed is not None
```

### Step 2: Assign log = _TraceLog(...)

```python
log = _TraceLog(seed=seed, ops=[])
```

**Verification:**
```python
assert landed == 0, log.fail('complete() landed post-cancel')
```

### Step 3: Assign rows = queue._conn.execute.fetchall(...)

```python
rows = queue._conn.execute('SELECT result_json FROM recall_requests WHERE cancelled = 1').fetchall()
```

**Verification:**
```python
assert r['result_json'] is None or r['result_json'] == '', log.fail(f"cancelled row has result_json: {r['result_json']!r}")
```

### Step 4: Assign rid = _enqueue_unique(...)

```python
rid = _enqueue_unique(queue, rng, f'p7-{i}')
```

### Step 5: Assign claimed = queue.claim_pending(...)

```python
claimed = queue.claim_pending(priority='high', stall_timeout_s=0.5)
```

**Verification:**
```python
assert claimed is not None
```

### Step 6: Call queue._force_cancelled()

```python
queue._force_cancelled(rid)
```

### Step 7: Assign landed = queue.complete(...)

```python
landed = queue.complete(rid, received=claimed['received'], result_json=json.dumps({'after_cancel': True}))
```

**Verification:**
```python
assert landed == 0, log.fail('complete() landed post-cancel')
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
rng, seed = _seeded_rng()
log = _TraceLog(seed=seed, ops=[])
for i in range(40):
    rid = _enqueue_unique(queue, rng, f'p7-{i}')
    claimed = queue.claim_pending(priority='high', stall_timeout_s=0.5)
    assert claimed is not None
    queue._force_cancelled(rid)
    landed = queue.complete(rid, received=claimed['received'], result_json=json.dumps({'after_cancel': True}))
    assert landed == 0, log.fail('complete() landed post-cancel')
rows = queue._conn.execute('SELECT result_json FROM recall_requests WHERE cancelled = 1').fetchall()
for r in rows:
    assert r['result_json'] is None or r['result_json'] == '', log.fail(f"cancelled row has result_json: {r['result_json']!r}")
```

## Next Steps


---

*Source: test_queue_invariants.py:273 | Complexity: Intermediate | Last updated: 2026-05-05*