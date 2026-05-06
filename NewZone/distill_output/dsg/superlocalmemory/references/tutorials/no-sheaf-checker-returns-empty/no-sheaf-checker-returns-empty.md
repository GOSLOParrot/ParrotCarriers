# How To: No Sheaf Checker Returns Empty

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Graceful degradation when sheaf_checker is None.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `time`
- `datetime`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.temporal_validator`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: 'Graceful degradation when sheaf_checker is None.'

```python
'Graceful degradation when sheaf_checker is None.'
```

**Verification:**
```python
assert result == []
```

### Step 2: Assign config = TemporalValidatorConfig(...)

```python
config = TemporalValidatorConfig(enabled=True, mode='a')
```

### Step 3: Assign tv = TemporalValidator(...)

```python
tv = TemporalValidator(db=db, sheaf_checker=None, config=config)
```

### Step 4: Assign fact = AtomicFact(...)

```python
fact = AtomicFact(profile_id='default', memory_id='m1', content='test')
```

### Step 5: Assign result = tv.detect_contradiction(...)

```python
result = tv.detect_contradiction(fact, 'default')
```

**Verification:**
```python
assert result == []
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
'Graceful degradation when sheaf_checker is None.'
config = TemporalValidatorConfig(enabled=True, mode='a')
tv = TemporalValidator(db=db, sheaf_checker=None, config=config)
fact = AtomicFact(profile_id='default', memory_id='m1', content='test')
result = tv.detect_contradiction(fact, 'default')
assert result == []
```

## Next Steps


---

*Source: test_temporal_validator.py:300 | Complexity: Intermediate | Last updated: 2026-05-05*