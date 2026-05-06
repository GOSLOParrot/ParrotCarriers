# How To: Consolidation Idempotency

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Running consolidation twice produces identical Core Memory state.

L18 guarantee: INSERT OR REPLACE on UNIQUE(profile_id, block_type).

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

### Step 1: 'Running consolidation twice produces identical Core Memory state.\n\n        L18 guarantee: INSERT OR REPLACE on UNIQUE(profile_id, block_type).\n        '

```python
'Running consolidation twice produces identical Core Memory state.\n\n        L18 guarantee: INSERT OR REPLACE on UNIQUE(profile_id, block_type).\n        '
```

**Verification:**
```python
assert engine._consolidation_engine is not None
```

### Step 2: Assign engine = _create_v32_engine(...)

```python
engine = _create_v32_engine(tmp_path)
```

**Verification:**
```python
assert r1.get('success') is True
```

### Step 3: Assign r1 = engine._consolidation_engine.consolidate(...)

```python
r1 = engine._consolidation_engine.consolidate('default')
```

**Verification:**
```python
assert r2.get('success') is True
```

### Step 4: Assign blocks_1 = engine._db.get_core_blocks(...)

```python
blocks_1 = engine._db.get_core_blocks('default')
```

**Verification:**
```python
assert len(blocks_1) == len(blocks_2), f'Block count mismatch: {len(blocks_1)} vs {len(blocks_2)}'
```

### Step 5: Assign r2 = engine._consolidation_engine.consolidate(...)

```python
r2 = engine._consolidation_engine.consolidate('default')
```

**Verification:**
```python
assert types_1 == types_2
```

### Step 6: Assign blocks_2 = engine._db.get_core_blocks(...)

```python
blocks_2 = engine._db.get_core_blocks('default')
```

**Verification:**
```python
assert len(blocks_1) == len(blocks_2), f'Block count mismatch: {len(blocks_1)} vs {len(blocks_2)}'
```

### Step 7: Assign types_1 = value

```python
types_1 = {b['block_type'] for b in blocks_1}
```

### Step 8: Assign types_2 = value

```python
types_2 = {b['block_type'] for b in blocks_2}
```

**Verification:**
```python
assert types_1 == types_2
```

### Step 9: Call engine.close()

```python
engine.close()
```

### Step 10: Call engine.store()

```python
engine.store(content, session_id='s1')
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Running consolidation twice produces identical Core Memory state.\n\n        L18 guarantee: INSERT OR REPLACE on UNIQUE(profile_id, block_type).\n        '
engine = _create_v32_engine(tmp_path)
for content in _SESSION_1_FACTS[:5]:
    engine.store(content, session_id='s1')
assert engine._consolidation_engine is not None
r1 = engine._consolidation_engine.consolidate('default')
assert r1.get('success') is True
blocks_1 = engine._db.get_core_blocks('default')
r2 = engine._consolidation_engine.consolidate('default')
assert r2.get('success') is True
blocks_2 = engine._db.get_core_blocks('default')
assert len(blocks_1) == len(blocks_2), f'Block count mismatch: {len(blocks_1)} vs {len(blocks_2)}'
types_1 = {b['block_type'] for b in blocks_1}
types_2 = {b['block_type'] for b in blocks_2}
assert types_1 == types_2
engine.close()
```

## Next Steps


---

*Source: test_e2e_v32.py:522 | Complexity: Advanced | Last updated: 2026-05-05*