# How To: Random Graph Full Path

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test random graph full path

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.undirected_gnp_random_graph(...)

```python
graph = rustworkx.undirected_gnp_random_graph(100, 0.95, seed=42)
```

### Step 2: Assign adjacency_matrix = rustworkx.graph_adjacency_matrix(...)

```python
adjacency_matrix = rustworkx.graph_adjacency_matrix(graph)
```

### Step 3: Assign new_graph = rustworkx.PyGraph.from_adjacency_matrix(...)

```python
new_graph = rustworkx.PyGraph.from_adjacency_matrix(adjacency_matrix)
```

### Step 4: Assign new_adjacency_matrix = rustworkx.graph_adjacency_matrix(...)

```python
new_adjacency_matrix = rustworkx.graph_adjacency_matrix(new_graph)
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(np.array_equal(adjacency_matrix, new_adjacency_matrix))
```


## Complete Example

```python
# Workflow
graph = rustworkx.undirected_gnp_random_graph(100, 0.95, seed=42)
adjacency_matrix = rustworkx.graph_adjacency_matrix(graph)
new_graph = rustworkx.PyGraph.from_adjacency_matrix(adjacency_matrix)
new_adjacency_matrix = rustworkx.graph_adjacency_matrix(new_graph)
self.assertTrue(np.array_equal(adjacency_matrix, new_adjacency_matrix))
```

## Next Steps


---

*Source: test_adjacency_matrix.py:138 | Complexity: Intermediate | Last updated: 2026-05-05*