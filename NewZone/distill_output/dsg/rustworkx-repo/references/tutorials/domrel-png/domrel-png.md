# How To: Domrel Png

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: '\n        Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png\n        '

```python
'\n        Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png\n        '
```

### Step 2: Assign edges = value

```python
edges = [(1, 2), (2, 3), (2, 4), (2, 6), (3, 5), (4, 5), (5, 2)]
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
result = rx.dominance_frontiers(graph, 1)
```

### Step 7: Call self.assertDictEqual()

```python
self.assertDictEqual(result, {1: set(), 2: {2}, 3: {5}, 4: {5}, 5: {2}, 6: set()})
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
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 1), result)
```

### Step 11: Call graph.reverse()

```python
graph.reverse()
```

### Step 12: Assign result = rx.dominance_frontiers(...)

```python
result = rx.dominance_frontiers(graph, 6)
```

### Step 13: Call self.assertDictEqual()

```python
self.assertDictEqual(result, {1: set(), 2: {2}, 3: {2}, 4: {2}, 5: {2}, 6: set()})
```

### Step 14: Call self.assertDictEqual()

```python
self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 6), result)
```


## Complete Example

```python
# Workflow
'\n        Graph taken from https://commons.wikipedia.org/wiki/File:Domrel.png\n        '
edges = [(1, 2), (2, 3), (2, 4), (2, 6), (3, 5), (4, 5), (5, 2)]
graph = rx.PyDiGraph()
graph.add_node(0)
graph.extend_from_edge_list(edges)
result = rx.dominance_frontiers(graph, 1)
self.assertDictEqual(result, {1: set(), 2: {2}, 3: {5}, 4: {5}, 5: {2}, 6: set()})
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 1), result)
graph.reverse()
result = rx.dominance_frontiers(graph, 6)
self.assertDictEqual(result, {1: set(), 2: {2}, 3: {2}, 4: {2}, 5: {2}, 6: set()})
self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 6), result)
```

## Next Steps


---

*Source: test_dominance.py:239 | Complexity: Advanced | Last updated: 2026-05-05*