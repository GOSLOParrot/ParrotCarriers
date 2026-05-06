# How To: Graph Multiple Edges

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Graph with multiple edges between two nodes.

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: 'Graph with multiple edges between two nodes.'

```python
'Graph with multiple edges between two nodes.'
```

### Step 2: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 3: Assign node_a = graph.add_node(...)

```python
node_a = graph.add_node('a')
```

### Step 4: Assign node_b = graph.add_node(...)

```python
node_b = graph.add_node('b')
```

### Step 5: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 1)
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 1)
```

### Step 7: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 1)
```

### Step 8: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 1)
```

### Step 9: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual({0: 0, 1: 1, 2: 2, 3: 3}, edge_colors)
```


## Complete Example

```python
# Workflow
'Graph with multiple edges between two nodes.'
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_a, node_b, 1)
edge_colors = rustworkx.graph_greedy_edge_color(graph)
self.assertEqual({0: 0, 1: 1, 2: 2, 3: 3}, edge_colors)
```

## Next Steps


---

*Source: test_coloring.py:162 | Complexity: Advanced | Last updated: 2026-05-05*