# How To: Clique

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test clique

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign N = 5

```python
N = 5
```

### Step 2: Assign graph = rustworkx.generators.complete_graph(...)

```python
graph = rustworkx.generators.complete_graph(N, multigraph=False)
```

### Step 3: Assign expected_graph = rustworkx.PyGraph(...)

```python
expected_graph = rustworkx.PyGraph(multigraph=False)
```

### Step 4: Call expected_graph.extend_from_edge_list()

```python
expected_graph.extend_from_edge_list([(i, node) for i in range(0, N) if i != node])
```

### Step 5: Assign complement_graph = rustworkx.local_complement(...)

```python
complement_graph = rustworkx.local_complement(graph, node)
```

### Step 6: Call self.assertTrue()

```python
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```


## Complete Example

```python
# Workflow
N = 5
graph = rustworkx.generators.complete_graph(N, multigraph=False)
for node in range(0, N):
    expected_graph = rustworkx.PyGraph(multigraph=False)
    expected_graph.extend_from_edge_list([(i, node) for i in range(0, N) if i != node])
    complement_graph = rustworkx.local_complement(graph, node)
    self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

## Next Steps


---

*Source: test_local_complement.py:31 | Complexity: Intermediate | Last updated: 2026-05-05*