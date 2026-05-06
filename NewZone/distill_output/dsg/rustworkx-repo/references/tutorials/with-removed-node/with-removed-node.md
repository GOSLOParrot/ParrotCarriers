# How To: With Removed Node

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test with removed node

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Assign edges = value

```python
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (0, 4)]
```

### Step 3: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list(edges)
```

### Step 4: Call graph.remove_node()

```python
graph.remove_node(3)
```

### Step 5: Assign ranks = rustworkx.pagerank(...)

```python
ranks = rustworkx.pagerank(graph)
```

### Step 6: Assign expected_ranks = value

```python
expected_ranks = {0: 0.17401467654615052, 1: 0.2479710438690554, 2: 0.3847906219106203, 4: 0.19322365767417365}
```

### Step 7: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(ranks[v], expected_ranks[v], delta=0.0001)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (0, 4)]
graph.extend_from_edge_list(edges)
graph.remove_node(3)
ranks = rustworkx.pagerank(graph)
expected_ranks = {0: 0.17401467654615052, 1: 0.2479710438690554, 2: 0.3847906219106203, 4: 0.19322365767417365}
for v in graph.node_indices():
    self.assertAlmostEqual(ranks[v], expected_ranks[v], delta=0.0001)
```

## Next Steps


---

*Source: test_pagerank.py:197 | Complexity: Intermediate | Last updated: 2026-05-05*