# How To: Enqueue Dedup Hit Returns Existing Id And Bumps Subscriber

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test enqueue dedup hit returns existing id and bumps subscriber

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
assert rid1 == rid2
```

### Step 2: Assign rid1 = q.enqueue(...)

```python
rid1 = q.enqueue(query='same', limit_n=10, mode='B', agent_id='a', session_id='s')
```

**Verification:**
```python
assert row['subscriber_count'] == 2
```

### Step 3: Assign rid2 = q.enqueue(...)

```python
rid2 = q.enqueue(query='same', limit_n=10, mode='B', agent_id='a', session_id='s')
```

**Verification:**
```python
assert rid1 == rid2
```

### Step 4: Assign row = q._get_row(...)

```python
row = q._get_row(rid1)
```

**Verification:**
```python
assert row['subscriber_count'] == 2
```

### Step 5: Call q.close()

```python
q.close()
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
q = _make_queue(tmp_path)
rid1 = q.enqueue(query='same', limit_n=10, mode='B', agent_id='a', session_id='s')
rid2 = q.enqueue(query='same', limit_n=10, mode='B', agent_id='a', session_id='s')
assert rid1 == rid2
row = q._get_row(rid1)
assert row['subscriber_count'] == 2
q.close()
```

## Next Steps


---

*Source: test_recall_queue.py:45 | Complexity: Intermediate | Last updated: 2026-05-05*