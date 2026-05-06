# How To: Worker Drains Enqueued Events

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Full producer → drain → pending_outcomes contract.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `time`
- `pathlib`
- `pytest`
- `superlocalmemory.learning`
- `superlocalmemory.learning.outcome_queue`
- `queue`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Full producer → drain → pending_outcomes contract.'

```python
'Full producer → drain → pending_outcomes contract.'
```

**Verification:**
```python
assert queue_size() == 1
```

### Step 2: Call _reset_for_testing()

```python
_reset_for_testing()
```

**Verification:**
```python
assert persisted == 1
```

### Step 3: Assign db_path = value

```python
db_path = tmp_path / 'memory.db'
```

**Verification:**
```python
assert len(rows) == 1
```

### Step 4: Call _mk_schema()

```python
_mk_schema(db_path)
```

**Verification:**
```python
assert rows[0][0] == 'sess-x'
```

### Step 5: Call enqueue_recall()

```python
enqueue_recall(RecallEvent(session_id='sess-x', profile_id='p', query='turboquant', fact_ids=('f1', 'f2'), query_id='qid-1'))
```

**Verification:**
```python
assert rows[0][1] == 'p'
```

### Step 6: Assign persisted = outcome_queue._drain_once(...)

```python
persisted = outcome_queue._drain_once(db_path)
```

**Verification:**
```python
assert rows[0][2] == 'pending'
```

### Step 7: Assign conn = sqlite3.connect(...)

```python
conn = sqlite3.connect(str(db_path))
```

### Step 8: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT session_id, profile_id, status FROM pending_outcomes').fetchall()
```

### Step 9: Call conn.close()

```python
conn.close()
```

**Verification:**
```python
assert len(rows) == 1
```

### Step 10: Call _reset_for_testing()

```python
_reset_for_testing()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Full producer → drain → pending_outcomes contract.'
_reset_for_testing()
db_path = tmp_path / 'memory.db'
_mk_schema(db_path)
enqueue_recall(RecallEvent(session_id='sess-x', profile_id='p', query='turboquant', fact_ids=('f1', 'f2'), query_id='qid-1'))
assert queue_size() == 1
persisted = outcome_queue._drain_once(db_path)
assert persisted == 1
conn = sqlite3.connect(str(db_path))
rows = conn.execute('SELECT session_id, profile_id, status FROM pending_outcomes').fetchall()
conn.close()
assert len(rows) == 1
assert rows[0][0] == 'sess-x'
assert rows[0][1] == 'p'
assert rows[0][2] == 'pending'
_reset_for_testing()
```

## Next Steps


---

*Source: test_s9_dash_outcome_queue.py:151 | Complexity: Advanced | Last updated: 2026-05-05*