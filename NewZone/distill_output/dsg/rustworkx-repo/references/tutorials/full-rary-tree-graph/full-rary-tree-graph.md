# How To: Full Rary Tree Graph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test full rary tree graph

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign b_factors = value

```python
b_factors = {0: 0, 1: 2, 2: 2, 3: 5}
```

### Step 2: Assign num_nodes = value

```python
num_nodes = {0: 0, 1: 4, 2: 10, 3: 15}
```

### Step 3: Assign expected_edges = value

```python
expected_edges = {0: [], 1: [(0, 1), (0, 2), (1, 3)], 2: [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (3, 8), (4, 9)], 3: [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, 11), (2, 12), (2, 13), (2, 14)]}
```

### Step 4: Assign graph = rustworkx.generators.full_rary_tree(...)

```python
graph = rustworkx.generators.full_rary_tree(b_factors[n], num_nodes[n])
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(list(graph.edge_list()), expected_edges[n])
```


## Complete Example

```python
# Workflow
b_factors = {0: 0, 1: 2, 2: 2, 3: 5}
num_nodes = {0: 0, 1: 4, 2: 10, 3: 15}
expected_edges = {0: [], 1: [(0, 1), (0, 2), (1, 3)], 2: [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (3, 8), (4, 9)], 3: [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, 11), (2, 12), (2, 13), (2, 14)]}
for n in range(4):
    with self.subTest(n=n):
        graph = rustworkx.generators.full_rary_tree(b_factors[n], num_nodes[n])
        self.assertEqual(list(graph.edge_list()), expected_edges[n])
```

## Next Steps


---

*Source: test_full_rary_tree.py:18 | Complexity: Intermediate | Last updated: 2026-05-05*