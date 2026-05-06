# How To: Reap Stale Finalizes Expired Pending

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test reap stale finalizes expired pending

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `os`
- `sqlite3`
- `statistics`
- `threading`
- `time`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`
- `superlocalmemory.learning.reward`

**Setup Required:**
```python
# Fixtures: memory_db
```

## Step-by-Step Guide

### Step 1: Assign now = value

```python
now = {'ms': 1000000}
```

**Verification:**
```python
assert reaped == 1
```

### Step 2: Assign m = EngagementRewardModel(...)

```python
m = EngagementRewardModel(memory_db, clock_ms=lambda: now['ms'])
```

**Verification:**
```python
assert row is not None
```

### Step 3: Assign outcome_id = m.record_recall(...)

```python
outcome_id = m.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
```

**Verification:**
```python
assert row['settled'] == 1
```

### Step 4: Assign reaped = m.reap_stale(...)

```python
reaped = m.reap_stale(older_than_ms=60 * 60 * 1000)
```

**Verification:**
```python
assert row['profile_id'] == 'default'
```

### Step 5: Assign row = _fetch_action(...)

```python
row = _fetch_action(memory_db, outcome_id)
```

**Verification:**
```python
assert row is not None
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
from superlocalmemory.learning.reward import EngagementRewardModel
now = {'ms': 1000000}
m = EngagementRewardModel(memory_db, clock_ms=lambda: now['ms'])
outcome_id = m.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
now['ms'] += 2 * 60 * 60 * 1000
reaped = m.reap_stale(older_than_ms=60 * 60 * 1000)
assert reaped == 1
row = _fetch_action(memory_db, outcome_id)
assert row is not None
assert row['settled'] == 1
assert row['profile_id'] == 'default'
```

## Next Steps


---

*Source: test_engagement_reward_model.py:408 | Complexity: Intermediate | Last updated: 2026-05-05*