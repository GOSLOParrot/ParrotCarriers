# How To: Transitivity Fulltriangle Directed

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test transitivity fulltriangle directed

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Call graph.add_nodes_from()

```python
graph.add_nodes_from(list(range(3)))
```

### Step 3: Call graph.add_edges_from_no_data()

```python
graph.add_edges_from_no_data([(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)])
```

### Step 4: Assign res = rustworkx.transitivity(...)

```python
res = rustworkx.transitivity(graph)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(res, 1.0)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
graph.add_nodes_from(list(range(3)))
graph.add_edges_from_no_data([(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)])
res = rustworkx.transitivity(graph)
self.assertEqual(res, 1.0)
```

## Next Steps


---

*Source: test_transitivity.py:33 | Complexity: Intermediate | Last updated: 2026-05-05*