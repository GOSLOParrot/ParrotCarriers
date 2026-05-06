# How To: Multigraph Sum Cast Weight Func Non Zero Null

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test multigraph sum cast weight func non zero null

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
graph.add_edge(node_a, node_b, 7.0)
```

### Step 5: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 0.5)
```

### Step 6: Assign res = rustworkx.graph_adjacency_matrix(...)

```python
res = rustworkx.graph_adjacency_matrix(graph, lambda x: float(x), null_value=np.inf)
```

### Step 7: Call self.assertIsInstance()

```python
self.assertIsInstance(res, np.ndarray)
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [7.5, np.inf]]), res))
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 7.0)
graph.add_edge(node_a, node_b, 0.5)
res = rustworkx.graph_adjacency_matrix(graph, lambda x: float(x), null_value=np.inf)
self.assertIsInstance(res, np.ndarray)
self.assertTrue(np.array_equal(np.array([[np.inf, 7.5], [7.5, np.inf]]), res))
```

## Next Steps


---

*Source: test_adjacency_matrix.py:96 | Complexity: Advanced | Last updated: 2026-05-05*