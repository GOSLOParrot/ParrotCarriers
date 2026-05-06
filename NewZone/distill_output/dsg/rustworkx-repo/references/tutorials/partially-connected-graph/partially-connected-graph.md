# How To: Partially Connected Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test partially connected graph

## Prerequisites

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_cycle_graph(...)

```python
graph = rustworkx.generators.directed_cycle_graph(32)
```

### Step 2: Call graph.add_nodes_from()

```python
graph.add_nodes_from(list(range(32)))
```

### Step 3: Assign res = rustworkx.unweighted_average_shortest_path_length(...)

```python
res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
```

### Step 4: Call self.assertTrue()

```python
self.assertTrue(math.isinf(res), 'Output is not infinity')
```

### Step 5: Assign s = 8192

```python
s = 8192
```

### Step 6: Assign den = 992

```python
den = 992
```

### Step 7: Assign res = rustworkx.unweighted_average_shortest_path_length(...)

```python
res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True, disconnected=True)
```

### Step 8: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(s / den, res, delta=1e-07)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_cycle_graph(32)
graph.add_nodes_from(list(range(32)))
with self.subTest(disconnected=False):
    res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True)
    self.assertTrue(math.isinf(res), 'Output is not infinity')
with self.subTest(disconnected=True):
    s = 8192
    den = 992
    res = rustworkx.unweighted_average_shortest_path_length(graph, as_undirected=True, disconnected=True)
    self.assertAlmostEqual(s / den, res, delta=1e-07)
```

## Next Steps


---

*Source: test_avg_shortest_path.py:149 | Complexity: Advanced | Last updated: 2026-05-05*