# How To: Finds Scene

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test finds scene

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.encoding.scene_builder`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Assign builder = SceneBuilder(...)

```python
builder = SceneBuilder(db=db, embedder=None)
```

**Verification:**
```python
assert found is not None
```

### Step 2: Assign fact = _make_fact(...)

```python
fact = _make_fact('f1', 'Alice works at Google')
```

**Verification:**
```python
assert found.scene_id == scene.scene_id
```

### Step 3: Assign scene = builder.assign_to_scene(...)

```python
scene = builder.assign_to_scene(fact, 'default')
```

### Step 4: Assign found = builder.get_scene_for_fact(...)

```python
found = builder.get_scene_for_fact('f1', 'default')
```

**Verification:**
```python
assert found is not None
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
builder = SceneBuilder(db=db, embedder=None)
fact = _make_fact('f1', 'Alice works at Google')
scene = builder.assign_to_scene(fact, 'default')
found = builder.get_scene_for_fact('f1', 'default')
assert found is not None
assert found.scene_id == scene.scene_id
```

## Next Steps


---

*Source: test_scene_builder.py:149 | Complexity: Intermediate | Last updated: 2026-05-05*