# How To: Returns All Data

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test returns all data

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.graph_store`
- `superlocalmemory.code_graph.models`

**Setup Required:**
```python
# Fixtures: store
```

## Step-by-Step Guide

### Step 1: Assign n1 = _make_node(...)

```python
n1 = _make_node('n1', 'foo', 'mod.foo')
```

**Verification:**
```python
assert len(nodes) == 2
```

### Step 2: Assign n2 = _make_node(...)

```python
n2 = _make_node('n2', 'bar', 'mod.bar')
```

**Verification:**
```python
assert len(edges) == 1
```

### Step 3: Assign edge = _make_edge(...)

```python
edge = _make_edge('e1', EdgeKind.CALLS, 'n1', 'n2')
```

### Step 4: Assign fr = _make_file_record(...)

```python
fr = _make_file_record()
```

### Step 5: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/mod.py', [n1, n2], [edge], fr)
```

### Step 6: Assign unknown = store.get_all_nodes_and_edges(...)

```python
nodes, edges = store.get_all_nodes_and_edges()
```

**Verification:**
```python
assert len(nodes) == 2
```


## Complete Example

```python
# Setup
# Fixtures: store

# Workflow
n1 = _make_node('n1', 'foo', 'mod.foo')
n2 = _make_node('n2', 'bar', 'mod.bar')
edge = _make_edge('e1', EdgeKind.CALLS, 'n1', 'n2')
fr = _make_file_record()
store.store_file_nodes_edges('src/mod.py', [n1, n2], [edge], fr)
nodes, edges = store.get_all_nodes_and_edges()
assert len(nodes) == 2
assert len(edges) == 1
```

## Next Steps


---

*Source: test_graph_store.py:188 | Complexity: Intermediate | Last updated: 2026-05-05*