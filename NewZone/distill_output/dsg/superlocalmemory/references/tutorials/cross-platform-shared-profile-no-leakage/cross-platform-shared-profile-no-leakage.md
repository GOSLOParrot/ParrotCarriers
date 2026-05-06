# How To: Cross Platform Shared Profile No Leakage

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Cross-platform sharing must not cross PROFILE boundaries.

Writes done under ``_SHARED_PROFILE`` from all 3 platforms must
remain invisible to ``_OTHER_PROFILE``'s training fetch. This is
the SEC-C-05 complement of (a): we asserted same-profile
aggregates; here we assert different-profile isolation holds even
when the same reward model + learning DB are in play.

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

### Step 1: "Cross-platform sharing must not cross PROFILE boundaries.\n\n    Writes done under ``_SHARED_PROFILE`` from all 3 platforms must\n    remain invisible to ``_OTHER_PROFILE``'s training fetch. This is\n    the SEC-C-05 complement of (a): we asserted same-profile\n    aggregates; here we assert different-profile isolation holds even\n    when the same reward model + learning DB are in play.\n    "

```python
"Cross-platform sharing must not cross PROFILE boundaries.\n\n    Writes done under ``_SHARED_PROFILE`` from all 3 platforms must\n    remain invisible to ``_OTHER_PROFILE``'s training fetch. This is\n    the SEC-C-05 complement of (a): we asserted same-profile\n    aggregates; here we assert different-profile isolation holds even\n    when the same reward model + learning DB are in play.\n    "
```

**Verification:**
```python
assert len(shared_rows) == 3
```

### Step 2: Call _simulate_platform_outcome()

```python
_simulate_platform_outcome(platform='claude_code', profile_id=_OTHER_PROFILE, reward_model=reward_model, learning_db=learning_db, memory_db_path=memory_db_path, fact_ids=['other-fact'], query_text='other profile probe', cited=True)
```

**Verification:**
```python
assert 'other-fact' not in shared_fact_ids
```

### Step 3: Call _mirror_action_outcomes_into_learning_db()

```python
_mirror_action_outcomes_into_learning_db(memory_db_path, learning_db)
```

**Verification:**
```python
assert len(other_rows) == 1
```

### Step 4: Assign shared_rows = learning_db.fetch_training_examples(...)

```python
shared_rows = learning_db.fetch_training_examples(profile_id=_SHARED_PROFILE, limit=100, min_outcome_age_sec=0)
```

**Verification:**
```python
assert other_rows[0]['fact_id'] == 'other-fact'
```

### Step 5: Assign other_rows = learning_db.fetch_training_examples(...)

```python
other_rows = learning_db.fetch_training_examples(profile_id=_OTHER_PROFILE, limit=100, min_outcome_age_sec=0)
```

**Verification:**
```python
assert shared_count == 3
```

### Step 6: Assign shared_fact_ids = value

```python
shared_fact_ids = {r['fact_id'] for r in shared_rows}
```

**Verification:**
```python
assert other_count == 1
```

### Step 7: Call _simulate_platform_outcome()

```python
_simulate_platform_outcome(platform=p, profile_id=_SHARED_PROFILE, reward_model=reward_model, learning_db=learning_db, memory_db_path=memory_db_path, fact_ids=[f'shared-{p}'], query_text=f'{p} probe shared', cited=True)
```

### Step 8: Assign shared_count = value

```python
shared_count = conn.execute('SELECT COUNT(*) FROM action_outcomes WHERE profile_id = ?', (_SHARED_PROFILE,)).fetchone()[0]
```

### Step 9: Assign other_count = value

```python
other_count = conn.execute('SELECT COUNT(*) FROM action_outcomes WHERE profile_id = ?', (_OTHER_PROFILE,)).fetchone()[0]
```


## Complete Example

```python
# Setup
# Fixtures: memory_db_path, reward_model, learning_db

# Workflow
"Cross-platform sharing must not cross PROFILE boundaries.\n\n    Writes done under ``_SHARED_PROFILE`` from all 3 platforms must\n    remain invisible to ``_OTHER_PROFILE``'s training fetch. This is\n    the SEC-C-05 complement of (a): we asserted same-profile\n    aggregates; here we assert different-profile isolation holds even\n    when the same reward model + learning DB are in play.\n    "
for p in _PLATFORMS:
    _simulate_platform_outcome(platform=p, profile_id=_SHARED_PROFILE, reward_model=reward_model, learning_db=learning_db, memory_db_path=memory_db_path, fact_ids=[f'shared-{p}'], query_text=f'{p} probe shared', cited=True)
_simulate_platform_outcome(platform='claude_code', profile_id=_OTHER_PROFILE, reward_model=reward_model, learning_db=learning_db, memory_db_path=memory_db_path, fact_ids=['other-fact'], query_text='other profile probe', cited=True)
_mirror_action_outcomes_into_learning_db(memory_db_path, learning_db)
shared_rows = learning_db.fetch_training_examples(profile_id=_SHARED_PROFILE, limit=100, min_outcome_age_sec=0)
other_rows = learning_db.fetch_training_examples(profile_id=_OTHER_PROFILE, limit=100, min_outcome_age_sec=0)
assert len(shared_rows) == 3
shared_fact_ids = {r['fact_id'] for r in shared_rows}
assert 'other-fact' not in shared_fact_ids
assert len(other_rows) == 1
assert other_rows[0]['fact_id'] == 'other-fact'
with sqlite3.connect(memory_db_path) as conn:
    shared_count = conn.execute('SELECT COUNT(*) FROM action_outcomes WHERE profile_id = ?', (_SHARED_PROFILE,)).fetchone()[0]
    other_count = conn.execute('SELECT COUNT(*) FROM action_outcomes WHERE profile_id = ?', (_OTHER_PROFILE,)).fetchone()[0]
assert shared_count == 3
assert other_count == 1
```

## Next Steps


---

*Source: test_cross_platform_learning.py:628 | Complexity: Advanced | Last updated: 2026-05-05*