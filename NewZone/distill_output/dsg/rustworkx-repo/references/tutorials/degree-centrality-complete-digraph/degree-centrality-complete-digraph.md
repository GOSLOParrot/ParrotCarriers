# How To: Degree Centrality Complete Digraph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test degree centrality complete digraph

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`
- `networkx`

**Setup Required:**
```python
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
edge_list = [(self.a, self.b, 1), (self.b, self.c, 1), (self.c, self.d, 1), (self.a, self.c, 1)]
self.graph.add_edges_from(edge_list)
```

## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_complete_graph(...)

```python
graph = rustworkx.generators.directed_complete_graph(5)
```

### Step 2: Assign centrality = rustworkx.degree_centrality(...)

```python
centrality = rustworkx.degree_centrality(graph)
```

### Step 3: Assign expected = value

```python
expected = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}
```

### Step 4: Call self.assertAlmostEqual()

```python
self.assertAlmostEqual(v, expected[k])
```


## Complete Example

```python
# Setup
self.graph = rustworkx.PyDiGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
edge_list = [(self.a, self.b, 1), (self.b, self.c, 1), (self.c, self.d, 1), (self.a, self.c, 1)]
self.graph.add_edges_from(edge_list)

# Workflow
graph = rustworkx.generators.directed_complete_graph(5)
centrality = rustworkx.degree_centrality(graph)
expected = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}
for k, v in centrality.items():
    self.assertAlmostEqual(v, expected[k])
```

## Next Steps


---

*Source: test_centrality.py:310 | Complexity: Intermediate | Last updated: 2026-05-05*