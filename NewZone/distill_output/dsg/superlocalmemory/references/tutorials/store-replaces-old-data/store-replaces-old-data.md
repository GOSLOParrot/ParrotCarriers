# How To: Store Replaces Old Data

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test store replaces old data

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
assert len(nodes) == 1
```

### Step 2: Assign fr1 = _make_file_record(...)

```python
fr1 = _make_file_record(node_count=1, edge_count=0)
```

**Verification:**
```python
assert nodes[0].node_id == 'n2'
```

### Step 3: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/mod.py', [n1], [], fr1)
```

### Step 4: Assign n2 = _make_node(...)

```python
n2 = _make_node('n2', 'bar', 'mod.bar')
```

### Step 5: Assign fr2 = _make_file_record(...)

```python
fr2 = _make_file_record(content_hash='def456', node_count=1)
```

### Step 6: Call store.store_file_nodes_edges()

```python
store.store_file_nodes_edges('src/mod.py', [n2], [], fr2)
```

### Step 7: Assign nodes = store.get_nodes_by_file(...)

```python
nodes = store.get_nodes_by_file('src/mod.py')
```

**Verification:**
```python
assert len(nodes) == 1
```


## Complete Example

```python
# Setup
# Fixtures: store

# Workflow
n1 = _make_node('n1', 'foo', 'mod.foo')
fr1 = _make_file_record(node_count=1, edge_count=0)
store.store_file_nodes_edges('src/mod.py', [n1], [], fr1)
n2 = _make_node('n2', 'bar', 'mod.bar')
fr2 = _make_file_record(content_hash='def456', node_count=1)
store.store_file_nodes_edges('src/mod.py', [n2], [], fr2)
nodes = store.get_nodes_by_file('src/mod.py')
assert len(nodes) == 1
assert nodes[0].node_id == 'n2'
```

## Next Steps


---

*Source: test_graph_store.py:103 | Complexity: Intermediate | Last updated: 2026-05-05*