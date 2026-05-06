# How To: Three Platforms Write To Same Profile Id

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: SEC-C-05 cross-profile guard must hold across every platform.

Each platform writes an outcome under ``_SHARED_PROFILE`` via the
canonical ``EngagementRewardModel.finalize_outcome`` path. The
resulting ``action_outcomes`` table must have EXACTLY 3 rows, all
carrying ``profile_id == _SHARED_PROFILE``, and zero rows with a
NULL / empty / mismatched profile_id.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `uuid`
- `pathlib`
- `typing`
- `pytest`
- `superlocalmemory.learning.database`
- `superlocalmemory.learning.reward`
- `json`
- `json`

**Setup Required:**
```python
# Fixtures: memory_db_path, reward_model, learning_db
```

## Step-by-Step Guide

### Step 1: 'SEC-C-05 cross-profile guard must hold across every platform.\n\n    Each platform writes an outcome under ``_SHARED_PROFILE`` via the\n    canonical ``EngagementRewardModel.finalize_outcome`` path. The\n    resulting ``action_outcomes`` table must have EXACTLY 3 rows, all\n    carrying ``profile_id == _SHARED_PROFILE``, and zero rows with a\n    NULL / empty / mismatched profile_id.\n    '

```python
'SEC-C-05 cross-profile guard must hold across every platform.\n\n    Each platform writes an outcome under ``_SHARED_PROFILE`` via the\n    canonical ``EngagementRewardModel.finalize_outcome`` path. The\n    resulting ``action_outcomes`` table must have EXACTLY 3 rows, all\n    carrying ``profile_id == _SHARED_PROFILE``, and zero rows with a\n    NULL / empty / mismatched profile_id.\n    '
```

**Verification:**
```python
assert len(results) == 3
```

### Step 2: Assign results = value

```python
results = [_simulate_platform_outcome(platform=p, profile_id=_SHARED_PROFILE, reward_model=reward_model, learning_db=learning_db, memory_db_path=memory_db_path, fact_ids=[f'fact-{p}-1', f'fact-{p}-2'], query_text=f'query from {p}', cited=True) for p in _PLATFORMS]
```

**Verification:**
```python
assert len(rows) == 3, 'exactly one action_outcomes row per platform'
```

### Step 3: Assign rows = conn.execute.fetchall(...)

```python
rows = conn.execute('SELECT profile_id, outcome_id FROM action_outcomes').fetchall()
```

**Verification:**
```python
assert profile_ids == {_SHARED_PROFILE}, f'SEC-C-05 breach: expected only {_SHARED_PROFILE!r}, got {profile_ids!r}'
```

### Step 4: Assign profile_ids = value

```python
profile_ids = {r[0] for r in rows}
```

**Verification:**
```python
assert len(outcome_ids) == 3
```

### Step 5: Assign outcome_ids = value

```python
outcome_ids = {r[1] for r in rows}
```

**Verification:**
```python
assert null_count == 0
```

### Step 6: Assign null_count = value

```python
null_count = conn.execute("SELECT COUNT(*) FROM action_outcomes WHERE profile_id IS NULL OR profile_id = ''").fetchone()[0]
```

**Verification:**
```python
assert null_count == 0
```


## Complete Example

```python
# Setup
# Fixtures: memory_db_path, reward_model, learning_db

# Workflow
'SEC-C-05 cross-profile guard must hold across every platform.\n\n    Each platform writes an outcome under ``_SHARED_PROFILE`` via the\n    canonical ``EngagementRewardModel.finalize_outcome`` path. The\n    resulting ``action_outcomes`` table must have EXACTLY 3 rows, all\n    carrying ``profile_id == _SHARED_PROFILE``, and zero rows with a\n    NULL / empty / mismatched profile_id.\n    '
results = [_simulate_platform_outcome(platform=p, profile_id=_SHARED_PROFILE, reward_model=reward_model, learning_db=learning_db, memory_db_path=memory_db_path, fact_ids=[f'fact-{p}-1', f'fact-{p}-2'], query_text=f'query from {p}', cited=True) for p in _PLATFORMS]
assert len(results) == 3
with sqlite3.connect(memory_db_path) as conn:
    rows = conn.execute('SELECT profile_id, outcome_id FROM action_outcomes').fetchall()
    assert len(rows) == 3, 'exactly one action_outcomes row per platform'
    profile_ids = {r[0] for r in rows}
    assert profile_ids == {_SHARED_PROFILE}, f'SEC-C-05 breach: expected only {_SHARED_PROFILE!r}, got {profile_ids!r}'
    outcome_ids = {r[1] for r in rows}
    assert len(outcome_ids) == 3
    null_count = conn.execute("SELECT COUNT(*) FROM action_outcomes WHERE profile_id IS NULL OR profile_id = ''").fetchone()[0]
    assert null_count == 0
```

## Next Steps


---

*Source: test_cross_platform_learning.py:347 | Complexity: Intermediate | Last updated: 2026-05-05*