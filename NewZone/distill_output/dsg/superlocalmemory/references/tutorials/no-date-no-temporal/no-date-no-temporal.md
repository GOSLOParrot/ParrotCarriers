# How To: No Date No Temporal

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test no date no temporal

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

### Step 1: Call _setup_fact()

```python
_setup_fact(db, 'f1', 'No date fact', canonical_entities=['ent_a'])
```

**Verification:**
```python
assert len(temporal) == 0
```

### Step 2: Assign f2 = _setup_fact(...)

```python
f2 = _setup_fact(db, 'f2', 'Also no date', canonical_entities=['ent_a'])
```

### Step 3: Assign builder = GraphBuilder(...)

```python
builder = GraphBuilder(db=db)
```

### Step 4: Assign edges = builder.build_edges(...)

```python
edges = builder.build_edges(f2, 'default')
```

### Step 5: Assign temporal = value

```python
temporal = [e for e in edges if e.edge_type == EdgeType.TEMPORAL]
```

**Verification:**
```python
assert len(temporal) == 0
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
_setup_fact(db, 'f1', 'No date fact', canonical_entities=['ent_a'])
f2 = _setup_fact(db, 'f2', 'Also no date', canonical_entities=['ent_a'])
builder = GraphBuilder(db=db)
edges = builder.build_edges(f2, 'default')
temporal = [e for e in edges if e.edge_type == EdgeType.TEMPORAL]
assert len(temporal) == 0
```

## Next Steps


---

*Source: test_graph_builder.py:163 | Complexity: Intermediate | Last updated: 2026-05-05*