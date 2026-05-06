# How To: Facts Linked To Entities

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test facts linked to entities

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `hashlib`
- `json`
- `pathlib`
- `unittest.mock`
- `numpy`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.engine`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: engine
```

## Step-by-Step Guide

### Step 1: Call engine.store()

```python
engine.store('Alice met Bob at the central park near downtown during the summer festival.', session_id='s1')
```

**Verification:**
```python
assert linked, 'At least one fact should have canonical_entities set'
```

### Step 2: Assign rows = _query(...)

```python
rows = _query(engine, "SELECT canonical_entities_json FROM atomic_facts WHERE profile_id = 'default'")
```

### Step 3: Assign linked = False

```python
linked = False
```

**Verification:**
```python
assert linked, 'At least one fact should have canonical_entities set'
```

### Step 4: Assign ce = json.loads(...)

```python
ce = json.loads(r['canonical_entities_json'])
```

### Step 5: Assign linked = True

```python
linked = True
```


## Complete Example

```python
# Setup
# Fixtures: engine

# Workflow
engine.store('Alice met Bob at the central park near downtown during the summer festival.', session_id='s1')
rows = _query(engine, "SELECT canonical_entities_json FROM atomic_facts WHERE profile_id = 'default'")
linked = False
for r in rows:
    ce = json.loads(r['canonical_entities_json'])
    if ce:
        linked = True
assert linked, 'At least one fact should have canonical_entities set'
```

## Next Steps


---

*Source: test_encoding_wiring.py:188 | Complexity: Intermediate | Last updated: 2026-05-05*