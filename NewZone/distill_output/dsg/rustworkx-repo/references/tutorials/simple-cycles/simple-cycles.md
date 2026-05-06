# How To: Simple Cycles

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test simple cycles

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign edges = value

```python
edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
```

### Step 2: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 3: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list(edges)
```

### Step 4: Assign expected = value

```python
expected = [[0], [0, 1, 2], [0, 2], [1, 2], [2]]
```

### Step 5: Assign res = list(...)

```python
res = list(rustworkx.simple_cycles(graph))
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(len(res), len(expected))
```

### Step 7: Call self.assertIn()

```python
self.assertIn(sorted(cycle), expected)
```


## Complete Example

```python
# Workflow
edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
graph = rustworkx.PyDiGraph()
graph.extend_from_edge_list(edges)
expected = [[0], [0, 1, 2], [0, 2], [1, 2], [2]]
res = list(rustworkx.simple_cycles(graph))
self.assertEqual(len(res), len(expected))
for cycle in res:
    self.assertIn(sorted(cycle), expected)
```

## Next Steps


---

*Source: test_simple_cycles.py:19 | Complexity: Intermediate | Last updated: 2026-05-05*