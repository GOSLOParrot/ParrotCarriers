# How To: Dijkstra With Disconnected Nodes

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test dijkstra with disconnected nodes

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

### Step 4: Call g.add_edge()

```python
g.add_edge(a, b, 1.2)
```

### Step 5: Call g.add_node()

```python
g.add_node('C')
```

### Step 6: Assign d = g.add_node(...)

```python
d = g.add_node('D')
```

### Step 7: Call g.add_edge()

```python
g.add_edge(b, d, 2.4)
```

### Step 8: Assign path = rustworkx.graph_dijkstra_shortest_path_lengths(...)

```python
path = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, lambda x: round(x, 1))
```

### Step 9: Assign expected = value

```python
expected = {1: 1.2, 3: 3.5999999999999996}
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(expected, path)
```


## Complete Example

```python
# Workflow
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
g.add_edge(a, b, 1.2)
g.add_node('C')
d = g.add_node('D')
g.add_edge(b, d, 2.4)
path = rustworkx.graph_dijkstra_shortest_path_lengths(g, a, lambda x: round(x, 1))
expected = {1: 1.2, 3: 3.5999999999999996}
self.assertEqual(expected, path)
```

## Next Steps


---

*Source: test_dijkstra.py:110 | Complexity: Advanced | Last updated: 2026-05-05*