# How To: Filter No Retention Data Keeps Facts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Facts without retention data should be kept as-is (new memories).

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.retrieval.forgetting_filter`
- `unittest.mock`

**Setup Required:**
```python
# Fixtures: config
```

## Step-by-Step Guide

### Step 1: 'Facts without retention data should be kept as-is (new memories).'

```python
'Facts without retention data should be kept as-is (new memories).'
```

**Verification:**
```python
assert filtered['semantic'] == [('new_fact', 0.9)]
```

### Step 2: Assign db = _make_mock_db(...)

```python
db = _make_mock_db({})
```

### Step 3: Assign filt = ForgettingFilter(...)

```python
filt = ForgettingFilter(db, config)
```

### Step 4: Assign all_results = value

```python
all_results = {'semantic': [('new_fact', 0.9)]}
```

### Step 5: Assign filtered = filt.filter(...)

```python
filtered = filt.filter(all_results, 'default', None)
```

**Verification:**
```python
assert filtered['semantic'] == [('new_fact', 0.9)]
```


## Complete Example

```python
# Setup
# Fixtures: config

# Workflow
'Facts without retention data should be kept as-is (new memories).'
db = _make_mock_db({})
filt = ForgettingFilter(db, config)
all_results = {'semantic': [('new_fact', 0.9)]}
filtered = filt.filter(all_results, 'default', None)
assert filtered['semantic'] == [('new_fact', 0.9)]
```

## Next Steps


---

*Source: test_forgetting_filter.py:151 | Complexity: Intermediate | Last updated: 2026-05-05*