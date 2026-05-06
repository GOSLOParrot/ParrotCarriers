# How To: Cache Invalidation On Write

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test cache invalidation on write

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.graph_engine`
- `superlocalmemory.code_graph.graph_store`
- `superlocalmemory.code_graph.models`
- `rustworkx`

**Setup Required:**
```python
# Fixtures: store, engine
```

## Step-by-Step Guide

### Step 1: Call _populate_simple_graph()

```python
_populate_simple_graph(store)
```

**Verification:**
```python
assert g2 is not g1
```

### Step 2: Assign g1 = engine.build_graph(...)

```python
g1 = engine.build_graph()
```

**Verification:**
```python
assert g2.num_nodes() == 4
```

### Step 3: Assign n_d = _node(...)

```python
n_d = _node('d', 'func_d', 'mod.func_d')
```

### Step 4: Assign fr2 = FileRecord(...)

```python
fr2 = FileRecord(file_path='src/other.py', content_hash='h2', mtime=2.0, language='python')
```

### Step 5: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/other.py', [n_d], [], fr2)
```

### Step 6: Assign g2 = engine.build_graph(...)

```python
g2 = engine.build_graph()
```

**Verification:**
```python
assert g2 is not g1
```


## Complete Example

```python
# Setup
# Fixtures: store, engine

# Workflow
_populate_simple_graph(store)
g1 = engine.build_graph()
n_d = _node('d', 'func_d', 'mod.func_d')
fr2 = FileRecord(file_path='src/other.py', content_hash='h2', mtime=2.0, language='python')
store.store_file_nodes_edges('src/other.py', [n_d], [], fr2)
g2 = engine.build_graph()
assert g2 is not g1
assert g2.num_nodes() == 4
```

## Next Steps


---

*Source: test_graph_engine.py:114 | Complexity: Intermediate | Last updated: 2026-05-05*