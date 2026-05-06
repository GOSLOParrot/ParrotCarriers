# How To: No Weight Fn

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test no weight fn

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
graph.add_edge(node_a, node_b, 'edge_a')
```

### Step 5: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_b, node_c, 'edge_b')
```

### Step 7: Assign res = rustworkx.graph_adjacency_matrix(...)

```python
res = rustworkx.graph_adjacency_matrix(graph)
```

### Step 8: Call self.assertIsInstance()

```python
self.assertIsInstance(res, np.ndarray)
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(np.array_equal(np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64), res))
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'edge_a')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'edge_b')
res = rustworkx.graph_adjacency_matrix(graph)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.float64), res))
```

## Next Steps


---

*Source: test_adjacency_matrix.py:39 | Complexity: Advanced | Last updated: 2026-05-05*