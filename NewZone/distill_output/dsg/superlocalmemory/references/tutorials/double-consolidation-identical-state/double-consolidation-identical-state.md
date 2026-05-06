# How To: Double Consolidation Identical State

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Running consolidate() twice produces identical Core Memory state.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `sqlite3`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.core.consolidation_engine`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: engine, tmp_db
```

## Step-by-Step Guide

### Step 1: 'Running consolidate() twice produces identical Core Memory state.'

```python
'Running consolidate() twice produces identical Core Memory state.'
```

**Verification:**
```python
assert contents_first == contents_second
```

### Step 2: Call _seed_facts()

```python
_seed_facts(tmp_db, 'default', 5)
```

**Verification:**
```python
assert len(blocks_second) == 5
```

### Step 3: Call engine.consolidate()

```python
engine.consolidate('default', lightweight=False)
```

### Step 4: Assign blocks_first = tmp_db.get_core_blocks(...)

```python
blocks_first = tmp_db.get_core_blocks('default')
```

### Step 5: Assign contents_first = value

```python
contents_first = {b['block_type']: b['content'] for b in blocks_first}
```

### Step 6: Call engine.consolidate()

```python
engine.consolidate('default', lightweight=False)
```

### Step 7: Assign blocks_second = tmp_db.get_core_blocks(...)

```python
blocks_second = tmp_db.get_core_blocks('default')
```

### Step 8: Assign contents_second = value

```python
contents_second = {b['block_type']: b['content'] for b in blocks_second}
```

**Verification:**
```python
assert contents_first == contents_second
```


## Complete Example

```python
# Setup
# Fixtures: engine, tmp_db

# Workflow
'Running consolidate() twice produces identical Core Memory state.'
_seed_facts(tmp_db, 'default', 5)
engine.consolidate('default', lightweight=False)
blocks_first = tmp_db.get_core_blocks('default')
contents_first = {b['block_type']: b['content'] for b in blocks_first}
engine.consolidate('default', lightweight=False)
blocks_second = tmp_db.get_core_blocks('default')
contents_second = {b['block_type']: b['content'] for b in blocks_second}
assert contents_first == contents_second
assert len(blocks_second) == 5
```

## Next Steps


---

*Source: test_consolidation_engine.py:471 | Complexity: Advanced | Last updated: 2026-05-05*