# How To: Simple Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test simple graph

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
res = rustworkx.graph_greedy_color(graph)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual({0: 0, 1: 1, 2: 1}, res)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, 1)
res = rustworkx.graph_greedy_color(graph)
self.assertEqual({0: 0, 1: 1, 2: 1}, res)
```

## Next Steps


---

*Source: test_coloring.py:24 | Complexity: Advanced | Last updated: 2026-05-05*