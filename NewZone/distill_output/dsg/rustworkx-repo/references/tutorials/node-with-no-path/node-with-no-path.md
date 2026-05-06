# How To: Node With No Path

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test node with no path

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.path_graph(...)

```python
graph = rustworkx.generators.path_graph(5)
```

### Step 2: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list([(6, 7), (7, 8), (8, 9), (9, 10), (10, 11)])
```

### Step 3: Assign expected = value

```python
expected = {1: 1, 2: 1, 3: 1, 4: 1}
```

### Step 4: Assign res = rustworkx.num_shortest_paths_unweighted(...)

```python
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(expected, res)
```

### Step 6: Assign res = rustworkx.num_shortest_paths_unweighted(...)

```python
res = rustworkx.num_shortest_paths_unweighted(graph, 6)
```

### Step 7: Assign expected = value

```python
expected = {7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(expected, res)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.path_graph(5)
graph.extend_from_edge_list([(6, 7), (7, 8), (8, 9), (9, 10), (10, 11)])
expected = {1: 1, 2: 1, 3: 1, 4: 1}
res = rustworkx.num_shortest_paths_unweighted(graph, 0)
self.assertEqual(expected, res)
res = rustworkx.num_shortest_paths_unweighted(graph, 6)
expected = {7: 1, 8: 1, 9: 1, 10: 1, 11: 1}
self.assertEqual(expected, res)
```

## Next Steps


---

*Source: test_num_shortest_path.py:95 | Complexity: Advanced | Last updated: 2026-05-05*