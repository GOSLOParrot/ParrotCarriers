# How To: Dedup On Query Hash

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test dedup on query hash

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
assert rid == seen_rids[k_idx], log.fail(f'dedup broke: key {k_idx} produced {rid} but earlier produced {seen_rids[k_idx]}')
```

### Step 2: Assign log = _TraceLog(...)

```python
log = _TraceLog(seed=seed, ops=[])
```

**Verification:**
```python
assert rows == len(seen_rids), log.fail(f'row count {rows} != distinct keys {len(seen_rids)}')
```

### Step 3: Assign key_universe = value

```python
key_universe = [{'query': f'same-q-{i}', 'limit_n': 5, 'mode': 'a', 'agent_id': 'ag', 'session_id': 's', 'tenant_id': ''} for i in range(8)]
```

### Step 4: Assign rows = value

```python
rows = queue._conn.execute('SELECT COUNT(*) FROM recall_requests').fetchone()[0]
```

**Verification:**
```python
assert rows == len(seen_rids), log.fail(f'row count {rows} != distinct keys {len(seen_rids)}')
```

### Step 5: Assign k_idx = rng.randrange(...)

```python
k_idx = rng.randrange(len(key_universe))
```

### Step 6: Assign k = value

```python
k = key_universe[k_idx]
```

### Step 7: Call log.ops.append()

```python
log.ops.append(f'enq[{k_idx}]')
```

### Step 8: Assign rid = queue.enqueue(...)

```python
rid = queue.enqueue(**k)
```

**Verification:**
```python
assert rid == seen_rids[k_idx], log.fail(f'dedup broke: key {k_idx} produced {rid} but earlier produced {seen_rids[k_idx]}')
```

### Step 9: Assign unknown = rid

```python
seen_rids[k_idx] = rid
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
rng, seed = _seeded_rng()
log = _TraceLog(seed=seed, ops=[])
key_universe = [{'query': f'same-q-{i}', 'limit_n': 5, 'mode': 'a', 'agent_id': 'ag', 'session_id': 's', 'tenant_id': ''} for i in range(8)]
seen_rids: dict[int, str] = {}
for _ in range(_DEFAULT_OPS_PER_ITER * 3):
    k_idx = rng.randrange(len(key_universe))
    k = key_universe[k_idx]
    log.ops.append(f'enq[{k_idx}]')
    rid = queue.enqueue(**k)
    if k_idx in seen_rids:
        assert rid == seen_rids[k_idx], log.fail(f'dedup broke: key {k_idx} produced {rid} but earlier produced {seen_rids[k_idx]}')
    else:
        seen_rids[k_idx] = rid
rows = queue._conn.execute('SELECT COUNT(*) FROM recall_requests').fetchone()[0]
assert rows == len(seen_rids), log.fail(f'row count {rows} != distinct keys {len(seen_rids)}')
```

## Next Steps


---

*Source: test_queue_invariants.py:134 | Complexity: Advanced | Last updated: 2026-05-05*