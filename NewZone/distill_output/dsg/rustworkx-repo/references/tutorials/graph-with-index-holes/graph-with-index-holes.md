# How To: Graph With Index Holes

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test graph with index holes

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Assign node_a = graph.add_node(...)

```python
node_a = graph.add_node('a')
```

### Step 3: Assign node_b = graph.add_node(...)

```python
node_b = graph.add_node('b')
```

### Step 4: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 1)
```

### Step 5: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_a, node_c, 1)
```

### Step 7: Call graph.remove_node()

```python
graph.remove_node(node_b)
```

### Step 8: Assign res = rustworkx.graph_adjacency_matrix(...)

```python
res = rustworkx.graph_adjacency_matrix(graph, lambda x: 1)
```

### Step 9: Call self.assertIsInstance()

```python
self.assertIsInstance(res, np.ndarray)
```

### Step 10: Call self.assertTrue()

```python
self.assertTrue(np.array_equal(np.array([[0, 1], [1, 0]]), res))
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
graph.remove_node(node_b)
res = rustworkx.graph_adjacency_matrix(graph, lambda x: 1)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0, 1], [1, 0]]), res))
```

## Next Steps


---

*Source: test_adjacency_matrix.py:117 | Complexity: Advanced | Last updated: 2026-05-05*