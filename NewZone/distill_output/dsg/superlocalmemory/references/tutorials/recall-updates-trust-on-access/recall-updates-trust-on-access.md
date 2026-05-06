# How To: Recall Updates Trust On Access

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: recall() calls trust_scorer.update_on_access for each result.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: engine_with_mock_deps
```

## Step-by-Step Guide

### Step 1: 'recall() calls trust_scorer.update_on_access for each result.'

```python
'recall() calls trust_scorer.update_on_access for each result.'
```

### Step 2: Assign fact = _make_fact(...)

```python
fact = _make_fact('trust-f1')
```

### Step 3: Assign mock_response = _make_recall_response(...)

```python
mock_response = _make_recall_response(facts=[fact])
```

### Step 4: Assign re = value

```python
re = engine_with_mock_deps._retrieval_engine
```

### Step 5: Assign ts = value

```python
ts = engine_with_mock_deps._trust_scorer
```

### Step 6: Call engine_with_mock_deps.recall()

```python
engine_with_mock_deps.recall('trust query')
```

### Step 7: Call trust_spy.assert_called_once_with()

```python
trust_spy.assert_called_once_with('fact', 'trust-f1', engine_with_mock_deps._profile_id)
```


## Complete Example

```python
# Setup
# Fixtures: engine_with_mock_deps

# Workflow
'recall() calls trust_scorer.update_on_access for each result.'
fact = _make_fact('trust-f1')
mock_response = _make_recall_response(facts=[fact])
re = engine_with_mock_deps._retrieval_engine
ts = engine_with_mock_deps._trust_scorer
with patch.object(re, 'recall', return_value=mock_response):
    with patch.object(ts, 'update_on_access') as trust_spy:
        engine_with_mock_deps.recall('trust query')
        trust_spy.assert_called_once_with('fact', 'trust-f1', engine_with_mock_deps._profile_id)
```

## Next Steps


---

*Source: test_engine_recall_path.py:157 | Complexity: Intermediate | Last updated: 2026-05-05*