# How To: Another Trivial Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test another trivial graph

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Assign a = graph.add_node(...)

```python
a = graph.add_node(0)
```

### Step 3: Assign b = graph.add_node(...)

```python
b = graph.add_node(1)
```

### Step 4: Assign c = graph.add_node(...)

```python
c = graph.add_node(2)
```

### Step 5: Call graph.add_edge()

```python
graph.add_edge(a, b, None)
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(b, c, None)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(rustworkx.articulation_points(graph), {1})
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
a = graph.add_node(0)
b = graph.add_node(1)
c = graph.add_node(2)
graph.add_edge(a, b, None)
graph.add_edge(b, c, None)
self.assertEqual(rustworkx.articulation_points(graph), {1})
self.assertEqual(sorted_edges(rustworkx.bridges(graph)), {(0, 1), (1, 2)})
```

## Next Steps


---

*Source: test_biconnected.py:74 | Complexity: Advanced | Last updated: 2026-05-05*