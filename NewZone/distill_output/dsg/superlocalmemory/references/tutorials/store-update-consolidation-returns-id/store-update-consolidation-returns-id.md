# How To: Store Update Consolidation Returns Id

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: When consolidator returns UPDATE, the updated fact ID is in result.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: engine_with_mock_deps
```

## Step-by-Step Guide

### Step 1: 'When consolidator returns UPDATE, the updated fact ID is in result.'

```python
'When consolidator returns UPDATE, the updated fact ID is in result.'
```

**Verification:**
```python
assert existing_id in ids
```

### Step 2: Assign original_ids = engine_with_mock_deps.store(...)

```python
original_ids = engine_with_mock_deps.store('Frank likes eating pepperoni pizza from the Italian restaurant downtown', session_id='s1')
```

### Step 3: Assign existing_id = value

```python
existing_id = original_ids[0]
```

### Step 4: Assign consolidator = value

```python
consolidator = engine_with_mock_deps._consolidator
```

### Step 5: Assign mock_action = _update_action(...)

```python
mock_action = _update_action(new_fact_id=existing_id)
```

### Step 6: Call pytest.skip()

```python
pytest.skip('No facts extracted from initial store')
```

### Step 7: Assign ids = engine_with_mock_deps.store(...)

```python
ids = engine_with_mock_deps.store('Frank really loves eating margherita pizza with fresh basil and mozzarella', session_id='s2')
```

**Verification:**
```python
assert existing_id in ids
```


## Complete Example

```python
# Setup
# Fixtures: engine_with_mock_deps

# Workflow
'When consolidator returns UPDATE, the updated fact ID is in result.'
original_ids = engine_with_mock_deps.store('Frank likes eating pepperoni pizza from the Italian restaurant downtown', session_id='s1')
if not original_ids:
    pytest.skip('No facts extracted from initial store')
existing_id = original_ids[0]
consolidator = engine_with_mock_deps._consolidator
mock_action = _update_action(new_fact_id=existing_id)
with patch.object(consolidator, 'consolidate', return_value=mock_action):
    ids = engine_with_mock_deps.store('Frank really loves eating margherita pizza with fresh basil and mozzarella', session_id='s2')
    assert existing_id in ids
```

## Next Steps


---

*Source: test_engine_store_path.py:177 | Complexity: Intermediate | Last updated: 2026-05-05*