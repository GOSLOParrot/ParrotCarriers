# How To: Filter By Kind

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test filter by kind

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.code_graph.blast_radius`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.graph_engine`
- `superlocalmemory.code_graph.graph_store`
- `superlocalmemory.code_graph.models`
- `rustworkx`

**Setup Required:**
```python
# Fixtures: store, br
```

## Step-by-Step Guide

### Step 1: Assign a = _node(...)

```python
a = _node('a', 'a', 'mod.a')
```

**Verification:**
```python
assert 'b' in result.impacted_nodes
```

### Step 2: Assign b = _node(...)

```python
b = _node('b', 'b', 'mod.b')
```

**Verification:**
```python
assert 'c' not in result.impacted_nodes
```

### Step 3: Assign c = _node(...)

```python
c = _node('c', 'c', 'mod.c')
```

### Step 4: Assign e1 = _edge(...)

```python
e1 = _edge('e1', 'a', 'b', kind=EdgeKind.CALLS)
```

### Step 5: Assign e2 = _edge(...)

```python
e2 = _edge('e2', 'a', 'c', kind=EdgeKind.IMPORTS)
```

### Step 6: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/mod.py', [a, b, c], [e1, e2], _fr())
```

### Step 7: Assign result = br.compute(...)

```python
result = br.compute(seed_node_ids=['a'], max_depth=1, direction='forward', edge_kinds={EdgeKind.CALLS.value})
```

**Verification:**
```python
assert 'b' in result.impacted_nodes
```


## Complete Example

```python
# Setup
# Fixtures: store, br

# Workflow
a = _node('a', 'a', 'mod.a')
b = _node('b', 'b', 'mod.b')
c = _node('c', 'c', 'mod.c')
e1 = _edge('e1', 'a', 'b', kind=EdgeKind.CALLS)
e2 = _edge('e2', 'a', 'c', kind=EdgeKind.IMPORTS)
store.store_file_nodes_edges('src/mod.py', [a, b, c], [e1, e2], _fr())
result = br.compute(seed_node_ids=['a'], max_depth=1, direction='forward', edge_kinds={EdgeKind.CALLS.value})
assert 'b' in result.impacted_nodes
assert 'c' not in result.impacted_nodes
```

## Next Steps


---

*Source: test_blast_radius.py:208 | Complexity: Intermediate | Last updated: 2026-05-05*