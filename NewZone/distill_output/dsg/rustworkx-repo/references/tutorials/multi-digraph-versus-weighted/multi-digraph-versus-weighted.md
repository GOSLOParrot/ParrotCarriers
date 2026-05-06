# How To: Multi Digraph Versus Weighted

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test multi digraph versus weighted

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign multi_graph = rustworkx.PyDiGraph(...)

```python
multi_graph = rustworkx.PyDiGraph()
```

### Step 2: Call multi_graph.extend_from_edge_list()

```python
multi_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
```

### Step 3: Assign weighted_graph = rustworkx.PyDiGraph(...)

```python
weighted_graph = rustworkx.PyDiGraph()
```

### Step 4: Call weighted_graph.extend_from_weighted_edge_list()

```python
weighted_graph.extend_from_weighted_edge_list([(0, 1, 3), (1, 0, 3), (1, 2, 2), (2, 1, 2), (2, 3, 2), (3, 2, 2)])
```

### Step 5: Assign alpha = 0.85

```python
alpha = 0.85
```

### Step 6: Assign ranks_multi = rustworkx.pagerank(...)

```python
ranks_multi = rustworkx.pagerank(multi_graph, alpha=alpha, weight_fn=lambda _: 1.0)
```

### Step 7: Assign ranks_weight = rustworkx.pagerank(...)

```python
ranks_weight = rustworkx.pagerank(weighted_graph, alpha=alpha, weight_fn=float)
```

### Step 8: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(ranks_multi[v], ranks_weight[v], delta=0.0001)
```


## Complete Example

```python
# Workflow
multi_graph = rustworkx.PyDiGraph()
multi_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
weighted_graph = rustworkx.PyDiGraph()
weighted_graph.extend_from_weighted_edge_list([(0, 1, 3), (1, 0, 3), (1, 2, 2), (2, 1, 2), (2, 3, 2), (3, 2, 2)])
alpha = 0.85
ranks_multi = rustworkx.pagerank(multi_graph, alpha=alpha, weight_fn=lambda _: 1.0)
ranks_weight = rustworkx.pagerank(weighted_graph, alpha=alpha, weight_fn=float)
for v in multi_graph.node_indices():
    self.assertAlmostEqual(ranks_multi[v], ranks_weight[v], delta=0.0001)
```

## Next Steps


---

*Source: test_pagerank.py:292 | Complexity: Advanced | Last updated: 2026-05-05*