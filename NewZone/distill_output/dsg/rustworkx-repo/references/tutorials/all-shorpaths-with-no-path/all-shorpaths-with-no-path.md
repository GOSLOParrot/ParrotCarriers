# How To: All Shorpaths With No Path

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test all shortest paths with no path

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

### Step 4: Assign paths = rustworkx.graph_all_shortest_paths(...)

```python
paths = rustworkx.graph_all_shortest_paths(g, a, b, lambda x: float(x))
```

### Step 5: Assign expected = value

```python
expected = []
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(expected, paths)
```


## Complete Example

```python
# Workflow
g = rustworkx.PyGraph()
a = g.add_node('A')
b = g.add_node('B')
paths = rustworkx.graph_all_shortest_paths(g, a, b, lambda x: float(x))
expected = []
self.assertEqual(expected, paths)
```

## Next Steps


---

*Source: test_all_shortest_paths.py:55 | Complexity: Intermediate | Last updated: 2026-05-05*