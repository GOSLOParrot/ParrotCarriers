# How To: Undirected Sbm Complete Blocks Loops

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test undirected sbm complete blocks loops

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
graph = rustworkx.undirected_sbm_random_graph([2, 1], np.array([[1, 1], [1, 0]], dtype=float), True)
```

### Step 2: Call self.assertEqual()

```python
self.assertEqual(len(graph), 3)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), 5)
```

### Step 4: Call self.assertFalse()

```python
self.assertFalse(graph.has_edge(2, 2))
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(graph.has_edge(i, j))
```


## Complete Example

```python
# Workflow
graph = rustworkx.undirected_sbm_random_graph([2, 1], np.array([[1, 1], [1, 0]], dtype=float), True)
self.assertEqual(len(graph), 3)
self.assertEqual(len(graph.edges()), 5)
for i in range(2):
    for j in range(i, 2):
        if (i, j) != (2, 2):
            self.assertTrue(graph.has_edge(i, j))
self.assertFalse(graph.has_edge(2, 2))
```

## Next Steps


---

*Source: test_random.py:182 | Complexity: Intermediate | Last updated: 2026-05-05*