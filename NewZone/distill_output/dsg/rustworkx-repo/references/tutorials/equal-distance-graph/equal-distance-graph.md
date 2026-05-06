# How To: Equal Distance Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test equal distance graph

## Prerequisites

**Required Modules:**
- `pprint`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign n = 3

```python
n = 3
```

### Step 2: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 3: Call graph.add_nodes_from()

```python
graph.add_nodes_from(range(n + 5))
```

### Step 4: Call graph.add_edges_from()

```python
graph.add_edges_from([(n, n + 1, 0.5), (n, n + 2, 0.5), (n + 1, n + 2, 0.5), (n, n + 3, 0.5), (n + 1, n + 4, 0.5)])
```

### Step 5: Call graph.add_edges_from()

```python
graph.add_edges_from([(i, n + 2, 2) for i in range(n)])
```

### Step 6: Assign terminals = value

```python
terminals = list(range(5)) + [n + 3, n + 4]
```

### Step 7: Assign tree = rustworkx.steiner_tree(...)

```python
tree = rustworkx.steiner_tree(graph, terminals, weight_fn=float)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(rustworkx.cycle_basis(tree), [])
```

### Step 9: Assign expected_edges = value

```python
expected_edges = [(3, 4, 0.5), (4, 5, 0.5), (3, 6, 0.5), (4, 7, 0.5), (0, 5, 2), (1, 5, 2), (2, 5, 2)]
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(tree.weighted_edge_list(), expected_edges)
```


## Complete Example

```python
# Workflow
n = 3
graph = rustworkx.PyGraph()
graph.add_nodes_from(range(n + 5))
graph.add_edges_from([(n, n + 1, 0.5), (n, n + 2, 0.5), (n + 1, n + 2, 0.5), (n, n + 3, 0.5), (n + 1, n + 4, 0.5)])
graph.add_edges_from([(i, n + 2, 2) for i in range(n)])
terminals = list(range(5)) + [n + 3, n + 4]
tree = rustworkx.steiner_tree(graph, terminals, weight_fn=float)
self.assertEqual(rustworkx.cycle_basis(tree), [])
expected_edges = [(3, 4, 0.5), (4, 5, 0.5), (3, 6, 0.5), (4, 7, 0.5), (0, 5, 2), (1, 5, 2), (2, 5, 2)]
self.assertEqual(tree.weighted_edge_list(), expected_edges)
```

## Next Steps


---

*Source: test_steiner_tree.py:160 | Complexity: Advanced | Last updated: 2026-05-05*