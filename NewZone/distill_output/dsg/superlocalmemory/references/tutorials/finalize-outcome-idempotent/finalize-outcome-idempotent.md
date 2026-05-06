# How To: Finalize Outcome Idempotent

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Second finalize_outcome call must not corrupt the settled row.

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
# Fixtures: model, memory_db
```

## Step-by-Step Guide

### Step 1: 'Second finalize_outcome call must not corrupt the settled row.'

```python
'Second finalize_outcome call must not corrupt the settled row.'
```

**Verification:**
```python
assert r1 == pytest.approx(0.75)
```

### Step 2: Assign outcome_id = model.record_recall(...)

```python
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
```

**Verification:**
```python
assert r2 == 0.5
```

### Step 3: Call model.register_signal()

```python
model.register_signal(outcome_id=outcome_id, signal_name='edit', signal_value=True)
```

**Verification:**
```python
assert row['reward'] == pytest.approx(0.75)
```

### Step 4: Assign r1 = model.finalize_outcome(...)

```python
r1 = model.finalize_outcome(outcome_id=outcome_id)
```

### Step 5: Assign r2 = model.finalize_outcome(...)

```python
r2 = model.finalize_outcome(outcome_id=outcome_id)
```

**Verification:**
```python
assert r1 == pytest.approx(0.75)
```

### Step 6: Assign row = _fetch_action(...)

```python
row = _fetch_action(memory_db, outcome_id)
```

**Verification:**
```python
assert row['reward'] == pytest.approx(0.75)
```


## Complete Example

```python
# Setup
# Fixtures: model, memory_db

# Workflow
'Second finalize_outcome call must not corrupt the settled row.'
outcome_id = model.record_recall(profile_id='default', session_id='s', recall_query_id='q', fact_ids=['f'], query_text='x')
model.register_signal(outcome_id=outcome_id, signal_name='edit', signal_value=True)
r1 = model.finalize_outcome(outcome_id=outcome_id)
r2 = model.finalize_outcome(outcome_id=outcome_id)
assert r1 == pytest.approx(0.75)
assert r2 == 0.5
row = _fetch_action(memory_db, outcome_id)
assert row['reward'] == pytest.approx(0.75)
```

## Next Steps


---

*Source: test_engagement_reward_model.py:553 | Complexity: Intermediate | Last updated: 2026-05-05*