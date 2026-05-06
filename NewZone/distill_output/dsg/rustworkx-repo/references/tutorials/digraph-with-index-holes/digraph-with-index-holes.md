# How To: Digraph With Index Holes

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test digraph with index holes

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 3: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', 1)
```

### Step 4: Call dag.add_child()

```python
dag.add_child(node_a, 'c', 1)
```

### Step 5: Call dag.remove_node()

```python
dag.remove_node(node_b)
```

### Step 6: Assign res = rustworkx.digraph_adjacency_matrix(...)

```python
res = rustworkx.digraph_adjacency_matrix(dag, lambda x: 1)
```

### Step 7: Call self.assertIsInstance()

```python
self.assertIsInstance(res, np.ndarray)
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(np.array_equal(np.array([[0, 1], [0, 0]]), res))
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
dag.add_child(node_a, 'c', 1)
dag.remove_node(node_b)
res = rustworkx.digraph_adjacency_matrix(dag, lambda x: 1)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0, 1], [0, 0]]), res))
```

## Next Steps


---

*Source: test_adjacency_matrix.py:109 | Complexity: Advanced | Last updated: 2026-05-05*