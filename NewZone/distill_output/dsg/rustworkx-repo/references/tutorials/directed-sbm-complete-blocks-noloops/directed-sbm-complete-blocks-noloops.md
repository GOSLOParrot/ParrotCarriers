# How To: Directed Sbm Complete Blocks Noloops

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test directed sbm complete blocks noloops

## Prerequisites

**Required Modules:**
- `unittest`
- `random`
- `math`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.directed_sbm_random_graph(...)

```python
graph = rustworkx.directed_sbm_random_graph([2, 1], np.array([[0, 0], [1, 1]], dtype=float), False)
```

### Step 2: Call self.assertEqual()

```python
self.assertEqual(len(graph), 3)
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(len(graph.edges()), 2)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(set(graph.edge_list()), set([(2, 0), (2, 1)]))
```


## Complete Example

```python
# Workflow
graph = rustworkx.directed_sbm_random_graph([2, 1], np.array([[0, 0], [1, 1]], dtype=float), False)
self.assertEqual(len(graph), 3)
self.assertEqual(len(graph.edges()), 2)
self.assertEqual(set(graph.edge_list()), set([(2, 0), (2, 1)]))
```

## Next Steps


---

*Source: test_random.py:213 | Complexity: Intermediate | Last updated: 2026-05-05*