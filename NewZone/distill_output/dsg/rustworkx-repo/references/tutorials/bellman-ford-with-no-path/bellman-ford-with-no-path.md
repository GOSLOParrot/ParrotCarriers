# How To: Bellman Ford With No Path

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test bellman ford with no path

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

### Step 3: Call g.add_node()

```python
g.add_node('B')
```

### Step 4: Assign path = rustworkx.graph_bellman_ford_shortest_path_lengths(...)

```python
path = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, lambda x: float(x))
```

### Step 5: Assign expected = value

```python
expected = {}
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(expected, path)
```


## Complete Example

```python
# Workflow
g = rustworkx.PyGraph()
a = g.add_node('A')
g.add_node('B')
path = rustworkx.graph_bellman_ford_shortest_path_lengths(g, a, lambda x: float(x))
expected = {}
self.assertEqual(expected, path)
```

## Next Steps


---

*Source: test_bellman_ford.py:109 | Complexity: Intermediate | Last updated: 2026-05-05*