# How To: Beta Scalar

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test beta scalar

## Prerequisites

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign rx_graph = rustworkx.generators.directed_grid_graph(...)

```python
rx_graph = rustworkx.generators.directed_grid_graph(5, 2)
```

### Step 2: Assign beta = 0.3

```python
beta = 0.3
```

### Step 3: Assign rx_centrality = rustworkx.katz_centrality(...)

```python
rx_centrality = rustworkx.katz_centrality(rx_graph, alpha=0.25, beta=beta)
```

### Step 4: Assign nx_graph = nx.DiGraph(...)

```python
nx_graph = nx.DiGraph()
```

### Step 5: Call nx_graph.add_edges_from()

```python
nx_graph.add_edges_from(rx_graph.edge_list())
```

### Step 6: Assign nx_centrality = nx.katz_centrality(...)

```python
nx_centrality = nx.katz_centrality(nx_graph, alpha=0.25, beta=beta)
```

### Step 7: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(rx_centrality[key], nx_centrality[key], delta=0.0001)
```


## Complete Example

```python
# Workflow
rx_graph = rustworkx.generators.directed_grid_graph(5, 2)
beta = 0.3
rx_centrality = rustworkx.katz_centrality(rx_graph, alpha=0.25, beta=beta)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(rx_graph.edge_list())
nx_centrality = nx.katz_centrality(nx_graph, alpha=0.25, beta=beta)
for key in rx_centrality.keys():
    self.assertAlmostEqual(rx_centrality[key], nx_centrality[key], delta=0.0001)
```

## Next Steps


---

*Source: test_centrality.py:195 | Complexity: Intermediate | Last updated: 2026-05-05*