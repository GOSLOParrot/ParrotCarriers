# How To: Expired Facts Excluded From Default Retrieval

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: temporal_validity_filter removes expired facts from results.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.encoding.temporal_validator`
- `superlocalmemory.retrieval.channel_registry`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db, _seed_facts
```

## Step-by-Step Guide

### Step 1: 'temporal_validity_filter removes expired facts from results.'

```python
'temporal_validity_filter removes expired facts from results.'
```

**Verification:**
```python
assert fid0 in fact_ids
```

### Step 2: Assign unknown = _seed_facts

```python
fid0, fid1, fid2 = _seed_facts
```

**Verification:**
```python
assert fid1 not in fact_ids
```

### Step 3: Call db.store_temporal_validity()

```python
db.store_temporal_validity(fid1, 'default')
```

**Verification:**
```python
assert fid2 in fact_ids
```

### Step 4: Call db.invalidate_fact_temporal()

```python
db.invalidate_fact_temporal(fid1, 'x', 'expired')
```

### Step 5: Assign channel_results = value

```python
channel_results = {'semantic': [(fid0, 0.9), (fid1, 0.8), (fid2, 0.7)]}
```

### Step 6: Assign filtered = temporal_validity_filter_impl(...)

```python
filtered = temporal_validity_filter_impl(channel_results, 'default', db, include_expired=False)
```

### Step 7: Assign fact_ids = value

```python
fact_ids = [item[0] for item in filtered['semantic']]
```

**Verification:**
```python
assert fid0 in fact_ids
```


## Complete Example

```python
# Setup
# Fixtures: db, _seed_facts

# Workflow
'temporal_validity_filter removes expired facts from results.'
fid0, fid1, fid2 = _seed_facts
db.store_temporal_validity(fid1, 'default')
db.invalidate_fact_temporal(fid1, 'x', 'expired')
channel_results = {'semantic': [(fid0, 0.9), (fid1, 0.8), (fid2, 0.7)]}
filtered = temporal_validity_filter_impl(channel_results, 'default', db, include_expired=False)
fact_ids = [item[0] for item in filtered['semantic']]
assert fid0 in fact_ids
assert fid1 not in fact_ids
assert fid2 in fact_ids
```

## Next Steps


---

*Source: test_temporal_filter.py:87 | Complexity: Intermediate | Last updated: 2026-05-05*