# How To: Graph

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test graph

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign edges = value

```python
edges = [(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)]
```

### Step 2: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 3: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list(edges)
```

### Step 4: Assign chains = rustworkx.chain_decomposition(...)

```python
chains = rustworkx.chain_decomposition(graph, source=0)
```

### Step 5: Assign expected = value

```python
expected = [[(0, 3), (3, 2), (2, 1), (1, 0)], [(0, 2)], [(1, 4), (4, 2)], [(4, 9), (9, 8), (8, 4)], [(5, 7), (7, 6), (6, 5)]]
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(expected, chains)
```


## Complete Example

```python
# Workflow
edges = [(0, 2), (0, 3), (1, 4), (4, 9), (5, 7), (0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 8), (5, 6), (6, 7), (8, 9)]
graph = rustworkx.PyGraph()
graph.extend_from_edge_list(edges)
chains = rustworkx.chain_decomposition(graph, source=0)
expected = [[(0, 3), (3, 2), (2, 1), (1, 0)], [(0, 2)], [(1, 4), (4, 2)], [(4, 9), (9, 8), (8, 4)], [(5, 7), (7, 6), (6, 5)]]
self.assertEqual(expected, chains)
```

## Next Steps


---

*Source: test_chain_decomposition.py:34 | Complexity: Intermediate | Last updated: 2026-05-05*