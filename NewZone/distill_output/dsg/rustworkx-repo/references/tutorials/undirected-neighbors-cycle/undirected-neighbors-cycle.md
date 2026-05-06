# How To: Undirected Neighbors Cycle

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test undirected neighbors cycle

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `rustworkx.generators`


## Step-by-Step Guide

### Step 1: Assign num_nodes = 10

```python
num_nodes = 10
```

### Step 2: Assign dag = rustworkx.generators.directed_cycle_graph(...)

```python
dag = rustworkx.generators.directed_cycle_graph(num_nodes, bidirectional=False)
```

### Step 3: Assign undirected_dag = dag.to_undirected(...)

```python
undirected_dag = dag.to_undirected()
```

### Step 4: Assign undirected_neighbors = dag.neighbors_undirected(...)

```python
undirected_neighbors = dag.neighbors_undirected(node)
```

### Step 5: Assign expected_neighbors = undirected_dag.neighbors(...)

```python
expected_neighbors = undirected_dag.neighbors(node)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(sorted(undirected_neighbors), sorted(expected_neighbors))
```


## Complete Example

```python
# Workflow
num_nodes = 10
dag = rustworkx.generators.directed_cycle_graph(num_nodes, bidirectional=False)
undirected_dag = dag.to_undirected()
for node in dag.node_indices():
    undirected_neighbors = dag.neighbors_undirected(node)
    expected_neighbors = undirected_dag.neighbors(node)
    self.assertEqual(sorted(undirected_neighbors), sorted(expected_neighbors))
```

## Next Steps


---

*Source: test_neighbors.py:73 | Complexity: Intermediate | Last updated: 2026-05-05*