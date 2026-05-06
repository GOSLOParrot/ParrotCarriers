# How To: Poll Result Raises Dead Letter Fast

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test poll result raises dead letter fast

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

### Step 1: Assign rq = _imports(...)

```python
rq = _imports()
```

**Verification:**
```python
assert elapsed < 0.5, f'DLQ did not fast-fail; waited {elapsed:.2f}s'
```

### Step 2: Assign q = _make_queue(...)

```python
q = _make_queue(tmp_path)
```

**Verification:**
```python
assert exc.value.request_id == rid
```

### Step 3: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
```

**Verification:**
```python
assert 'max_receives' in exc.value.reason
```

### Step 4: Call q.claim_pending()

```python
q.claim_pending(priority='high', stall_timeout_s=25.0)
```

### Step 5: Call q.mark_dead_letter()

```python
q.mark_dead_letter(rid, reason='max_receives_exceeded')
```

### Step 6: Assign t0 = time.monotonic(...)

```python
t0 = time.monotonic()
```

### Step 7: Assign elapsed = value

```python
elapsed = time.monotonic() - t0
```

**Verification:**
```python
assert elapsed < 0.5, f'DLQ did not fast-fail; waited {elapsed:.2f}s'
```

### Step 8: Call q.close()

```python
q.close()
```

### Step 9: Call q.poll_result()

```python
q.poll_result(rid, timeout_s=5.0)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
rq = _imports()
q = _make_queue(tmp_path)
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
q.claim_pending(priority='high', stall_timeout_s=25.0)
q.mark_dead_letter(rid, reason='max_receives_exceeded')
t0 = time.monotonic()
with pytest.raises(rq.DeadLetterError) as exc:
    q.poll_result(rid, timeout_s=5.0)
elapsed = time.monotonic() - t0
assert elapsed < 0.5, f'DLQ did not fast-fail; waited {elapsed:.2f}s'
assert exc.value.request_id == rid
assert 'max_receives' in exc.value.reason
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:167 | Complexity: Advanced | Last updated: 2026-05-05*