# How To: Filter Removes Archived

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Archive-zone and forgotten-zone facts should be excluded from results.

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

### Step 1: 'Archive-zone and forgotten-zone facts should be excluded from results.'

```python
'Archive-zone and forgotten-zone facts should be excluded from results.'
```

**Verification:**
```python
assert 'fact_active' in fact_ids_in_result
```

### Step 2: Assign retention_data = value

```python
retention_data = {'fact_active': {'fact_id': 'fact_active', 'retention_score': 0.9, 'lifecycle_zone': 'active'}, 'fact_archive': {'fact_id': 'fact_archive', 'retention_score': 0.1, 'lifecycle_zone': 'archive'}, 'fact_forgotten': {'fact_id': 'fact_forgotten', 'retention_score': 0.01, 'lifecycle_zone': 'forgotten'}}
```

**Verification:**
```python
assert 'fact_archive' not in fact_ids_in_result
```

### Step 3: Assign db = _make_mock_db(...)

```python
db = _make_mock_db(retention_data)
```

**Verification:**
```python
assert 'fact_forgotten' not in fact_ids_in_result
```

### Step 4: Assign filt = ForgettingFilter(...)

```python
filt = ForgettingFilter(db, config)
```

### Step 5: Assign all_results = value

```python
all_results = {'semantic': [('fact_active', 0.8), ('fact_archive', 0.7), ('fact_forgotten', 0.6)]}
```

### Step 6: Assign filtered = filt.filter(...)

```python
filtered = filt.filter(all_results, 'default', None)
```

### Step 7: Assign fact_ids_in_result = value

```python
fact_ids_in_result = [fid for fid, _ in filtered['semantic']]
```

**Verification:**
```python
assert 'fact_active' in fact_ids_in_result
```


## Complete Example

```python
# Setup
# Fixtures: config

# Workflow
'Archive-zone and forgotten-zone facts should be excluded from results.'
retention_data = {'fact_active': {'fact_id': 'fact_active', 'retention_score': 0.9, 'lifecycle_zone': 'active'}, 'fact_archive': {'fact_id': 'fact_archive', 'retention_score': 0.1, 'lifecycle_zone': 'archive'}, 'fact_forgotten': {'fact_id': 'fact_forgotten', 'retention_score': 0.01, 'lifecycle_zone': 'forgotten'}}
db = _make_mock_db(retention_data)
filt = ForgettingFilter(db, config)
all_results = {'semantic': [('fact_active', 0.8), ('fact_archive', 0.7), ('fact_forgotten', 0.6)]}
filtered = filt.filter(all_results, 'default', None)
fact_ids_in_result = [fid for fid, _ in filtered['semantic']]
assert 'fact_active' in fact_ids_in_result
assert 'fact_archive' not in fact_ids_in_result
assert 'fact_forgotten' not in fact_ids_in_result
```

## Next Steps


---

*Source: test_forgetting_filter.py:51 | Complexity: Intermediate | Last updated: 2026-05-05*