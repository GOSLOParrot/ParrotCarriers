# How To: No Ann No Semantic

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test no ann no semantic

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
f1 = _setup_fact(db, 'f1', 'Fact', embedding=[1.0, 0.0])
```

**Verification:**
```python
assert len(semantic) == 0
```

### Step 2: Assign builder = GraphBuilder(...)

```python
builder = GraphBuilder(db=db, ann_index=None)
```

### Step 3: Assign edges = builder.build_edges(...)

```python
edges = builder.build_edges(f1, 'default')
```

### Step 4: Assign semantic = value

```python
semantic = [e for e in edges if e.edge_type == EdgeType.SEMANTIC]
```

**Verification:**
```python
assert len(semantic) == 0
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
f1 = _setup_fact(db, 'f1', 'Fact', embedding=[1.0, 0.0])
builder = GraphBuilder(db=db, ann_index=None)
edges = builder.build_edges(f1, 'default')
semantic = [e for e in edges if e.edge_type == EdgeType.SEMANTIC]
assert len(semantic) == 0
```

## Next Steps


---

*Source: test_graph_builder.py:204 | Complexity: Intermediate | Last updated: 2026-05-05*