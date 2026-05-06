# How To: Digraph Dijkstra Tree Edges

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test digraph dijkstra tree edges

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign vis = DijkstraTreeEdgesRecorder(...)

```python
vis = DijkstraTreeEdgesRecorder()
```

### Step 2: Call rustworkx.digraph_dijkstra_search()

```python
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

### Step 4: Assign self.edges = value

```python
self.edges = []
```

### Step 5: Assign self.parents = dict(...)

```python
self.parents = dict()
```

### Step 6: Assign u = self.parents.get(...)

```python
u = self.parents.get(v, None)
```

### Step 7: Assign unknown = edge

```python
u, v, _ = edge
```

### Step 8: Assign unknown = u

```python
self.parents[v] = u
```

### Step 9: Call self.edges.append()

```python
self.edges.append((u, v))
```


## Complete Example

```python
# Workflow
class DijkstraTreeEdgesRecorder(rustworkx.visit.DijkstraVisitor):

    def __init__(self):
        self.edges = []
        self.parents = dict()

    def discover_vertex(self, v, _):
        u = self.parents.get(v, None)
        if u is not None:
            self.edges.append((u, v))

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u
vis = DijkstraTreeEdgesRecorder()
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.edges, [(0, 1), (0, 2), (2, 6), (2, 5), (5, 3)])
```

## Next Steps


---

*Source: test_dijkstra_search.py:34 | Complexity: Advanced | Last updated: 2026-05-05*