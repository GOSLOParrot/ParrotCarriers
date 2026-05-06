# How To: Store Does Not Delete Facts

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: No operation should ever delete facts (Rule 17).

Store, consolidation, and temporal invalidation must all
preserve the original fact count.

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

### Step 1: 'No operation should ever delete facts (Rule 17).\n\n        Store, consolidation, and temporal invalidation must all\n        preserve the original fact count.\n        '

```python
'No operation should ever delete facts (Rule 17).\n\n        Store, consolidation, and temporal invalidation must all\n        preserve the original fact count.\n        '
```

**Verification:**
```python
assert count_after_contra >= count_after_store
```

### Step 2: Assign engine = _create_v32_engine(...)

```python
engine = _create_v32_engine(tmp_path)
```

**Verification:**
```python
assert count_after_consol >= count_after_contra, f'Facts deleted during consolidation: {count_after_contra} -> {count_after_consol}'
```

### Step 3: Assign count_after_store = value

```python
count_after_store = engine.fact_count
```

### Step 4: Call engine.store()

```python
engine.store(_CONTRADICTION_FACT, session_id='s2')
```

### Step 5: Assign count_after_contra = value

```python
count_after_contra = engine.fact_count
```

**Verification:**
```python
assert count_after_contra >= count_after_store
```

### Step 6: Assign count_after_consol = value

```python
count_after_consol = engine.fact_count
```

**Verification:**
```python
assert count_after_consol >= count_after_contra, f'Facts deleted during consolidation: {count_after_contra} -> {count_after_consol}'
```

### Step 7: Call engine.close()

```python
engine.close()
```

### Step 8: Call engine.store()

```python
engine.store(content, session_id='s1')
```

### Step 9: Call engine._consolidation_engine.consolidate()

```python
engine._consolidation_engine.consolidate('default')
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'No operation should ever delete facts (Rule 17).\n\n        Store, consolidation, and temporal invalidation must all\n        preserve the original fact count.\n        '
engine = _create_v32_engine(tmp_path)
for content in _SESSION_1_FACTS:
    engine.store(content, session_id='s1')
count_after_store = engine.fact_count
engine.store(_CONTRADICTION_FACT, session_id='s2')
count_after_contra = engine.fact_count
assert count_after_contra >= count_after_store
if engine._consolidation_engine:
    engine._consolidation_engine.consolidate('default')
count_after_consol = engine.fact_count
assert count_after_consol >= count_after_contra, f'Facts deleted during consolidation: {count_after_contra} -> {count_after_consol}'
engine.close()
```

## Next Steps


---

*Source: test_e2e_v32.py:647 | Complexity: Advanced | Last updated: 2026-05-05*