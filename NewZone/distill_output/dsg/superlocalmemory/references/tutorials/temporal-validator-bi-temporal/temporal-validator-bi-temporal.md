# How To: Temporal Validator Bi Temporal

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Verify bi-temporal integrity: BOTH valid_until and system_expired_at
are set when a fact is invalidated.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `dataclasses`
- `hashlib`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Verify bi-temporal integrity: BOTH valid_until and system_expired_at\n        are set when a fact is invalidated.\n        '

```python
'Verify bi-temporal integrity: BOTH valid_until and system_expired_at\n        are set when a fact is invalidated.\n        '
```

**Verification:**
```python
assert len(ids_1) > 0
```

### Step 2: Assign engine = _create_v32_engine(...)

```python
engine = _create_v32_engine(tmp_path)
```

**Verification:**
```python
assert tv.get('valid_until') is None
```

### Step 3: Assign ids_1 = engine.store(...)

```python
ids_1 = engine.store('The production server runs Ubuntu 22.04 LTS with the latest security patches installed.', session_id='s1')
```

**Verification:**
```python
assert tv_after is not None
```

### Step 4: Assign tv = engine._db.get_temporal_validity(...)

```python
tv = engine._db.get_temporal_validity(ids_1[0])
```

**Verification:**
```python
assert tv_after.get('valid_until') is not None, 'valid_until not set after invalidation'
```

### Step 5: Call engine.close()

```python
engine.close()
```

**Verification:**
```python
assert tv_after.get('system_expired_at') is not None, 'system_expired_at not set after invalidation'
```

### Step 6: Call engine._temporal_validator.invalidate_fact()

```python
engine._temporal_validator.invalidate_fact(fact_id=ids_1[0], invalidated_by='test_fact', reason='Test invalidation')
```

**Verification:**
```python
assert not engine._temporal_validator.is_temporally_valid(ids_1[0], 'default')
```

### Step 7: Assign tv_after = engine._db.get_temporal_validity(...)

```python
tv_after = engine._db.get_temporal_validity(ids_1[0])
```

**Verification:**
```python
assert tv_double['invalidated_by'] == 'test_fact'
```

### Step 8: Call engine._temporal_validator.invalidate_fact()

```python
engine._temporal_validator.invalidate_fact(fact_id=ids_1[0], invalidated_by='test_fact_2', reason='Duplicate invalidation')
```

### Step 9: Assign tv_double = engine._db.get_temporal_validity(...)

```python
tv_double = engine._db.get_temporal_validity(ids_1[0])
```

**Verification:**
```python
assert tv_double['invalidated_by'] == 'test_fact'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Verify bi-temporal integrity: BOTH valid_until and system_expired_at\n        are set when a fact is invalidated.\n        '
engine = _create_v32_engine(tmp_path)
ids_1 = engine.store('The production server runs Ubuntu 22.04 LTS with the latest security patches installed.', session_id='s1')
assert len(ids_1) > 0
tv = engine._db.get_temporal_validity(ids_1[0])
if tv is not None:
    assert tv.get('valid_until') is None
if engine._temporal_validator:
    engine._temporal_validator.invalidate_fact(fact_id=ids_1[0], invalidated_by='test_fact', reason='Test invalidation')
    tv_after = engine._db.get_temporal_validity(ids_1[0])
    assert tv_after is not None
    assert tv_after.get('valid_until') is not None, 'valid_until not set after invalidation'
    assert tv_after.get('system_expired_at') is not None, 'system_expired_at not set after invalidation'
    assert not engine._temporal_validator.is_temporally_valid(ids_1[0], 'default')
    engine._temporal_validator.invalidate_fact(fact_id=ids_1[0], invalidated_by='test_fact_2', reason='Duplicate invalidation')
    tv_double = engine._db.get_temporal_validity(ids_1[0])
    assert tv_double['invalidated_by'] == 'test_fact'
engine.close()
```

## Next Steps


---

*Source: test_e2e_v32.py:563 | Complexity: Advanced | Last updated: 2026-05-05*