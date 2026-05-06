# How To: Irreducible1

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).
https://hdl.handle.net/1911/96345

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: '\n        Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '

```python
'\n        Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
```

### Step 2: Assign edges = value

```python
edges = [(1, 2), (2, 1), (3, 2), (4, 1), (5, 3), (5, 4)]
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

### Step 6: Assign result = rx.immediate_dominators(...)

```python
result = rx.immediate_dominators(graph, 5)
```

### Step 7: Call self.assertDictEqual()

```python
self.assertDictEqual(result, {i: 5 for i in range(1, 6)})
```

### Step 8: Assign nx_graph = nx.DiGraph(...)

```python
nx_graph = nx.DiGraph()
```

### Step 9: Call nx_graph.add_edges_from()

```python
nx_graph.add_edges_from(graph.edge_list())
```

### Step 10: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 5).items())
```


## Complete Example

```python
# Workflow
'\n        Graph taken from figure 2 of "A simple, fast dominance algorithm." (2006).\n        https://hdl.handle.net/1911/96345\n        '
edges = [(1, 2), (2, 1), (3, 2), (4, 1), (5, 3), (5, 4)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.immediate_dominators(graph, 5)
self.assertDictEqual(result, {i: 5 for i in range(1, 6)})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertGreaterEqual(result.items(), nx.immediate_dominators(nx_graph, 5).items())
```

## Next Steps


---

*Source: test_dominance.py:65 | Complexity: Advanced | Last updated: 2026-05-05*