# How To: Simple Graph With Preset

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test simple graph with preset

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


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
graph.add_edge(node_a, node_b, 1)
```

### Step 5: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_a, node_c, 1)
```

### Step 7: Assign res = rustworkx.graph_greedy_color(...)

```python
res = rustworkx.graph_greedy_color(graph, preset)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual({0: 1, 1: 0, 2: 0}, res)
```


## Complete Example

```python
# Workflow
def preset(node_idx):
    if node_idx == 0:
        return 1
    return None
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
res = rustworkx.graph_greedy_color(graph, preset)
self.assertEqual({0: 1, 1: 0, 2: 0}, res)
```

## Next Steps


---

*Source: test_coloring.py:48 | Complexity: Advanced | Last updated: 2026-05-05*