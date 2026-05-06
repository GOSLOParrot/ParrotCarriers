# How To: Register Signal Rejects After Expiry

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Stage 8 H-05: signals MUST be rejected once past expires_at_ms.

Seed a pending row whose grace period has already elapsed; call
register_signal; expect False and no mutation to signals_json.

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

### Step 1: 'Stage 8 H-05: signals MUST be rejected once past expires_at_ms.\n\n    Seed a pending row whose grace period has already elapsed; call\n    register_signal; expect False and no mutation to signals_json.\n    '

```python
'Stage 8 H-05: signals MUST be rejected once past expires_at_ms.\n\n    Seed a pending row whose grace period has already elapsed; call\n    register_signal; expect False and no mutation to signals_json.\n    '
```

**Verification:**
```python
assert ok is False
```

### Step 2: Assign clock = value

```python
clock = {'ms': 1000}
```

**Verification:**
```python
assert row is not None
```

### Step 3: Assign model = EngagementRewardModel(...)

```python
model = EngagementRewardModel(memory_db, clock_ms=lambda: clock['ms'])
```

**Verification:**
```python
assert json.loads(row['signals_json']) == {}
```

### Step 4: Assign outcome_id = model.record_recall(...)

```python
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
```

### Step 5: Assign unknown = value

```python
clock['ms'] = 1000 + EngagementRewardModel.GRACE_PERIOD_MS + 1
```

### Step 6: Assign ok = model.register_signal(...)

```python
ok = model.register_signal(outcome_id=outcome_id, signal_name='cite', signal_value=True)
```

**Verification:**
```python
assert ok is False
```

### Step 7: Assign row = _fetch_pending(...)

```python
row = _fetch_pending(memory_db, outcome_id)
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
'Stage 8 H-05: signals MUST be rejected once past expires_at_ms.\n\n    Seed a pending row whose grace period has already elapsed; call\n    register_signal; expect False and no mutation to signals_json.\n    '
from superlocalmemory.learning.reward import EngagementRewardModel
clock = {'ms': 1000}
model = EngagementRewardModel(memory_db, clock_ms=lambda: clock['ms'])
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
clock['ms'] = 1000 + EngagementRewardModel.GRACE_PERIOD_MS + 1
ok = model.register_signal(outcome_id=outcome_id, signal_name='cite', signal_value=True)
assert ok is False
row = _fetch_pending(memory_db, outcome_id)
assert row is not None
assert json.loads(row['signals_json']) == {}
```

## Next Steps


---

*Source: test_engagement_reward_model.py:588 | Complexity: Intermediate | Last updated: 2026-05-05*