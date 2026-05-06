# How To: Register Signal Accepts Within Grace Period Window

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Signals still land when now_ms == expires_at_ms (boundary inclusive).

Regression guard — the TTL check must be strict ``>``, not ``>=``;
the expires_at_ms tick itself is still within the window by design.

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

### Step 1: 'Signals still land when now_ms == expires_at_ms (boundary inclusive).\n\n    Regression guard — the TTL check must be strict ``>``, not ``>=``;\n    the expires_at_ms tick itself is still within the window by design.\n    '

```python
'Signals still land when now_ms == expires_at_ms (boundary inclusive).\n\n    Regression guard — the TTL check must be strict ``>``, not ``>=``;\n    the expires_at_ms tick itself is still within the window by design.\n    '
```

**Verification:**
```python
assert row_before is not None
```

### Step 2: Assign clock = value

```python
clock = {'ms': 5000}
```

**Verification:**
```python
assert ok is True
```

### Step 3: Assign model = EngagementRewardModel(...)

```python
model = EngagementRewardModel(memory_db, clock_ms=lambda: clock['ms'])
```

**Verification:**
```python
assert json.loads(row_after['signals_json']) == {'cite': True}
```

### Step 4: Assign outcome_id = model.record_recall(...)

```python
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
```

### Step 5: Assign row_before = _fetch_pending(...)

```python
row_before = _fetch_pending(memory_db, outcome_id)
```

**Verification:**
```python
assert row_before is not None
```

### Step 6: Assign unknown = int(...)

```python
clock['ms'] = int(row_before['expires_at_ms'])
```

### Step 7: Assign ok = model.register_signal(...)

```python
ok = model.register_signal(outcome_id=outcome_id, signal_name='cite', signal_value=True)
```

**Verification:**
```python
assert ok is True
```

### Step 8: Assign row_after = _fetch_pending(...)

```python
row_after = _fetch_pending(memory_db, outcome_id)
```

**Verification:**
```python
assert json.loads(row_after['signals_json']) == {'cite': True}
```


## Complete Example

```python
# Setup
# Fixtures: memory_db

# Workflow
'Signals still land when now_ms == expires_at_ms (boundary inclusive).\n\n    Regression guard — the TTL check must be strict ``>``, not ``>=``;\n    the expires_at_ms tick itself is still within the window by design.\n    '
from superlocalmemory.learning.reward import EngagementRewardModel
clock = {'ms': 5000}
model = EngagementRewardModel(memory_db, clock_ms=lambda: clock['ms'])
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
row_before = _fetch_pending(memory_db, outcome_id)
assert row_before is not None
clock['ms'] = int(row_before['expires_at_ms'])
ok = model.register_signal(outcome_id=outcome_id, signal_name='cite', signal_value=True)
assert ok is True
row_after = _fetch_pending(memory_db, outcome_id)
assert json.loads(row_after['signals_json']) == {'cite': True}
```

## Next Steps


---

*Source: test_engagement_reward_model.py:625 | Complexity: Advanced | Last updated: 2026-05-05*