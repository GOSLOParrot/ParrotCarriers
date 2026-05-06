# How To: Find Negative Cycle Self Loop Cycle

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test find negative cycle self loop cycle

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `unittest`
- `rustworkx`

**Setup Required:**
```python
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)
```

## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Call graph.add_nodes_from()

```python
graph.add_nodes_from(list(range(4)))
```

### Step 3: Call graph.add_edges_from()

```python
graph.add_edges_from([(0, 1, 1), (1, 0, 1), (0, 0, -1)])
```

### Step 4: Assign cycle = rustworkx.find_negative_cycle(...)

```python
cycle = rustworkx.find_negative_cycle(graph, edge_cost_fn=float)
```

### Step 5: Assign cycle_weight = 0

```python
cycle_weight = 0
```

### Step 6: Call self.assertTrue()

```python
self.assertTrue(cycle_weight < 0)
```


## Complete Example

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
self.e = self.graph.add_node('E')
self.f = self.graph.add_node('F')
edge_list = [(self.a, self.b, 7), (self.c, self.a, 9), (self.a, self.d, 14), (self.b, self.c, 10), (self.d, self.c, 2), (self.d, self.e, 9), (self.b, self.f, 15), (self.c, self.f, 11), (self.e, self.f, 6)]
self.graph.add_edges_from(edge_list)

# Workflow
graph = rustworkx.PyDiGraph()
graph.add_nodes_from(list(range(4)))
graph.add_edges_from([(0, 1, 1), (1, 0, 1), (0, 0, -1)])
cycle = rustworkx.find_negative_cycle(graph, edge_cost_fn=float)
cycle_weight = 0
for i in range(len(cycle) - 1):
    cycle_weight += graph.get_edge_data(cycle[i], cycle[i + 1])
self.assertTrue(cycle_weight < 0)
```

## Next Steps


---

*Source: test_bellman_ford.py:296 | Complexity: Intermediate | Last updated: 2026-05-05*