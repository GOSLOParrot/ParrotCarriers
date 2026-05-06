# How To: Enqueue Drops Oldest On Overflow

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Queue has a cap — overflow drops oldest, never raises.

## Prerequisites

**Required Modules:**
- `__future__`
- `sqlite3`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.outcome_queue`
- `queue`


## Step-by-Step Guide

### Step 1: 'Queue has a cap — overflow drops oldest, never raises.'

```python
'Queue has a cap — overflow drops oldest, never raises.'
```

**Verification:**
```python
assert queue_size() <= 3
```

### Step 2: Call _reset_for_testing()

```python
_reset_for_testing()
```

**Verification:**
```python
assert get_counters()['recall_dropped_queue_full'] >= 2
```

### Step 3: Assign original = value

```python
original = outcome_queue._MAX_QUEUE
```

### Step 4: Assign outcome_queue._queue = _q.Queue(...)

```python
outcome_queue._queue = _q.Queue(maxsize=3)
```

**Verification:**
```python
assert queue_size() <= 3
```

### Step 5: Assign outcome_queue._queue = _q.Queue(...)

```python
outcome_queue._queue = _q.Queue(maxsize=original)
```

### Step 6: Call _reset_for_testing()

```python
_reset_for_testing()
```

### Step 7: Call enqueue_recall()

```python
enqueue_recall(RecallEvent(session_id=f's{i}', profile_id='p', query='q', fact_ids=('f',)))
```


## Complete Example

```python
# Workflow
'Queue has a cap — overflow drops oldest, never raises.'
_reset_for_testing()
original = outcome_queue._MAX_QUEUE
import queue as _q
outcome_queue._queue = _q.Queue(maxsize=3)
try:
    for i in range(5):
        enqueue_recall(RecallEvent(session_id=f's{i}', profile_id='p', query='q', fact_ids=('f',)))
    assert queue_size() <= 3
    assert get_counters()['recall_dropped_queue_full'] >= 2
finally:
    outcome_queue._queue = _q.Queue(maxsize=original)
    _reset_for_testing()
```

## Next Steps


---

*Source: test_s9_dash_outcome_queue.py:96 | Complexity: Advanced | Last updated: 2026-05-05*