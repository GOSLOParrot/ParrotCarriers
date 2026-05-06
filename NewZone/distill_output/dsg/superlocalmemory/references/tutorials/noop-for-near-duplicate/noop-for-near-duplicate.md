# How To: Noop For Near Duplicate

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test noop for near duplicate

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.core.config`
- `superlocalmemory.encoding.consolidator`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Assign existing = _store_fact(...)

```python
existing = _store_fact(db, 'f_existing', 'Alice works at Google', canonical_entities=['ent_alice'], embedding=[1.0, 0.0, 0.0])
```

**Verification:**
```python
assert action.action_type == ConsolidationActionType.NOOP
```

### Step 2: Assign consolidator = MemoryConsolidator(...)

```python
consolidator = MemoryConsolidator(db=db)
```

### Step 3: Call db.store_memory()

```python
db.store_memory(MemoryRecord(memory_id='m_dup', content='parent'))
```

### Step 4: Assign new_fact = AtomicFact(...)

```python
new_fact = AtomicFact(fact_id='f_dup', memory_id='m_dup', content='Alice works at Google', canonical_entities=['ent_alice'], embedding=[1.0, 0.0, 0.0])
```

### Step 5: Assign action = consolidator.consolidate(...)

```python
action = consolidator.consolidate(new_fact, 'default')
```

**Verification:**
```python
assert action.action_type == ConsolidationActionType.NOOP
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
existing = _store_fact(db, 'f_existing', 'Alice works at Google', canonical_entities=['ent_alice'], embedding=[1.0, 0.0, 0.0])
consolidator = MemoryConsolidator(db=db)
db.store_memory(MemoryRecord(memory_id='m_dup', content='parent'))
new_fact = AtomicFact(fact_id='f_dup', memory_id='m_dup', content='Alice works at Google', canonical_entities=['ent_alice'], embedding=[1.0, 0.0, 0.0])
action = consolidator.consolidate(new_fact, 'default')
assert action.action_type == ConsolidationActionType.NOOP
```

## Next Steps


---

*Source: test_consolidator.py:150 | Complexity: Intermediate | Last updated: 2026-05-05*