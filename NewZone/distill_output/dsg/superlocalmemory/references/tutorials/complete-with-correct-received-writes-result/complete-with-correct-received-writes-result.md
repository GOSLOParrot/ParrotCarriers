# How To: Complete With Correct Received Writes Result

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test complete with correct received writes result

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
assert n == 1
```

### Step 2: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
```

**Verification:**
```python
assert row['completed'] == 1
```

### Step 3: Assign claim = q.claim_pending(...)

```python
claim = q.claim_pending(priority='high', stall_timeout_s=25.0)
```

**Verification:**
```python
assert row['result_json'] == json.dumps({'ok': True})
```

### Step 4: Assign n = q.complete(...)

```python
n = q.complete(rid, received=claim['received'], result_json=json.dumps({'ok': True}))
```

**Verification:**
```python
assert n == 1
```

### Step 5: Assign row = q._get_row(...)

```python
row = q._get_row(rid)
```

**Verification:**
```python
assert row['completed'] == 1
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
claim = q.claim_pending(priority='high', stall_timeout_s=25.0)
n = q.complete(rid, received=claim['received'], result_json=json.dumps({'ok': True}))
assert n == 1
row = q._get_row(rid)
assert row['completed'] == 1
assert row['result_json'] == json.dumps({'ok': True})
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:105 | Complexity: Intermediate | Last updated: 2026-05-05*