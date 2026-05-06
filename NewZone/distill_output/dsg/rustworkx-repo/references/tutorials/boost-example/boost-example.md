# How To: Boost Example

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Graph taken from Figure 1 of
http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: '\n        Graph taken from Figure 1 of\n        http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm\n        '

```python
'\n        Graph taken from Figure 1 of\n        http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm\n        '
```

### Step 2: Assign edges = value

```python
edges = [(0, 1), (1, 2), (1, 3), (2, 7), (3, 4), (4, 5), (4, 6), (5, 7), (6, 4)]
```

### Step 3: Assign graph = rx.PyDiGraph(...)

```python
graph = rx.PyDiGraph()
```

### Step 4: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list(edges)
```

### Step 5: Assign nx_graph = nx.DiGraph(...)

```python
nx_graph = nx.DiGraph()
```

### Step 6: Call nx_graph.add_edges_from()

```python
nx_graph.add_edges_from(graph.edge_list())
```

### Step 7: Assign result = rx.dominance_frontiers(...)

```python
result = rx.dominance_frontiers(graph, 0)
```

### Step 8: Call self.assertDictEqual()

```python
self.assertDictEqual(result, {0: set(), 1: set(), 2: {7}, 3: {7}, 4: {4, 7}, 5: {7}, 6: {4}, 7: set()})
```

### Step 9: Call self.assertDictEqual()

```python
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 0), result)
```

### Step 10: Call graph.reverse()

```python
graph.reverse()
```

### Step 11: Assign result = rx.dominance_frontiers(...)

```python
result = rx.dominance_frontiers(graph, 7)
```

### Step 12: Call self.assertDictEqual()

```python
self.assertDictEqual(result, {0: set(), 1: set(), 2: {1}, 3: {1}, 4: {1, 4}, 5: {1}, 6: {4}, 7: set()})
```

### Step 13: Call self.assertDictEqual()

```python
self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 7), result)
```


## Complete Example

```python
# Workflow
'\n        Graph taken from Figure 1 of\n        http://www.boost.org/doc/libs/1_56_0/libs/graph/doc/lengauer_tarjan_dominator.htm\n        '
edges = [(0, 1), (1, 2), (1, 3), (2, 7), (3, 4), (4, 5), (4, 6), (5, 7), (6, 4)]
graph = rx.PyDiGraph()
graph.extend_from_edge_list(edges)
nx_graph = nx.DiGraph()
nx_graph.add_edges_from(graph.edge_list())
result = rx.dominance_frontiers(graph, 0)
self.assertDictEqual(result, {0: set(), 1: set(), 2: {7}, 3: {7}, 4: {4, 7}, 5: {7}, 6: {4}, 7: set()})
self.assertDictEqual(nx.dominance_frontiers(nx_graph, 0), result)
graph.reverse()
result = rx.dominance_frontiers(graph, 7)
self.assertDictEqual(result, {0: set(), 1: set(), 2: {1}, 3: {1}, 4: {1, 4}, 5: {1}, 6: {4}, 7: set()})
self.assertDictEqual(nx.dominance_frontiers(nx_graph.reverse(copy=False), 7), result)
```

## Next Steps


---

*Source: test_dominance.py:283 | Complexity: Advanced | Last updated: 2026-05-05*