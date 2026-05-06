# How To: Crash Recovery Reaper On Daemon Restart

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test crash recovery reaper on daemon restart

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
assert reaped == 3
```

### Step 2: Assign m1 = EngagementRewardModel(...)

```python
m1 = EngagementRewardModel(memory_db, clock_ms=lambda: now['ms'])
```

**Verification:**
```python
assert row is not None
```

### Step 3: Assign ids = value

```python
ids = [m1.record_recall(profile_id='default', session_id='crashed', recall_query_id=f'q{i}', fact_ids=['f'], query_text='x') for i in range(3)]
```

**Verification:**
```python
assert row['settled'] == 1
```

### Step 4: Assign m2 = EngagementRewardModel(...)

```python
m2 = EngagementRewardModel(memory_db, clock_ms=lambda: now['ms'])
```

### Step 5: Assign reaped = m2.reap_stale(...)

```python
reaped = m2.reap_stale(older_than_ms=60 * 60 * 1000)
```

**Verification:**
```python
assert reaped == 3
```

### Step 6: Assign row = _fetch_action(...)

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
m1 = EngagementRewardModel(memory_db, clock_ms=lambda: now['ms'])
ids = [m1.record_recall(profile_id='default', session_id='crashed', recall_query_id=f'q{i}', fact_ids=['f'], query_text='x') for i in range(3)]
del m1
now['ms'] += 2 * 60 * 60 * 1000
m2 = EngagementRewardModel(memory_db, clock_ms=lambda: now['ms'])
reaped = m2.reap_stale(older_than_ms=60 * 60 * 1000)
assert reaped == 3
for outcome_id in ids:
    row = _fetch_action(memory_db, outcome_id)
    assert row is not None
    assert row['settled'] == 1
```

## Next Steps


---

*Source: test_engagement_reward_model.py:518 | Complexity: Intermediate | Last updated: 2026-05-05*