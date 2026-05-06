# How To: Multi Graph 4

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test multi graph 4

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
graph_2 = rustworkx.generators.directed_path_graph(2)
```

### Step 3: Call graph_2.add_edge()

```python
graph_2.add_edge(0, 0, None)
```

### Step 4: Assign unknown = rustworkx.digraph_tensor_product(...)

```python
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
```

### Step 5: Assign expected_edges = value

```python
expected_edges = [(0, 3), (0, 2)]
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(graph_product.num_edges(), 2)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(graph_product.edge_list(), expected_edges)
```


## Complete Example

```python
# Workflow
graph_1 = rustworkx.generators.directed_path_graph(2)
graph_2 = rustworkx.generators.directed_path_graph(2)
graph_2.add_edge(0, 0, None)
graph_product, _ = rustworkx.digraph_tensor_product(graph_1, graph_2)
expected_edges = [(0, 3), (0, 2)]
self.assertEqual(graph_product.num_edges(), 2)
self.assertEqual(graph_product.edge_list(), expected_edges)
```

## Next Steps


---

*Source: test_tensor_product.py:102 | Complexity: Intermediate | Last updated: 2026-05-05*