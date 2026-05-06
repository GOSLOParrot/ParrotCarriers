# How To: Chaos 3 Clock Skew

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Wall-clock-based claim_expires_at must survive NTP jumps per
§1.3 jump detection. We can't change the system clock inside a
test run without sudo, so we simulate by directly bumping stored
claim_expires_at values and running the claim loop.

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

### Step 1: "Wall-clock-based claim_expires_at must survive NTP jumps per\n    §1.3 jump detection. We can't change the system clock inside a\n    test run without sudo, so we simulate by directly bumping stored\n    claim_expires_at values and running the claim loop."

```python
"Wall-clock-based claim_expires_at must survive NTP jumps per\n    §1.3 jump detection. We can't change the system clock inside a\n    test run without sudo, so we simulate by directly bumping stored\n    claim_expires_at values and running the claim loop."
```

**Verification:**
```python
assert claimed is not None and claimed['request_id'] == rid
```

### Step 2: Assign rid = queue.enqueue(...)

```python
rid = queue.enqueue(query='clock-test', limit_n=3, mode='a', agent_id='chaos3', session_id='s')
```

**Verification:**
```python
assert reclaimed is not None, 'after forward jump, expired claim must be reclaimable'
```

### Step 3: Assign claimed = queue.claim_pending(...)

```python
claimed = queue.claim_pending(priority='high', stall_timeout_s=25.0)
```

**Verification:**
```python
assert nothing is None, 'backward jump must not prematurely expire a valid claim'
```

### Step 4: Call queue._conn.execute()

```python
queue._conn.execute('UPDATE recall_requests SET claim_expires_at = ? WHERE request_id = ?', (time.time() - 300, rid))
```

### Step 5: Assign reclaimed = queue.claim_pending(...)

```python
reclaimed = queue.claim_pending(priority='high', stall_timeout_s=25.0)
```

**Verification:**
```python
assert reclaimed is not None, 'after forward jump, expired claim must be reclaimable'
```

### Step 6: Call queue._conn.execute()

```python
queue._conn.execute('UPDATE recall_requests SET claim_expires_at = ? WHERE request_id = ?', (time.time() + 600, rid))
```

### Step 7: Assign nothing = queue.claim_pending(...)

```python
nothing = queue.claim_pending(priority='high', stall_timeout_s=25.0)
```

**Verification:**
```python
assert nothing is None, 'backward jump must not prematurely expire a valid claim'
```


## Complete Example

```python
# Setup
# Fixtures: queue

# Workflow
"Wall-clock-based claim_expires_at must survive NTP jumps per\n    §1.3 jump detection. We can't change the system clock inside a\n    test run without sudo, so we simulate by directly bumping stored\n    claim_expires_at values and running the claim loop."
rid = queue.enqueue(query='clock-test', limit_n=3, mode='a', agent_id='chaos3', session_id='s')
claimed = queue.claim_pending(priority='high', stall_timeout_s=25.0)
assert claimed is not None and claimed['request_id'] == rid
queue._conn.execute('UPDATE recall_requests SET claim_expires_at = ? WHERE request_id = ?', (time.time() - 300, rid))
reclaimed = queue.claim_pending(priority='high', stall_timeout_s=25.0)
assert reclaimed is not None, 'after forward jump, expired claim must be reclaimable'
queue._conn.execute('UPDATE recall_requests SET claim_expires_at = ? WHERE request_id = ?', (time.time() + 600, rid))
nothing = queue.claim_pending(priority='high', stall_timeout_s=25.0)
assert nothing is None, 'backward jump must not prematurely expire a valid claim'
```

## Next Steps


---

*Source: test_chaos_queue.py:157 | Complexity: Intermediate | Last updated: 2026-05-05*