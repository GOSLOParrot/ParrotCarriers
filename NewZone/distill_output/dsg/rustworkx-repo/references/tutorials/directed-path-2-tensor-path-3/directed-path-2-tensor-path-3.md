# How To: Directed Path 2 Tensor Path 3

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test directed path 2 tensor path 3

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_1 = rustworkx.generators.directed_path_graph(...)

```python
graph_1 = rustworkx.generators.directed_path_graph(2)
```

### Step 2: Assign graph_2 = rustworkx.generators.directed_path_graph(...)

```python
graph_2 = rustworkx.generators.directed_path_graph(3)
```

### Step 3: Assign unknown = rustworkx.digraph_tensor_product(...)

```python
graph_product, node_map = rustworkx.digraph_tensor_product(graph_1, graph_2)
```

### Step 4: Assign expected_node_map = value

```python
expected_node_map = {(0, 1): 1, (1, 0): 3, (0, 0): 0, (1, 2): 5, (0, 2): 2, (1, 1): 4}
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(dict(node_map), expected_node_map)
```

### Step 6: Assign expected_edges = value

```python
expected_edges = [(0, 4), (1, 5)]
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(graph_product.num_nodes(), 6)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(graph_product.num_edges(), 2)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(graph_product.edge_list(), expected_edges)
```


## Complete Example

```python
# Workflow
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(3)
graph_product, node_map = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_node_map = {(0, 1): 1, (1, 0): 3, (0, 0): 0, (1, 2): 5, (0, 2): 2, (1, 1): 4}
self.assertEqual(dict(node_map), expected_node_map)
expected_edges = [(0, 4), (1, 5)]
self.assertEqual(graph_product.num_nodes(), 6)
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

## Next Steps


---

*Source: test_tensor_product.py:39 | Complexity: Advanced | Last updated: 2026-05-05*