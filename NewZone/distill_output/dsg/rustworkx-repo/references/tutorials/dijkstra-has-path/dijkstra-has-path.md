# How To: Dijkstra Has Path

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test dijkstra has path

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

### Step 4: Assign c = g.add_node(...)

```python
c = g.add_node('C')
```

### Step 5: Assign edge_list = value

```python
edge_list = [(a, b, 7), (c, b, 9), (c, b, 10)]
```

### Step 6: Call g.add_edges_from()

```python
g.add_edges_from(edge_list)
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(rustworkx.graph_has_path(g, a, c))
```


## Complete Example

```python
# Workflow
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
edge_list = [(a, b, 7), (c, b, 9), (c, b, 10)]
g.add_edges_from(edge_list)
self.assertTrue(rustworkx.graph_has_path(g, a, c))
```

## Next Steps


---

*Source: test_dijkstra.py:53 | Complexity: Intermediate | Last updated: 2026-05-05*