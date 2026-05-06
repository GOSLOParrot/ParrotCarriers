# How To: Scene Persisted

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test scene persisted

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
assert len(rows) == 1
```

### Step 2: Assign fact = _make_fact(...)

```python
fact = _make_fact('f1', 'Alice works at Google')
```

### Step 3: Assign scene = builder.assign_to_scene(...)

```python
scene = builder.assign_to_scene(fact, 'default')
```

### Step 4: Assign rows = db.execute(...)

```python
rows = db.execute('SELECT * FROM memory_scenes WHERE scene_id = ?', (scene.scene_id,))
```

**Verification:**
```python
assert len(rows) == 1
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
builder = SceneBuilder(db=db, embedder=None)
fact = _make_fact('f1', 'Alice works at Google')
scene = builder.assign_to_scene(fact, 'default')
rows = db.execute('SELECT * FROM memory_scenes WHERE scene_id = ?', (scene.scene_id,))
assert len(rows) == 1
```

## Next Steps


---

*Source: test_scene_builder.py:83 | Complexity: Intermediate | Last updated: 2026-05-05*