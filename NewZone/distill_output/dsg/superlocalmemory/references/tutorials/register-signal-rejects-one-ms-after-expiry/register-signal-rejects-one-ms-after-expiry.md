# How To: Register Signal Rejects One Ms After Expiry

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Exactly one millisecond past expires_at_ms must reject.

Tightens the boundary on the H-05 fix.

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

### Step 1: 'Exactly one millisecond past expires_at_ms must reject.\n\n    Tightens the boundary on the H-05 fix.\n    '

```python
'Exactly one millisecond past expires_at_ms must reject.\n\n    Tightens the boundary on the H-05 fix.\n    '
```

**Verification:**
```python
assert ok is False
```

### Step 2: Assign clock = value

```python
clock = {'ms': 7000}
```

### Step 3: Assign model = EngagementRewardModel(...)

```python
model = EngagementRewardModel(memory_db, clock_ms=lambda: clock['ms'])
```

### Step 4: Assign outcome_id = model.record_recall(...)

```python
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
```

### Step 5: Assign row = _fetch_pending(...)

```python
row = _fetch_pending(memory_db, outcome_id)
```

### Step 6: Assign unknown = value

```python
clock['ms'] = int(row['expires_at_ms']) + 1
```

### Step 7: Assign ok = model.register_signal(...)

```python
ok = model.register_signal(outcome_id=outcome_id, signal_name='requery', signal_value=True)
```

**Verification:**
```python
assert ok is False
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
'Exactly one millisecond past expires_at_ms must reject.\n\n    Tightens the boundary on the H-05 fix.\n    '
from superlocalmemory.learning.reward import EngagementRewardModel
clock = {'ms': 7000}
model = EngagementRewardModel(memory_db, clock_ms=lambda: clock['ms'])
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
row = _fetch_pending(memory_db, outcome_id)
clock['ms'] = int(row['expires_at_ms']) + 1
ok = model.register_signal(outcome_id=outcome_id, signal_name='requery', signal_value=True)
assert ok is False
```

## Next Steps


---

*Source: test_engagement_reward_model.py:656 | Complexity: Intermediate | Last updated: 2026-05-05*