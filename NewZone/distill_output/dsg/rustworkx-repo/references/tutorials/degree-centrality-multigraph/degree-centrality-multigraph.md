# How To: Degree Centrality Multigraph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test degree centrality multigraph

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `math`
- `unittest`
- `rustworkx`
- `networkx`

**Setup Required:**
```python
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
edge_list = [(self.a, self.b, 1), (self.b, self.c, 1), (self.c, self.d, 1)]
self.graph.add_edges_from(edge_list)
```

## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Assign a = graph.add_node(...)

```python
a = graph.add_node('A')
```

### Step 3: Assign b = graph.add_node(...)

```python
b = graph.add_node('B')
```

### Step 4: Assign c = graph.add_node(...)

```python
c = graph.add_node('C')
```

### Step 5: Assign edge_list = value

```python
edge_list = [(a, b, 1), (a, b, 2), (b, c, 1)]
```

### Step 6: Call graph.add_edges_from()

```python
graph.add_edges_from(edge_list)
```

### Step 7: Assign centrality = rustworkx.degree_centrality(...)

```python
centrality = rustworkx.degree_centrality(graph)
```

### Step 8: Assign expected = value

```python
expected = {0: 1.0, 1: 1.5, 2: 0.5}
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(expected, dict(centrality))
```


## Complete Example

```python
# Setup
self.graph = rustworkx.PyGraph()
self.a = self.graph.add_node('A')
self.b = self.graph.add_node('B')
self.c = self.graph.add_node('C')
self.d = self.graph.add_node('D')
edge_list = [(self.a, self.b, 1), (self.b, self.c, 1), (self.c, self.d, 1)]
self.graph.add_edges_from(edge_list)

# Workflow
graph = rustworkx.PyGraph()
a = graph.add_node('A')
b = graph.add_node('B')
c = graph.add_node('C')
edge_list = [(a, b, 1), (a, b, 2), (b, c, 1)]
graph.add_edges_from(edge_list)
centrality = rustworkx.degree_centrality(graph)
expected = {0: 1.0, 1: 1.5, 2: 0.5}
self.assertEqual(expected, dict(centrality))
```

## Next Steps


---

*Source: test_centrality.py:293 | Complexity: Advanced | Last updated: 2026-05-05*