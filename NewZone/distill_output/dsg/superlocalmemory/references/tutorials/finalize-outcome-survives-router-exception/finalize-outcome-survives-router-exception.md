# How To: Finalize Outcome Survives Router Exception

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: unittest, mock, workflow, integration

## Overview

Workflow: C1 fail-soft: a raised exception inside feed_recall_settled must
NOT propagate — the reward return contract is more important than
the A/B loop signal.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `sqlite3`
- `uuid`
- `pathlib`
- `unittest`
- `pytest`
- `superlocalmemory.core`
- `superlocalmemory.learning.reward`
- `json`
- `superlocalmemory.learning`

**Setup Required:**
```python
# Fixtures: tmp_path, reset_router
```

## Step-by-Step Guide

### Step 1: 'C1 fail-soft: a raised exception inside feed_recall_settled must\n    NOT propagate — the reward return contract is more important than\n    the A/B loop signal.'

```python
'C1 fail-soft: a raised exception inside feed_recall_settled must\n    NOT propagate — the reward return contract is more important than\n    the A/B loop signal.'
```

**Verification:**
```python
assert 0.0 <= reward <= 1.0
```

### Step 2: Assign memory_db = value

```python
memory_db = tmp_path / 'memory.db'
```

### Step 3: Assign outcome_id = _seed_pending_row(...)

```python
outcome_id = _seed_pending_row(memory_db)
```

### Step 4: Assign model = EngagementRewardModel(...)

```python
model = EngagementRewardModel(memory_db)
```

### Step 5: Call model.close()

```python
model.close()
```

**Verification:**
```python
assert 0.0 <= reward <= 1.0
```

### Step 6: Assign reward = model.finalize_outcome(...)

```python
reward = model.finalize_outcome(outcome_id=outcome_id)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, reset_router

# Workflow
'C1 fail-soft: a raised exception inside feed_recall_settled must\n    NOT propagate — the reward return contract is more important than\n    the A/B loop signal.'
memory_db = tmp_path / 'memory.db'
outcome_id = _seed_pending_row(memory_db)
model = EngagementRewardModel(memory_db)
with mock.patch('superlocalmemory.core.recall_pipeline.feed_recall_settled', side_effect=RuntimeError('simulated router crash')):
    reward = model.finalize_outcome(outcome_id=outcome_id)
model.close()
assert 0.0 <= reward <= 1.0
```

## Next Steps


---

*Source: test_s9_w1_lld10_wiring.py:126 | Complexity: Advanced | Last updated: 2026-05-05*