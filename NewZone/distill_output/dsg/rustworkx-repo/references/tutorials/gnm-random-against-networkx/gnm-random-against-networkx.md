# How To: Gnm Random Against Networkx

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test gnm random against networkx

## Prerequisites

**Required Modules:**
- `random`
- `unittest`
- `networkx`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign rx_graph = rustworkx.undirected_gnm_random_graph(...)

```python
rx_graph = rustworkx.undirected_gnm_random_graph(10, 13, seed=42)
```

### Step 2: Assign nx_graph = networkx.Graph(...)

```python
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
```

### Step 3: Assign nx_matches = networkx.max_weight_matching(...)

```python
nx_matches = networkx.max_weight_matching(nx_graph)
```

### Step 4: Assign rx_matches = rustworkx.max_weight_matching(...)

```python
rx_matches = rustworkx.max_weight_matching(rx_graph, verify_optimum=True)
```

### Step 5: Call self.compare_rx_nx_sets()

```python
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 42, nx_graph)
```


## Complete Example

```python
# Workflow
rx_graph = rustworkx.undirected_gnm_random_graph(10, 13, seed=42)
nx_graph = networkx.Graph(list(rx_graph.edge_list()))
nx_matches = networkx.max_weight_matching(nx_graph)
rx_matches = rustworkx.max_weight_matching(rx_graph, verify_optimum=True)
self.compare_rx_nx_sets(rx_graph, rx_matches, nx_matches, 42, nx_graph)
```

## Next Steps


---

*Source: test_max_weight_matching.py:586 | Complexity: Intermediate | Last updated: 2026-05-05*