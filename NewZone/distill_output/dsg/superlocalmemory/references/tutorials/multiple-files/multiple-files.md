# How To: Multiple Files

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test multiple files

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
n1 = _make_node('n1', 'foo', 'a.foo', 'src/a.py')
```

**Verification:**
```python
assert len(nodes) == 2
```

### Step 2: Assign n2 = _make_node(...)

```python
n2 = _make_node('n2', 'bar', 'b.bar', 'src/b.py')
```

### Step 3: Assign fr_a = _make_file_record(...)

```python
fr_a = _make_file_record('src/a.py', 'h1', 1, 0)
```

### Step 4: Assign fr_b = _make_file_record(...)

```python
fr_b = _make_file_record('src/b.py', 'h2', 1, 0)
```

### Step 5: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/a.py', [n1], [], fr_a)
```

### Step 6: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/b.py', [n2], [], fr_b)
```

### Step 7: Assign unknown = store.get_all_nodes_and_edges(...)

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
n1 = _make_node('n1', 'foo', 'a.foo', 'src/a.py')
n2 = _make_node('n2', 'bar', 'b.bar', 'src/b.py')
fr_a = _make_file_record('src/a.py', 'h1', 1, 0)
fr_b = _make_file_record('src/b.py', 'h2', 1, 0)
store.store_file_nodes_edges('src/a.py', [n1], [], fr_a)
store.store_file_nodes_edges('src/b.py', [n2], [], fr_b)
nodes, edges = store.get_all_nodes_and_edges()
assert len(nodes) == 2
```

## Next Steps


---

*Source: test_graph_store.py:199 | Complexity: Intermediate | Last updated: 2026-05-05*