# How To: Causal Marker Creates Edge

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test causal marker creates edge

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
_setup_fact(db, 'f1', 'Alice left the company', canonical_entities=['ent_alice'])
```

**Verification:**
```python
assert len(causal) >= 1
```

### Step 2: Assign f2 = _setup_fact(...)

```python
f2 = _setup_fact(db, 'f2', 'Alice moved to New York because of the new job', canonical_entities=['ent_alice'])
```

**Verification:**
```python
assert all((e.target_id == 'f2' for e in causal))
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
assert len(causal) >= 1
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
_setup_fact(db, 'f1', 'Alice left the company', canonical_entities=['ent_alice'])
f2 = _setup_fact(db, 'f2', 'Alice moved to New York because of the new job', canonical_entities=['ent_alice'])
builder = GraphBuilder(db=db)
edges = builder.build_edges(f2, 'default')
causal = [e for e in edges if e.edge_type == EdgeType.CAUSAL]
assert len(causal) >= 1
assert all((e.target_id == 'f2' for e in causal))
```

## Next Steps


---

*Source: test_graph_builder.py:225 | Complexity: Intermediate | Last updated: 2026-05-05*