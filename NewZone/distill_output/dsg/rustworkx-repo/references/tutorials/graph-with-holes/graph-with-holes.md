# How To: Graph With Holes

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Graph with missing node and edge indices.

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: 'Graph with missing node and edge indices.'

```python
'Graph with missing node and edge indices.'
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

### Step 5: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 6: Assign node_d = graph.add_node(...)

```python
node_d = graph.add_node('d')
```

### Step 7: Assign node_e = graph.add_node(...)

```python
node_e = graph.add_node('e')
```

### Step 8: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, 1)
```

### Step 9: Call graph.add_edge()

```python
graph.add_edge(node_b, node_c, 1)
```

### Step 10: Call graph.add_edge()

```python
graph.add_edge(node_c, node_d, 1)
```

### Step 11: Call graph.add_edge()

```python
graph.add_edge(node_d, node_e, 1)
```

### Step 12: Call graph.remove_node()

```python
graph.remove_node(node_c)
```

### Step 13: Assign edge_colors = rustworkx.graph_greedy_edge_color(...)

```python
edge_colors = rustworkx.graph_greedy_edge_color(graph)
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual({0: 0, 3: 0}, edge_colors)
```


## Complete Example

```python
# Workflow
'Graph with missing node and edge indices.'
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
node_c = graph.add_node('c')
node_d = graph.add_node('d')
node_e = graph.add_node('e')
graph.add_edge(node_a, node_b, 1)
graph.add_edge(node_b, node_c, 1)
graph.add_edge(node_c, node_d, 1)
graph.add_edge(node_d, node_e, 1)
graph.remove_node(node_c)
edge_colors = rustworkx.graph_greedy_edge_color(graph)
self.assertEqual({0: 0, 3: 0}, edge_colors)
```

## Next Steps


---

*Source: test_coloring.py:135 | Complexity: Advanced | Last updated: 2026-05-05*