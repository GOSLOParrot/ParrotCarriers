# How To: Recall Increments Access Count

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: recall() calls _db.update_fact to increment access_count.

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

### Step 1: 'recall() calls _db.update_fact to increment access_count.'

```python
'recall() calls _db.update_fact to increment access_count.'
```

**Verification:**
```python
assert update_dict['access_count'] == 4
```

### Step 2: Assign fact = _make_fact(...)

```python
fact = _make_fact('access-f1', access_count=3)
```

### Step 3: Assign mock_response = _make_recall_response(...)

```python
mock_response = _make_recall_response(facts=[fact])
```

### Step 4: Assign re = value

```python
re = engine_with_mock_deps._retrieval_engine
```

### Step 5: Assign db = value

```python
db = engine_with_mock_deps._db
```

### Step 6: Call engine_with_mock_deps.recall()

```python
engine_with_mock_deps.recall('access query')
```

### Step 7: Call db_spy.assert_called_once()

```python
db_spy.assert_called_once()
```

### Step 8: Assign update_dict = value

```python
update_dict = db_spy.call_args[0][1]
```

**Verification:**
```python
assert update_dict['access_count'] == 4
```


## Complete Example

```python
# Setup
# Fixtures: engine_with_mock_deps

# Workflow
'recall() calls _db.update_fact to increment access_count.'
fact = _make_fact('access-f1', access_count=3)
mock_response = _make_recall_response(facts=[fact])
re = engine_with_mock_deps._retrieval_engine
db = engine_with_mock_deps._db
with patch.object(re, 'recall', return_value=mock_response):
    with patch.object(db, 'update_fact') as db_spy:
        engine_with_mock_deps.recall('access query')
        db_spy.assert_called_once()
        update_dict = db_spy.call_args[0][1]
        assert update_dict['access_count'] == 4
```

## Next Steps


---

*Source: test_engine_recall_path.py:173 | Complexity: Advanced | Last updated: 2026-05-05*