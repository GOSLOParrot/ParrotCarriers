# How To: Limits To Last 20 Facts

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test limits to last 20 facts

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `pytest`
- `superlocalmemory.encoding.observation_builder`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: builder, db
```

## Step-by-Step Guide

### Step 1: Call db.store_entity()

```python
db.store_entity(CanonicalEntity(entity_id='ent_many', profile_id='default', canonical_name='ManyFacts', entity_type='concept'))
```

**Verification:**
```python
assert len(parts) <= 20
```

### Step 2: Assign fact_ids = value

```python
fact_ids = [f'f_many_{i}' for i in range(25)]
```

### Step 3: Assign summary = builder._build_summary(...)

```python
summary = builder._build_summary('ent_many', fact_ids, 'default')
```

### Step 4: Assign parts = summary.split(...)

```python
parts = summary.split(' | ')
```

**Verification:**
```python
assert len(parts) <= 20
```

### Step 5: Assign mem_id = value

```python
mem_id = f'm_many_{i}'
```

### Step 6: Assign fact_id = value

```python
fact_id = f'f_many_{i}'
```

### Step 7: Call db.store_memory()

```python
db.store_memory(MemoryRecord(memory_id=mem_id, content='parent'))
```

### Step 8: Call db.store_fact()

```python
db.store_fact(AtomicFact(fact_id=fact_id, memory_id=mem_id, profile_id='default', content=f'Fact number {i} about ManyFacts', canonical_entities=['ent_many']))
```


## Complete Example

```python
# Setup
# Fixtures: builder, db

# Workflow
db.store_entity(CanonicalEntity(entity_id='ent_many', profile_id='default', canonical_name='ManyFacts', entity_type='concept'))
for i in range(25):
    mem_id = f'm_many_{i}'
    fact_id = f'f_many_{i}'
    db.store_memory(MemoryRecord(memory_id=mem_id, content='parent'))
    db.store_fact(AtomicFact(fact_id=fact_id, memory_id=mem_id, profile_id='default', content=f'Fact number {i} about ManyFacts', canonical_entities=['ent_many']))
fact_ids = [f'f_many_{i}' for i in range(25)]
summary = builder._build_summary('ent_many', fact_ids, 'default')
parts = summary.split(' | ')
assert len(parts) <= 20
```

## Next Steps


---

*Source: test_observation_builder.py:214 | Complexity: Advanced | Last updated: 2026-05-05*