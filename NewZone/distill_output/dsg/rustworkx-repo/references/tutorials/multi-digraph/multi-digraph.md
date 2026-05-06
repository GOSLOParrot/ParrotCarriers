# How To: Multi Digraph

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test multi digraph

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign rx_graph = rustworkx.PyDiGraph(...)

```python
rx_graph = rustworkx.PyDiGraph()
```

### Step 2: Call rx_graph.extend_from_edge_list()

```python
rx_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
```

### Step 3: Assign nx_graph = nx.MultiDiGraph(...)

```python
nx_graph = nx.MultiDiGraph(list(rx_graph.edge_list()))
```

### Step 4: Assign alpha = 0.9

```python
alpha = 0.9
```

### Step 5: Assign rx_ranks = rustworkx.pagerank(...)

```python
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha)
```

### Step 6: Assign nx_ranks = pagerank_python(...)

```python
nx_ranks = pagerank_python(nx_graph, alpha=alpha)
```

### Step 7: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```


## Complete Example

```python
# Workflow
rx_graph = rustworkx.PyDiGraph()
rx_graph.extend_from_edge_list([(0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (1, 2), (2, 1), (1, 2), (2, 1), (2, 3), (3, 2), (2, 3), (3, 2)])
nx_graph = nx.MultiDiGraph(list(rx_graph.edge_list()))
alpha = 0.9
rx_ranks = rustworkx.pagerank(rx_graph, alpha=alpha)
nx_ranks = pagerank_python(nx_graph, alpha=alpha)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_ranks[v], nx_ranks[v], delta=0.0001)
```

## Next Steps


---

*Source: test_pagerank.py:258 | Complexity: Intermediate | Last updated: 2026-05-05*