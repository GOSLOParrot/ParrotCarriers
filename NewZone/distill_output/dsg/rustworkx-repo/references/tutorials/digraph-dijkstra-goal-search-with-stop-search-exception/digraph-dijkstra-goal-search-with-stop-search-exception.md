# How To: Digraph Dijkstra Goal Search With Stop Search Exception

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test digraph dijkstra goal search with stop search exception

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign vis = GoalSearch(...)

```python
vis = GoalSearch()
```

### Step 2: Call rustworkx.digraph_dijkstra_search()

```python
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(vis.opt_goal_cost, 4.0)
```

### Step 5: Assign goal = 3

```python
goal = 3
```

### Step 6: Assign self.parents = value

```python
self.parents = {}
```

### Step 7: Assign self.opt_goal_cost = None

```python
self.opt_goal_cost = None
```

### Step 8: Assign unknown = edge

```python
u, v, _ = edge
```

### Step 9: Assign unknown = u

```python
self.parents[v] = u
```

### Step 10: Assign v = value

```python
v = self.goal
```

### Step 11: Assign path = value

```python
path = [v]
```

### Step 12: Call path.reverse()

```python
path.reverse()
```

### Step 13: Assign self.opt_goal_cost = score

```python
self.opt_goal_cost = score
```

### Step 14: Assign v = value

```python
v = self.parents[v]
```

### Step 15: Call path.append()

```python
path.append(v)
```


## Complete Example

```python
# Workflow
class GoalSearch(rustworkx.visit.DijkstraVisitor):
    goal = 3

    def __init__(self):
        self.parents = {}
        self.opt_goal_cost = None

    def discover_vertex(self, v, score):
        if v == self.goal:
            self.opt_goal_cost = score
            raise rustworkx.visit.StopSearch

    def edge_relaxed(self, edge):
        u, v, _ = edge
        self.parents[v] = u

    def reconstruct_path(self):
        v = self.goal
        path = [v]
        while v in self.parents:
            v = self.parents[v]
            path.append(v)
        path.reverse()
        return path
vis = GoalSearch()
rustworkx.digraph_dijkstra_search(self.graph, [0], float, vis)
self.assertEqual(vis.reconstruct_path(), [0, 2, 5, 3])
self.assertEqual(vis.opt_goal_cost, 4.0)
```

## Next Steps


---

*Source: test_dijkstra_search.py:72 | Complexity: Advanced | Last updated: 2026-05-05*