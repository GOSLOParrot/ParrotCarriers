# How To: Bellman Ford Length With No Path And Goal

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test bellman ford length with no path and goal

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign g = rustworkx.PyGraph(...)

```python
g = rustworkx.PyGraph()
```

### Step 2: Assign a = g.add_node(...)

```python
a = g.add_node('A')
```

### Step 3: Assign b = g.add_node(...)

```python
b = g.add_node('B')
```

### Step 4: Assign path_lengths = rustworkx.graph_bellman_ford_shortest_path_lengths(...)

```python
path_lengths = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
```

### Step 5: Assign expected = rustworkx.graph_dijkstra_shortest_path_lengths(...)

```python
expected = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(expected, path_lengths)
```


## Complete Example

```python
# Workflow
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
path_lengths = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
expected = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, edge_cost_fn=float, goal=b)
self.assertEqual(expected, path_lengths)
```

## Next Steps


---

*Source: test_bellman_ford.py:80 | Complexity: Intermediate | Last updated: 2026-05-05*