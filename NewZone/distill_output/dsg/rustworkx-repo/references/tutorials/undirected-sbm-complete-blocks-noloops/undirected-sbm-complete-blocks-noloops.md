# How To: Undirected Sbm Complete Blocks Noloops

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test undirected sbm complete blocks noloops

## Prerequisites

**Required Modules:**
- `unittest`
- `random`
- `math`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.undirected_sbm_random_graph(...)

```python
graph = rustworkx.undirected_sbm_random_graph([2, 1], np.array([[1, 1], [1, 0]], dtype=float), False)
```

### Step 2: Call self.assertEqual()

```python
self.assertEqual(len(graph), 3)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), 3)
```

### Step 4: Call self.assertTrue()

```python
self.assertTrue(graph.has_edge(i, j))
```


## Complete Example

```python
# Workflow
graph = rustworkx.undirected_sbm_random_graph([2, 1], np.array([[1, 1], [1, 0]], dtype=float), False)
self.assertEqual(len(graph), 3)
self.assertEqual(len(graph.edges()), 3)
for i in range(2):
    for j in range(i, 2):
        if i != j:
            self.assertTrue(graph.has_edge(i, j))
```

## Next Steps


---

*Source: test_random.py:202 | Complexity: Intermediate | Last updated: 2026-05-05*