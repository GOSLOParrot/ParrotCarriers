# How To: Poll Result Returns Completed

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test poll result returns completed

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
assert payload == {'hits': 3}
```

### Step 2: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
```

### Step 3: Assign claim = q.claim_pending(...)

```python
claim = q.claim_pending(priority='high', stall_timeout_s=25.0)
```

### Step 4: Call q.complete()

```python
q.complete(rid, received=claim['received'], result_json=json.dumps({'hits': 3}))
```

### Step 5: Assign payload = q.poll_result(...)

```python
payload = q.poll_result(rid, timeout_s=1.0)
```

**Verification:**
```python
assert payload == {'hits': 3}
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
q.complete(rid, received=claim['received'], result_json=json.dumps({'hits': 3}))
payload = q.poll_result(rid, timeout_s=1.0)
assert payload == {'hits': 3}
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:157 | Complexity: Intermediate | Last updated: 2026-05-05*