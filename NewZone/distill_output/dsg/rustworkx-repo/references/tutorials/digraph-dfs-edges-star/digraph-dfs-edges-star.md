# How To: Digraph Dfs Edges Star

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test digraph dfs edges star

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_star_graph(...)

```python
graph = rustworkx.generators.directed_star_graph(101)
```

### Step 2: Assign hub = 0

```python
hub = 0
```

### Step 3: Assign spokes = list(...)

```python
spokes = list(range(1, 101))
```

### Step 4: Assign edges = rustworkx.digraph_dfs_edges(...)

```python
edges = rustworkx.digraph_dfs_edges(graph, hub)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(len(edges), 100)
```

### Step 6: Assign visited = value

```python
visited = {tgt for _, tgt in edges}
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(visited, set(spokes))
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(src, hub)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_star_graph(101)
hub = 0
spokes = list(range(1, 101))
edges = rustworkx.digraph_dfs_edges(graph, hub)
self.assertEqual(len(edges), 100)
for src, _ in edges:
    self.assertEqual(src, hub)
visited = {tgt for _, tgt in edges}
self.assertEqual(visited, set(spokes))
```

## Next Steps


---

*Source: test_dfs_edges.py:53 | Complexity: Advanced | Last updated: 2026-05-05*