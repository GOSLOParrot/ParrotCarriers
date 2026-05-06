# How To: Hits

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test hits

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign edges = value

```python
edges = [(0, 2), (0, 4), (1, 0), (2, 4), (4, 3), (4, 2), (5, 4)]
```

### Step 2: Assign rx_graph = rustworkx.PyDiGraph(...)

```python
rx_graph = rustworkx.PyDiGraph()
```

### Step 3: Call rx_graph.extend_from_edge_list()

```python
rx_graph.extend_from_edge_list(edges)
```

### Step 4: Assign nx_graph = nx.DiGraph(...)

```python
nx_graph = nx.DiGraph()
```

### Step 5: Call nx_graph.add_edges_from()

```python
nx_graph.add_edges_from(edges)
```

### Step 6: Assign unknown = rustworkx.hits(...)

```python
rx_h, rx_a = rustworkx.hits(rx_graph)
```

### Step 7: Assign unknown = hits_python(...)

```python
nx_h, nx_a = hits_python(nx_graph)
```

### Step 8: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(rx_h[v], nx_h[v], delta=0.0001)
```

### Step 9: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(rx_a[v], nx_a[v], delta=0.0001)
```


## Complete Example

```python
# Workflow
edges = [(0, 2), (0, 4), (1, 0), (2, 4), (4, 3), (4, 2), (5, 4)]
rx_graph = rustworkx.PyDiGraph()
rx_graph.extend_from_edge_list(edges)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(edges)
rx_h, rx_a = rustworkx.hits(rx_graph)
nx_h, nx_a = hits_python(nx_graph)
for v in rx_graph.node_indices():
    self.assertAlmostEqual(rx_h[v], nx_h[v], delta=0.0001)
    self.assertAlmostEqual(rx_a[v], nx_a[v], delta=0.0001)
```

## Next Steps


---

*Source: test_hits.py:108 | Complexity: Advanced | Last updated: 2026-05-05*