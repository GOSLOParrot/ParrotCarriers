# How To: Audit Trail Complete

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Pipeline creates audit entry with all fields populated.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.learning.consolidation_quantization_worker`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage`
- `superlocalmemory.core.config`
- `superlocalmemory.core.consolidation_engine`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db, ccq_config, profile_id
```

## Step-by-Step Guide

### Step 1: 'Pipeline creates audit entry with all fields populated.'

```python
'Pipeline creates audit entry with all fields populated.'
```

**Verification:**
```python
assert len(audits) >= 1
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert audit['cluster_id']
```

### Step 3: Call _seed_warm_cluster()

```python
_seed_warm_cluster(db, profile_id, count=3)
```

**Verification:**
```python
assert audit['block_id']
```

### Step 4: Assign cons = CognitiveConsolidator(...)

```python
cons = CognitiveConsolidator(db=db, config=ccq_config)
```

**Verification:**
```python
assert audit['fact_count'] >= 3
```

### Step 5: Call cons.run_pipeline()

```python
cons.run_pipeline(profile_id)
```

**Verification:**
```python
assert audit['gist_text']
```

### Step 6: Assign audits = db.get_ccq_audit(...)

```python
audits = db.get_ccq_audit(profile_id)
```

**Verification:**
```python
assert audit['extraction_mode'] in ('rules', 'llm')
```

### Step 7: Assign audit = value

```python
audit = audits[0]
```

**Verification:**
```python
assert audit['bytes_before'] >= 0
```


## Complete Example

```python
# Setup
# Fixtures: db, ccq_config, profile_id

# Workflow
'Pipeline creates audit entry with all fields populated.'
_seed_profile(db, profile_id)
_seed_warm_cluster(db, profile_id, count=3)
cons = CognitiveConsolidator(db=db, config=ccq_config)
cons.run_pipeline(profile_id)
audits = db.get_ccq_audit(profile_id)
assert len(audits) >= 1
audit = audits[0]
assert audit['cluster_id']
assert audit['block_id']
assert audit['fact_count'] >= 3
assert audit['gist_text']
assert audit['extraction_mode'] in ('rules', 'llm')
assert audit['bytes_before'] >= 0
assert audit['bytes_after'] >= 0
```

## Next Steps


---

*Source: test_consolidation_quantization_worker.py:142 | Complexity: Advanced | Last updated: 2026-05-05*