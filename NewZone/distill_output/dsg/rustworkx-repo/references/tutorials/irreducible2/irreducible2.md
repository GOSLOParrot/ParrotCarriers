# How To: Irreducible2

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).
https://hdl.handle.net/1911/96345

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: '\n        Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '

```python
'\n        Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
```

### Step 2: Assign edges = value

```python
edges = [(1, 2), (2, 1), (2, 3), (3, 2), (4, 2), (4, 3), (5, 1), (6, 4), (6, 5)]
```

### Step 3: Assign graph = rx.PyDiGraph(...)

```python
graph = rx.PyDiGraph()
```

### Step 4: Call graph.add_node()

```python
graph.add_node(0)
```

### Step 5: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list(edges)
```

### Step 6: Assign result = rx.dominance_frontiers(...)

```python
result = rx.dominance_frontiers(graph, 6)
```

### Step 7: Call self.assertDictEqual()

```python
self.assertDictEqual(result, {1: {2}, 2: {1, 3}, 3: {2}, 4: {2, 3}, 5: {1}, 6: set()})
```

### Step 8: Assign nx_graph = nx.DiGraph(...)

```python
nx_graph = nx.DiGraph()
```

### Step 9: Call nx_graph.add_edges_from()

```python
nx_graph.add_edges_from(graph.edge_list())
```

### Step 10: Call self.assertDictEqual()

```python
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 6), result)
```


## Complete Example

```python
# Workflow
'\n        Graph taken from figure 4 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
edges = [(1, 2), (2, 1), (2, 3), (3, 2), (4, 2), (4, 3), (5, 1), (6, 4), (6, 5)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.dominance_frontiers(graph, 6)
self.assertDictEqual(result, {1: {2}, 2: {1, 3}, 3: {2}, 4: {2, 3}, 5: {1}, 6: set()})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 6), result)
```

## Next Steps


---

*Source: test_dominance.py:211 | Complexity: Advanced | Last updated: 2026-05-05*