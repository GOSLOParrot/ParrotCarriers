# How To: No Causal Marker No Edge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test no causal marker no edge

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
_setup_fact(db, 'f1', 'Alice likes cats', canonical_entities=['ent_alice'])
```

**Verification:**
```python
assert len(causal) == 0
```

### Step 2: Assign f2 = _setup_fact(...)

```python
f2 = _setup_fact(db, 'f2', 'Alice has a pet', canonical_entities=['ent_alice'])
```

### Step 3: Assign builder = GraphBuilder(...)

```python
builder = GraphBuilder(db=db)
```

### Step 4: Assign edges = builder.build_edges(...)

```python
edges = builder.build_edges(f2, 'default')
```

### Step 5: Assign causal = value

```python
causal = [e for e in edges if e.edge_type == EdgeType.CAUSAL]
```

**Verification:**
```python
assert len(causal) == 0
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
_setup_fact(db, 'f1', 'Alice likes cats', canonical_entities=['ent_alice'])
f2 = _setup_fact(db, 'f2', 'Alice has a pet', canonical_entities=['ent_alice'])
builder = GraphBuilder(db=db)
edges = builder.build_edges(f2, 'default')
causal = [e for e in edges if e.edge_type == EdgeType.CAUSAL]
assert len(causal) == 0
```

## Next Steps


---

*Source: test_graph_builder.py:239 | Complexity: Intermediate | Last updated: 2026-05-05*