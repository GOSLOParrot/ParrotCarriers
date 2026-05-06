# How To: No Canonical Entities

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test no canonical entities

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
f1 = _setup_fact(db, 'f1', 'Some fact', canonical_entities=[])
```

**Verification:**
```python
assert len(entity_edges) == 0
```

### Step 2: Assign builder = GraphBuilder(...)

```python
builder = GraphBuilder(db=db)
```

### Step 3: Assign edges = builder.build_edges(...)

```python
edges = builder.build_edges(f1, 'default')
```

### Step 4: Assign entity_edges = value

```python
entity_edges = [e for e in edges if e.edge_type == EdgeType.ENTITY]
```

**Verification:**
```python
assert len(entity_edges) == 0
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
f1 = _setup_fact(db, 'f1', 'Some fact', canonical_entities=[])
builder = GraphBuilder(db=db)
edges = builder.build_edges(f1, 'default')
entity_edges = [e for e in edges if e.edge_type == EdgeType.ENTITY]
assert len(entity_edges) == 0
```

## Next Steps


---

*Source: test_graph_builder.py:122 | Complexity: Intermediate | Last updated: 2026-05-05*