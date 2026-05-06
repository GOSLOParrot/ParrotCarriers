# How To: Greedy Strategies

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test greedy strategies

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.complete_graph(...)

```python
graph = rustworkx.generators.complete_graph(4)
```

### Step 2: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual({0: 0, 1: 1, 2: 2, 3: 2, 4: 1, 5: 0}, edge_colors)
```

### Step 4: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.Degree)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual({0: 0, 1: 1, 2: 2, 3: 2, 4: 1, 5: 0}, edge_colors)
```

### Step 6: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.Saturation)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual({0: 0, 1: 2, 2: 1, 3: 1, 4: 2, 5: 0}, edge_colors)
```

### Step 8: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.IndependentSet)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual({0: 0, 1: 2, 2: 1, 3: 1, 4: 2, 5: 0}, edge_colors)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.complete_graph(4)
with self.subTest():
    edge_colors = rustworkx.graph_greedy_edge_color(graph)
    self.assertEqual({0: 0, 1: 1, 2: 2, 3: 2, 4: 1, 5: 0}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Degree):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.Degree)
    self.assertEqual({0: 0, 1: 1, 2: 2, 3: 2, 4: 1, 5: 0}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Saturation):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.Saturation)
    self.assertEqual({0: 0, 1: 2, 2: 1, 3: 1, 4: 2, 5: 0}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.IndependentSet):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, strategy=rustworkx.ColoringStrategy.IndependentSet)
    self.assertEqual({0: 0, 1: 2, 2: 1, 3: 1, 4: 2, 5: 0}, edge_colors)
```

## Next Steps


---

*Source: test_coloring.py:179 | Complexity: Advanced | Last updated: 2026-05-05*