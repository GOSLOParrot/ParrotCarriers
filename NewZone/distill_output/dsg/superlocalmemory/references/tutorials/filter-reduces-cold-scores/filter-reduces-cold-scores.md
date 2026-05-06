# How To: Filter Reduces Cold Scores

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Cold-zone facts should have score * 0.3.

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

### Step 1: 'Cold-zone facts should have score * 0.3.'

```python
'Cold-zone facts should have score * 0.3.'
```

**Verification:**
```python
assert len(filtered['semantic']) == 1
```

### Step 2: Assign retention_data = value

```python
retention_data = {'fact_cold': {'fact_id': 'fact_cold', 'retention_score': 0.4, 'lifecycle_zone': 'cold'}}
```

**Verification:**
```python
assert fid == 'fact_cold'
```

### Step 3: Assign db = _make_mock_db(...)

```python
db = _make_mock_db(retention_data)
```

**Verification:**
```python
assert score == pytest.approx(0.3, abs=0.01)
```

### Step 4: Assign filt = ForgettingFilter(...)

```python
filt = ForgettingFilter(db, config)
```

### Step 5: Assign all_results = value

```python
all_results = {'semantic': [('fact_cold', 1.0)]}
```

### Step 6: Assign filtered = filt.filter(...)

```python
filtered = filt.filter(all_results, 'default', None)
```

**Verification:**
```python
assert len(filtered['semantic']) == 1
```

### Step 7: Assign unknown = value

```python
fid, score = filtered['semantic'][0]
```

**Verification:**
```python
assert fid == 'fact_cold'
```


## Complete Example

```python
# Setup
# Fixtures: config

# Workflow
'Cold-zone facts should have score * 0.3.'
retention_data = {'fact_cold': {'fact_id': 'fact_cold', 'retention_score': 0.4, 'lifecycle_zone': 'cold'}}
db = _make_mock_db(retention_data)
filt = ForgettingFilter(db, config)
all_results = {'semantic': [('fact_cold', 1.0)]}
filtered = filt.filter(all_results, 'default', None)
assert len(filtered['semantic']) == 1
fid, score = filtered['semantic'][0]
assert fid == 'fact_cold'
assert score == pytest.approx(0.3, abs=0.01)
```

## Next Steps


---

*Source: test_forgetting_filter.py:75 | Complexity: Intermediate | Last updated: 2026-05-05*