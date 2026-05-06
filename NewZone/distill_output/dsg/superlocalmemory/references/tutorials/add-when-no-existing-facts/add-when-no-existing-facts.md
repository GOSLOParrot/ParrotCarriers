# How To: Add When No Existing Facts

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test add when no existing facts

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

### Step 1: Assign consolidator = MemoryConsolidator(...)

```python
consolidator = MemoryConsolidator(db=db)
```

**Verification:**
```python
assert action.action_type == ConsolidationActionType.ADD
```

### Step 2: Call db.store_memory()

```python
db.store_memory(MemoryRecord(memory_id='m_new', content='parent'))
```

**Verification:**
```python
assert any((f.fact_id == 'f_new' for f in facts))
```

### Step 3: Assign new_fact = AtomicFact(...)

```python
new_fact = AtomicFact(fact_id='f_new', memory_id='m_new', content='Alice works at Google', canonical_entities=['ent_alice'])
```

### Step 4: Assign action = consolidator.consolidate(...)

```python
action = consolidator.consolidate(new_fact, 'default')
```

**Verification:**
```python
assert action.action_type == ConsolidationActionType.ADD
```

### Step 5: Assign facts = db.get_all_facts(...)

```python
facts = db.get_all_facts('default')
```

**Verification:**
```python
assert any((f.fact_id == 'f_new' for f in facts))
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
consolidator = MemoryConsolidator(db=db)
db.store_memory(MemoryRecord(memory_id='m_new', content='parent'))
new_fact = AtomicFact(fact_id='f_new', memory_id='m_new', content='Alice works at Google', canonical_entities=['ent_alice'])
action = consolidator.consolidate(new_fact, 'default')
assert action.action_type == ConsolidationActionType.ADD
facts = db.get_all_facts('default')
assert any((f.fact_id == 'f_new' for f in facts))
```

## Next Steps


---

*Source: test_consolidator.py:117 | Complexity: Intermediate | Last updated: 2026-05-05*