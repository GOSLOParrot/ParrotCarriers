# How To: Pipeline No Candidates

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Pipeline returns empty result when no candidates exist.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `datetime`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.encoding.cognitive_consolidator`
- `unittest.mock`
- `superlocalmemory.encoding.cognitive_consolidator`
- `unittest.mock`
- `builtins`
- `superlocalmemory.encoding.cognitive_consolidator`
- `superlocalmemory.core.config`
- `unittest.mock`

**Setup Required:**
```python
# Fixtures: db, consolidator, profile_id
```

## Step-by-Step Guide

### Step 1: 'Pipeline returns empty result when no candidates exist.'

```python
'Pipeline returns empty result when no candidates exist.'
```

**Verification:**
```python
assert result.clusters_processed == 0
```

### Step 2: Call _seed_profile()

```python
_seed_profile(db, profile_id)
```

**Verification:**
```python
assert result.blocks_created == 0
```

### Step 3: Assign result = consolidator.run_pipeline(...)

```python
result = consolidator.run_pipeline(profile_id)
```

**Verification:**
```python
assert result.facts_archived == 0
```


## Complete Example

```python
# Setup
# Fixtures: db, consolidator, profile_id

# Workflow
'Pipeline returns empty result when no candidates exist.'
_seed_profile(db, profile_id)
result = consolidator.run_pipeline(profile_id)
assert result.clusters_processed == 0
assert result.blocks_created == 0
assert result.facts_archived == 0
assert result.errors == ()
```

## Next Steps


---

*Source: test_cognitive_consolidator.py:683 | Complexity: Beginner | Last updated: 2026-05-05*