# How To: Graph Bfs Goal Search With Stop Search Exception

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test graph bfs goal search with stop search exception

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign vis = GoalSearch(...)

```python
vis = GoalSearch()
```

### Step 2: Call rustworkx.graph_bfs_search()

```python
rustworkx.graph_bfs_search(self.graph, [0], vis)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

### Step 4: Assign goal = 3

```python
goal = 3
```

### Step 5: Assign self.parents = value

```python
self.parents = {}
```

### Step 6: Assign unknown = edge

```python
u, v, _ = edge
```

### Step 7: Assign unknown = u

```python
self.parents[v] = u
```

### Step 8: Assign v = value

```python
v = self.goal
```

### Step 9: Assign path = value

```python
path = [v]
```

### Step 10: Call path.reverse()

```python
path.reverse()
```

### Step 11: Assign v = value

```python
v = self.parents[v]
```

### Step 12: Call path.append()

```python
path.append(v)
```


## Complete Example

```python
# Workflow
class GoalSearch(rustworkx.visit.BFSVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}

    def tree_edge(self, edge):
        u, v, _ = edge
        self.parents[v] = u
        if v == self.goal:
            raise rustworkx.visit.StopSearch

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.graph_bfs_search(self.graph, [0], vis)
self.assertEqual(vis.reconstruct_path(), [0, 1, 3])
```

## Next Steps


---

*Source: test_bfs_search.py:75 | Complexity: Advanced | Last updated: 2026-05-05*