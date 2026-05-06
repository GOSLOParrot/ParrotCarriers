# How To: Greedy Strategies With Preset

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test greedy strategies with preset

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
edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
```

### Step 4: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.Degree)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
```

### Step 6: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.Saturation)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
```

### Step 8: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.IndependentSet)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
```


## Complete Example

```python
# Workflow
def preset(edge_idx):
    if edge_idx == 0:
        return 1
    elif edge_idx == 3:
        return 0
    else:
        return None
graph = rustworkx.generators.complete_graph(4)
with self.subTest():
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Degree):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.Degree)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.Saturation):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.Saturation)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
with self.subTest(strategy=rustworkx.ColoringStrategy.IndependentSet):
    edge_colors = rustworkx.graph_greedy_edge_color(graph, preset_color_fn=preset, strategy=rustworkx.ColoringStrategy.IndependentSet)
    self.assertEqual({0: 1, 1: 2, 2: 0, 3: 0, 4: 2, 5: 1}, edge_colors)
```

## Next Steps


---

*Source: test_coloring.py:204 | Complexity: Advanced | Last updated: 2026-05-05*