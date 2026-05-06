# How To: Empty Directed

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test empty directed

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign N = 5

```python
N = 5
```

### Step 2: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 3: Call graph.add_nodes_from()

```python
graph.add_nodes_from([i for i in range(N)])
```

### Step 4: Assign expected_graph = rustworkx.PyDiGraph(...)

```python
expected_graph = rustworkx.PyDiGraph()
```

### Step 5: Call expected_graph.extend_from_edge_list()

```python
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j])
```

### Step 6: Assign complement_graph = rustworkx.complement(...)

```python
complement_graph = rustworkx.complement(graph)
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```


## Complete Example

```python
# Workflow
N = 5
graph = rustworkx.PyDiGraph()
graph.add_nodes_from([i for i in range(N)])
expected_graph = rustworkx.PyDiGraph()
expected_graph.extend_from_edge_list([(i, j) for i in range(N) for j in range(N) if i != j])
complement_graph = rustworkx.complement(graph)
self.assertTrue(rustworkx.is_isomorphic(expected_graph, complement_graph))
```

## Next Steps


---

*Source: test_complement.py:34 | Complexity: Intermediate | Last updated: 2026-05-05*