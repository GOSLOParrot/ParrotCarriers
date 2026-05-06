# How To: Vs Dijkstra All Pairs

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test vs dijkstra all pairs

## Prerequisites

**Required Modules:**
- `unittest`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
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

### Step 5: Assign d = graph.add_node(...)

```python
d = graph.add_node('D')
```

### Step 6: Assign e = graph.add_node(...)

```python
e = graph.add_node('E')
```

### Step 7: Assign f = graph.add_node(...)

```python
f = graph.add_node('F')
```

### Step 8: Assign edge_list = value

```python
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
```

### Step 9: Call graph.add_edges_from()

```python
graph.add_edges_from(edge_list)
```

### Step 10: Assign dijkstra_lengths = rustworkx.graph_all_pairs_dijkstra_path_lengths(...)

```python
dijkstra_lengths = rustworkx.graph_all_pairs_dijkstra_path_lengths(graph, float)
```

### Step 11: Assign expected = value

```python
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
```

### Step 12: Assign result = rustworkx.graph_floyd_warshall(...)

```python
result = rustworkx.graph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual(result, expected)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
d = graph.add_node('D')
e = graph.add_node('E')
f = graph.add_node('F')
edge_list = [(a, b, 7), (c, a, 9), (a, d, 14), (b, c, 10), (d, c, 2), (d, e, 9), (b, f, 15), (c, f, 11), (e, f, 6)]
graph.add_edges_from(edge_list)
dijkstra_lengths = rustworkx.graph_all_pairs_dijkstra_path_lengths(graph, float)
expected = {k: {**v, k: 0.0} for k, v in dijkstra_lengths.items()}
result = rustworkx.graph_floyd_warshall(graph, float, parallel_threshold=self.parallel_threshold)
self.assertEqual(result, expected)
```

## Next Steps


---

*Source: test_floyd_warshall.py:23 | Complexity: Advanced | Last updated: 2026-05-05*