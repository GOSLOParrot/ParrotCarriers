# How To: Within Window

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test within window

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
_setup_fact(db, 'f1', 'Monday meeting', canonical_entities=['ent_alice'], obs_date='2026-03-10T10:00:00')
```

**Verification:**
```python
assert len(temporal) >= 1
```

### Step 2: Assign f2 = _setup_fact(...)

```python
f2 = _setup_fact(db, 'f2', 'Tuesday meeting', canonical_entities=['ent_alice'], obs_date='2026-03-11T10:00:00')
```

**Verification:**
```python
assert all((e.weight > 0 for e in temporal))
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
assert len(temporal) >= 1
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
_setup_fact(db, 'f1', 'Monday meeting', canonical_entities=['ent_alice'], obs_date='2026-03-10T10:00:00')
f2 = _setup_fact(db, 'f2', 'Tuesday meeting', canonical_entities=['ent_alice'], obs_date='2026-03-11T10:00:00')
builder = GraphBuilder(db=db)
edges = builder.build_edges(f2, 'default')
temporal = [e for e in edges if e.edge_type == EdgeType.TEMPORAL]
assert len(temporal) >= 1
assert all((e.weight > 0 for e in temporal))
```

## Next Steps


---

*Source: test_graph_builder.py:135 | Complexity: Intermediate | Last updated: 2026-05-05*