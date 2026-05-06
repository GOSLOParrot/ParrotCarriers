# How To: Finalize Outcome Feeds Shadow Router

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, mock, workflow, integration

## Overview

Workflow: C1: finalize_outcome must call feed_recall_settled with reward
as the NDCG@10 proxy. Verified by mocking feed_recall_settled and
checking it was invoked with the right kwargs.

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

### Step 1: 'C1: finalize_outcome must call feed_recall_settled with reward\n    as the NDCG@10 proxy. Verified by mocking feed_recall_settled and\n    checking it was invoked with the right kwargs.'

```python
'C1: finalize_outcome must call feed_recall_settled with reward\n    as the NDCG@10 proxy. Verified by mocking feed_recall_settled and\n    checking it was invoked with the right kwargs.'
```

**Verification:**
```python
assert 0.0 <= reward <= 1.0
```

### Step 2: Assign memory_db = value

```python
memory_db = tmp_path / 'memory.db'
```

**Verification:**
```python
assert call_kwargs['profile_id'] == 'default'
```

### Step 3: Assign outcome_id = _seed_pending_row(...)

```python
outcome_id = _seed_pending_row(memory_db, recall_query_id='q-123')
```

**Verification:**
```python
assert call_kwargs['query_id'] == 'q-123'
```

### Step 4: Assign model = EngagementRewardModel(...)

```python
model = EngagementRewardModel(memory_db)
```

**Verification:**
```python
assert call_kwargs['ndcg_at_10'] == pytest.approx(reward)
```

### Step 5: Call model.close()

```python
model.close()
```

**Verification:**
```python
assert call_kwargs['memory_db'].endswith('memory.db')
```

### Step 6: Call mock_feed.assert_called_once()

```python
mock_feed.assert_called_once()
```

**Verification:**
```python
assert call_kwargs['learning_db'].endswith('learning.db')
```

### Step 7: Assign call_kwargs = value

```python
call_kwargs = mock_feed.call_args.kwargs
```

**Verification:**
```python
assert call_kwargs['profile_id'] == 'default'
```

### Step 8: Assign reward = model.finalize_outcome(...)

```python
reward = model.finalize_outcome(outcome_id=outcome_id)
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, reset_router

# Workflow
'C1: finalize_outcome must call feed_recall_settled with reward\n    as the NDCG@10 proxy. Verified by mocking feed_recall_settled and\n    checking it was invoked with the right kwargs.'
memory_db = tmp_path / 'memory.db'
outcome_id = _seed_pending_row(memory_db, recall_query_id='q-123')
model = EngagementRewardModel(memory_db)
with mock.patch('superlocalmemory.core.recall_pipeline.feed_recall_settled') as mock_feed:
    reward = model.finalize_outcome(outcome_id=outcome_id)
model.close()
assert 0.0 <= reward <= 1.0
mock_feed.assert_called_once()
call_kwargs = mock_feed.call_args.kwargs
assert call_kwargs['profile_id'] == 'default'
assert call_kwargs['query_id'] == 'q-123'
assert call_kwargs['ndcg_at_10'] == pytest.approx(reward)
assert call_kwargs['memory_db'].endswith('memory.db')
assert call_kwargs['learning_db'].endswith('learning.db')
```

## Next Steps


---

*Source: test_s9_w1_lld10_wiring.py:98 | Complexity: Advanced | Last updated: 2026-05-05*