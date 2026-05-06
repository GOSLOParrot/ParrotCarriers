# How To: Claim Twice Sees Updated Received

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test claim twice sees updated received

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.core`
- `sqlite3`
- `sqlite3`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign q = _make_queue(...)

```python
q = _make_queue(tmp_path)
```

**Verification:**
```python
assert c1['received'] == 1
```

### Step 2: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
```

**Verification:**
```python
assert c2 is not None
```

### Step 3: Assign c1 = q.claim_pending(...)

```python
c1 = q.claim_pending(priority='high', stall_timeout_s=0.01)
```

**Verification:**
```python
assert c2['request_id'] == rid
```

### Step 4: Call time.sleep()

```python
time.sleep(0.02)
```

**Verification:**
```python
assert c2['received'] == 2
```

### Step 5: Assign c2 = q.claim_pending(...)

```python
c2 = q.claim_pending(priority='high', stall_timeout_s=0.01)
```

**Verification:**
```python
assert c2 is not None
```

### Step 6: Call q.close()

```python
q.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
q = _make_queue(tmp_path)
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
c1 = q.claim_pending(priority='high', stall_timeout_s=0.01)
assert c1['received'] == 1
time.sleep(0.02)
c2 = q.claim_pending(priority='high', stall_timeout_s=0.01)
assert c2 is not None
assert c2['request_id'] == rid
assert c2['received'] == 2
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:92 | Complexity: Intermediate | Last updated: 2026-05-05*