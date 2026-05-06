# How To: Complete On Cancelled Row Is Fenced

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test complete on cancelled row is fenced

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
assert n == 0
```

### Step 2: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
```

### Step 3: Assign claim = q.claim_pending(...)

```python
claim = q.claim_pending(priority='high', stall_timeout_s=25.0)
```

### Step 4: Call q._force_cancelled()

```python
q._force_cancelled(rid)
```

### Step 5: Assign n = q.complete(...)

```python
n = q.complete(rid, received=claim['received'], result_json='{}')
```

**Verification:**
```python
assert n == 0
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
q._force_cancelled(rid)
n = q.complete(rid, received=claim['received'], result_json='{}')
assert n == 0
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:133 | Complexity: Intermediate | Last updated: 2026-05-05*