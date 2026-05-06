# How To: Shared Entity Creates Edge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test shared entity creates edge

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pathlib`
- `unittest.mock`
- `pytest`
- `superlocalmemory.encoding.graph_builder`
- `superlocalmemory.storage`
- `superlocalmemory.storage.database`
- `superlocalmemory.storage.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: Assign f1 = _setup_fact(...)

```python
f1 = _setup_fact(db, 'f1', 'Alice works at Google', canonical_entities=['ent_alice'])
```

**Verification:**
```python
assert len(entity_edges) == 1
```

### Step 2: Assign f2 = _setup_fact(...)

```python
f2 = _setup_fact(db, 'f2', 'Alice likes hiking', canonical_entities=['ent_alice'])
```

**Verification:**
```python
assert entity_edges[0].source_id == 'f2'
```

### Step 3: Assign builder = GraphBuilder(...)

```python
builder = GraphBuilder(db=db)
```

**Verification:**
```python
assert entity_edges[0].target_id == 'f1'
```

### Step 4: Assign edges = builder.build_edges(...)

```python
edges = builder.build_edges(f2, 'default')
```

### Step 5: Assign entity_edges = value

```python
entity_edges = [e for e in edges if e.edge_type == EdgeType.ENTITY]
```

**Verification:**
```python
assert len(entity_edges) == 1
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
f1 = _setup_fact(db, 'f1', 'Alice works at Google', canonical_entities=['ent_alice'])
f2 = _setup_fact(db, 'f2', 'Alice likes hiking', canonical_entities=['ent_alice'])
builder = GraphBuilder(db=db)
edges = builder.build_edges(f2, 'default')
entity_edges = [e for e in edges if e.edge_type == EdgeType.ENTITY]
assert len(entity_edges) == 1
assert entity_edges[0].source_id == 'f2'
assert entity_edges[0].target_id == 'f1'
```

## Next Steps


---

*Source: test_graph_builder.py:100 | Complexity: Intermediate | Last updated: 2026-05-05*