# How To: Check Constraint Forbids Completed And Cancelled

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test check constraint forbids completed and cancelled

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

### Step 2: Assign rid = q.enqueue(...)

```python
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
```

### Step 3: Call q.close()

```python
q.close()
```

### Step 4: Call q._raw_execute()

```python
q._raw_execute("UPDATE recall_requests SET completed=1, cancelled=1, result_json='{}' WHERE request_id=?", (rid,))
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
import sqlite3
q = _make_queue(tmp_path)
rid = q.enqueue(query='x', limit_n=10, mode='B', agent_id='a', session_id='s')
with pytest.raises(sqlite3.IntegrityError):
    q._raw_execute("UPDATE recall_requests SET completed=1, cancelled=1, result_json='{}' WHERE request_id=?", (rid,))
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:206 | Complexity: Intermediate | Last updated: 2026-05-05*