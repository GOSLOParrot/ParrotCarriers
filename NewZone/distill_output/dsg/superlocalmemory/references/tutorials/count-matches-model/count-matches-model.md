# How To: Count Matches Model

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: test count matches model

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
assert actual == expected, log.fail(f'rid={rid} actual={actual} expected={expected}')
```

### Step 2: Assign log = _TraceLog(...)

```python
log = _TraceLog(seed=seed, ops=[])
```

**Verification:**
```python
assert actual >= 0, log.fail(f'rid={rid} subscriber_count went negative: {actual}')
```

### Step 3: Assign op = rng.choice(...)

```python
op = rng.choice(['enqueue', 'unsubscribe'])
```

### Step 4: Call log.ops.append()

```python
log.ops.append(op)
```

### Step 5: Assign rows = queue._conn.execute.fetchall(...)

```python
rows = queue._conn.execute('SELECT request_id, subscriber_count FROM recall_requests').fetchall()
```

### Step 6: Assign k_idx = rng.randrange(...)

```python
k_idx = rng.randrange(6)
```

### Step 7: Assign rid = queue.enqueue(...)

```python
rid = queue.enqueue(query=f'subq-{k_idx}', limit_n=5, mode='a', agent_id='ag', session_id='s')
```

### Step 8: Call rid_by_key.setdefault()

```python
rid_by_key.setdefault(k_idx, rid)
```

### Step 9: Assign rid = rng.choice(...)

```python
rid = rng.choice(list(rid_to_model_count.keys()))
```

### Step 10: Assign rid = value

```python
rid = r['request_id']
```

### Step 11: Assign actual = value

```python
actual = r['subscriber_count']
```

### Step 12: Assign expected = value

```python
expected = rid_to_model_count[rid]
```

**Verification:**
```python
assert actual == expected, log.fail(f'rid={rid} actual={actual} expected={expected}')
```

### Step 13: Call queue.unsubscribe()

```python
queue.unsubscribe(rid)
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
rng, seed = _seeded_rng()
log = _TraceLog(seed=seed, ops=[])
rid_to_model_count: defaultdict[str, int] = defaultdict(int)
rid_by_key: dict[int, str] = {}
for _ in range(_DEFAULT_OPS_PER_ITER * 4):
    op = rng.choice(['enqueue', 'unsubscribe'])
    log.ops.append(op)
    if op == 'enqueue':
        k_idx = rng.randrange(6)
        rid = queue.enqueue(query=f'subq-{k_idx}', limit_n=5, mode='a', agent_id='ag', session_id='s')
        rid_by_key.setdefault(k_idx, rid)
        rid_to_model_count[rid] += 1
    else:
        if not rid_to_model_count:
            continue
        rid = rng.choice(list(rid_to_model_count.keys()))
        if rid_to_model_count[rid] > 0:
            queue.unsubscribe(rid)
            rid_to_model_count[rid] -= 1
    rows = queue._conn.execute('SELECT request_id, subscriber_count FROM recall_requests').fetchall()
    for r in rows:
        rid = r['request_id']
        actual = r['subscriber_count']
        expected = rid_to_model_count[rid]
        assert actual == expected, log.fail(f'rid={rid} actual={actual} expected={expected}')
        assert actual >= 0, log.fail(f'rid={rid} subscriber_count went negative: {actual}')
```

## Next Steps


---

*Source: test_queue_invariants.py:178 | Complexity: Advanced | Last updated: 2026-05-05*