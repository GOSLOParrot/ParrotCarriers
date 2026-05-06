# How To: With Dangling Node

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test with dangling node

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign edges = value

```python
edges = [(0, 1), (0, 2), (2, 0), (2, 1), (2, 4), (3, 4), (3, 5), (4, 3), (4, 5), (5, 4)]
```

### Step 2: Assign rx_graph = rustworkx.PyDiGraph(...)

```python
rx_graph = rustworkx.PyDiGraph()
```

### Step 3: Assign nx_graph = nx.DiGraph(...)

```python
nx_graph = nx.DiGraph()
```

### Step 4: Call rx_graph.extend_from_edge_list()

```python
rx_graph.extend_from_edge_list(edges)
```

### Step 5: Call nx_graph.add_edges_from()

```python
nx_graph.add_edges_from(edges)
```

### Step 6: Assign alpha = 0.9

```python
alpha = 0.9
```

### Step 7: Assign tol = 1e-08

```python
tol = 1e-08
```

### Step 8: Assign rx_ranks = rustworkx.pagerank(...)

```python
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, tol=tol)
```

### Step 9: Assign nx_ranks = pagerank_python(...)

```python
nx_ranks = pagerank_python(nx_graph, alpha=alpha, tol=tol)
```

### Step 10: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```


## Complete Example

```python
# Workflow
edges = [(0, 1), (0, 2), (2, 0), (2, 1), (2, 4), (3, 4), (3, 5), (4, 3), (4, 5), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
nx_graph = nx.DiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph.add_edges_from(edges)
alpha = 0.9
tol = 1e-08
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha, tol=tol)
nx_ranks = pagerank_python(nx_graph, alpha=alpha, tol=tol)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

## Next Steps


---

*Source: test_pagerank.py:119 | Complexity: Advanced | Last updated: 2026-05-05*