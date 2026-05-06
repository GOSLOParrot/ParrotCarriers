# How To: Filter Applies To All Channels

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Filter removes expired facts from all channels.

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

### Step 1: 'Filter removes expired facts from all channels.'

```python
'Filter removes expired facts from all channels.'
```

**Verification:**
```python
assert fid1 not in fact_ids, f'fid1 should be excluded from {ch_name}'
```

### Step 2: Assign unknown = _seed_facts

```python
fid0, fid1, fid2 = _seed_facts
```

### Step 3: Call db.store_temporal_validity()

```python
db.store_temporal_validity(fid1, 'default')
```

### Step 4: Call db.invalidate_fact_temporal()

```python
db.invalidate_fact_temporal(fid1, 'x', 'expired')
```

### Step 5: Assign channel_results = value

```python
channel_results = {'semantic': [(fid0, 0.9), (fid1, 0.8)], 'bm25': [(fid1, 0.7), (fid2, 0.6)], 'entity_graph': [(fid0, 0.5), (fid1, 0.4)]}
```

### Step 6: Assign filtered = temporal_validity_filter_impl(...)

```python
filtered = temporal_validity_filter_impl(channel_results, 'default', db, include_expired=False)
```

### Step 7: Assign fact_ids = value

```python
fact_ids = [_extract_fact_id(item) for item in results]
```

**Verification:**
```python
assert fid1 not in fact_ids, f'fid1 should be excluded from {ch_name}'
```


## Complete Example

```python
# Setup
# Fixtures: db, _seed_facts

# Workflow
'Filter removes expired facts from all channels.'
fid0, fid1, fid2 = _seed_facts
db.store_temporal_validity(fid1, 'default')
db.invalidate_fact_temporal(fid1, 'x', 'expired')
channel_results = {'semantic': [(fid0, 0.9), (fid1, 0.8)], 'bm25': [(fid1, 0.7), (fid2, 0.6)], 'entity_graph': [(fid0, 0.5), (fid1, 0.4)]}
filtered = temporal_validity_filter_impl(channel_results, 'default', db, include_expired=False)
for ch_name, results in filtered.items():
    fact_ids = [_extract_fact_id(item) for item in results]
    assert fid1 not in fact_ids, f'fid1 should be excluded from {ch_name}'
```

## Next Steps


---

*Source: test_temporal_filter.py:144 | Complexity: Intermediate | Last updated: 2026-05-05*