# How To: Digraph Dfs Tree Edges Restricted

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test digraph dfs tree edges restricted

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign vis = TreeEdgesRecorderRestricted(...)

```python
vis = TreeEdgesRecorderRestricted()
```

### Step 2: Call rustworkx.digraph_dfs_search()

```python
rustworkx.digraph_dfs_search(self.graph, [0], vis)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])
```

### Step 4: Assign prohibited = value

```python
prohibited = [(0, 1), (5, 3)]
```

### Step 5: Assign self.edges = value

```python
self.edges = []
```

### Step 6: Assign edge = value

```python
edge = (edge[0], edge[1])
```

### Step 7: Call self.edges.append()

```python
self.edges.append(edge)
```


## Complete Example

```python
# Workflow
class TreeEdgesRecorderRestricted(rustworkx.visit.DFSVisitor):
    prohibited = [(0, 1), (5, 3)]

    def __init__(self):
        self.edges = []

    def tree_edge(self, edge):
        edge = (edge[0], edge[1])
        if edge in self.prohibited:
            raise rustworkx.visit.PruneSearch
        self.edges.append(edge)
vis = TreeEdgesRecorderRestricted()
rustworkx.digraph_dfs_search(self.graph, [0], vis)
self.assertEqual(vis.edges, [(0, 2), (2, 6), (2, 5), (2, 1), (1, 3)])
```

## Next Steps


---

*Source: test_dfs_search.py:58 | Complexity: Intermediate | Last updated: 2026-05-05*