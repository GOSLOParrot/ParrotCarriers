# How To: Nan Null

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test nan null

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: Assign input_matrix = np.array(...)

```python
input_matrix = np.array([[np.nan, 1, np.nan], [1, np.nan, 1], [np.nan, 1, np.nan]], dtype=np.float64)
```

### Step 2: Assign graph = rustworkx.PyGraph.from_adjacency_matrix(...)

```python
graph = rustworkx.PyGraph.from_adjacency_matrix(input_matrix, null_value=np.nan)
```

### Step 3: Assign adj_matrix = rustworkx.adjacency_matrix(...)

```python
adj_matrix = rustworkx.adjacency_matrix(graph, float)
```

### Step 4: Assign expected_matrix = np.array(...)

```python
expected_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=np.float64)
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(np.array_equal(adj_matrix, expected_matrix))
```


## Complete Example

```python
# Workflow
input_matrix = np.array([[np.nan, 1, np.nan], [1, np.nan, 1], [np.nan, 1, np.nan]], dtype=np.float64)
graph = rustworkx.PyGraph.from_adjacency_matrix(input_matrix, null_value=np.nan)
adj_matrix = rustworkx.adjacency_matrix(graph, float)
expected_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=np.float64)
self.assertTrue(np.array_equal(adj_matrix, expected_matrix))
```

## Next Steps


---

*Source: test_adjacency_matrix.py:183 | Complexity: Intermediate | Last updated: 2026-05-05*