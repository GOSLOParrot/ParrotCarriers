# How To: Complete With Stale Received Is Fenced Out

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test complete with stale received is fenced out

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
assert n == 0, 'Stale write must be fenced out'
```

### Step 2: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
```

**Verification:**
```python
assert row['completed'] == 0
```

### Step 3: Call q.claim_pending()

```python
q.claim_pending(priority='high', stall_timeout_s=0.01)
```

**Verification:**
```python
assert row['result_json'] is None
```

### Step 4: Call time.sleep()

```python
time.sleep(0.02)
```

### Step 5: Call q.claim_pending()

```python
q.claim_pending(priority='high', stall_timeout_s=25.0)
```

### Step 6: Assign n = q.complete(...)

```python
n = q.complete(rid, received=1, result_json=json.dumps({'stale': True}))
```

**Verification:**
```python
assert n == 0, 'Stale write must be fenced out'
```

### Step 7: Assign row = q._get_row(...)

```python
row = q._get_row(rid)
```

**Verification:**
```python
assert row['completed'] == 0
```

### Step 8: Call q.close()

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
q.claim_pending(priority='high', stall_timeout_s=0.01)
time.sleep(0.02)
q.claim_pending(priority='high', stall_timeout_s=25.0)
n = q.complete(rid, received=1, result_json=json.dumps({'stale': True}))
assert n == 0, 'Stale write must be fenced out'
row = q._get_row(rid)
assert row['completed'] == 0
assert row['result_json'] is None
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:118 | Complexity: Advanced | Last updated: 2026-05-05*