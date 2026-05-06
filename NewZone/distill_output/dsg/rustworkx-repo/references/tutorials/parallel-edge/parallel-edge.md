# How To: Parallel Edge

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test parallel edge

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Assign a = graph.add_node(...)

```python
a = graph.add_node('A')
```

### Step 3: Assign b = graph.add_node(...)

```python
b = graph.add_node('B')
```

### Step 4: Assign c = graph.add_node(...)

```python
c = graph.add_node('C')
```

### Step 5: Call graph.add_edges_from()

```python
graph.add_edges_from([(a, b, 3.0), (a, b, 1.0), (a, c, 2.0), (b, c, 7.0), (c, a, 1.0), (b, c, 2.0), (a, b, 4.0)])
```

### Step 6: Assign min_matrix = rustworkx.digraph_adjacency_matrix(...)

```python
min_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='min')
```

### Step 7: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal([[0.0, 1.0, 2.0], [0.0, 0.0, 2.0], [1.0, 0.0, 0.0]], min_matrix)
```

### Step 8: Assign max_matrix = rustworkx.digraph_adjacency_matrix(...)

```python
max_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='max')
```

### Step 9: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal([[0.0, 4.0, 2.0], [0.0, 0.0, 7.0], [1.0, 0.0, 0.0]], max_matrix)
```

### Step 10: Assign avg_matrix = rustworkx.digraph_adjacency_matrix(...)

```python
avg_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='avg')
```

### Step 11: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal([[0.0, 8 / 3.0, 2.0], [0.0, 0.0, 4.5], [1.0, 0.0, 0.0]], avg_matrix)
```

### Step 12: Assign sum_matrix = rustworkx.digraph_adjacency_matrix(...)

```python
sum_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='sum')
```

### Step 13: Call np.testing.assert_array_equal()

```python
np.testing.assert_array_equal([[0.0, 8.0, 2.0], [0.0, 0.0, 9.0], [1.0, 0.0, 0.0]], sum_matrix)
```

### Step 14: Call rustworkx.digraph_adjacency_matrix()

```python
rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='error')
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
graph.add_edges_from([(a, b, 3.0), (a, b, 1.0), (a, c, 2.0), (b, c, 7.0), (c, a, 1.0), (b, c, 2.0), (a, b, 4.0)])
min_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='min')
np.testing.assert_array_equal([[0.0, 1.0, 2.0], [0.0, 0.0, 2.0], [1.0, 0.0, 0.0]], min_matrix)
max_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='max')
np.testing.assert_array_equal([[0.0, 4.0, 2.0], [0.0, 0.0, 7.0], [1.0, 0.0, 0.0]], max_matrix)
avg_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='avg')
np.testing.assert_array_equal([[0.0, 8 / 3.0, 2.0], [0.0, 0.0, 4.5], [1.0, 0.0, 0.0]], avg_matrix)
sum_matrix = rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='sum')
np.testing.assert_array_equal([[0.0, 8.0, 2.0], [0.0, 0.0, 9.0], [1.0, 0.0, 0.0]], sum_matrix)
with self.assertRaises(ValueError):
    rustworkx.digraph_adjacency_matrix(graph, weight_fn=lambda x: float(x), parallel_edge='error')
```

## Next Steps


---

*Source: test_adjacency_matrix.py:266 | Complexity: Advanced | Last updated: 2026-05-05*