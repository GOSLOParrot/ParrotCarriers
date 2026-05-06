# How To: Scheduler Triggers On Interval

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Scheduler only runs when time_since_last_run >= interval.
Calling before interval returns early with no-op stats.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `time`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.learning.forgetting_scheduler`
- `superlocalmemory.math.ebbinghaus`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage`
- `superlocalmemory.storage.schema_v32`
- `superlocalmemory.storage`
- `superlocalmemory.storage.schema_v32`

**Setup Required:**
```python
# Fixtures: db_with_facts, ebbinghaus, config
```

## Step-by-Step Guide

### Step 1: 'Scheduler only runs when time_since_last_run >= interval.\n    Calling before interval returns early with no-op stats.'

```python
'Scheduler only runs when time_since_last_run >= interval.\n    Calling before interval returns early with no-op stats.'
```

**Verification:**
```python
assert stats1['total'] == 10
```

### Step 2: Assign scheduler = ForgettingScheduler(...)

```python
scheduler = ForgettingScheduler(db_with_facts, ebbinghaus, config)
```

**Verification:**
```python
assert stats2.get('skipped', False) is True, 'Second immediate run should be skipped (within interval)'
```

### Step 3: Assign stats1 = scheduler.run_decay_cycle(...)

```python
stats1 = scheduler.run_decay_cycle('test_profile')
```

**Verification:**
```python
assert stats3['total'] == 10, 'Force run should execute regardless of interval'
```

### Step 4: Assign stats2 = scheduler.run_decay_cycle(...)

```python
stats2 = scheduler.run_decay_cycle('test_profile')
```

**Verification:**
```python
assert stats2.get('skipped', False) is True, 'Second immediate run should be skipped (within interval)'
```

### Step 5: Assign stats3 = scheduler.run_decay_cycle(...)

```python
stats3 = scheduler.run_decay_cycle('test_profile', force=True)
```

**Verification:**
```python
assert stats3['total'] == 10, 'Force run should execute regardless of interval'
```


## Complete Example

```python
# Setup
# Fixtures: db_with_facts, ebbinghaus, config

# Workflow
'Scheduler only runs when time_since_last_run >= interval.\n    Calling before interval returns early with no-op stats.'
scheduler = ForgettingScheduler(db_with_facts, ebbinghaus, config)
stats1 = scheduler.run_decay_cycle('test_profile')
assert stats1['total'] == 10
stats2 = scheduler.run_decay_cycle('test_profile')
assert stats2.get('skipped', False) is True, 'Second immediate run should be skipped (within interval)'
stats3 = scheduler.run_decay_cycle('test_profile', force=True)
assert stats3['total'] == 10, 'Force run should execute regardless of interval'
```

## Next Steps


---

*Source: test_forgetting_scheduler.py:253 | Complexity: Intermediate | Last updated: 2026-05-05*