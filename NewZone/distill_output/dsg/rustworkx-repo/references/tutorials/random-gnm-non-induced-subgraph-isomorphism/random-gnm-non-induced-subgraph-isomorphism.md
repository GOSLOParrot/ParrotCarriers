# How To: Random Gnm Non Induced Subgraph Isomorphism

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test random gnm non induced subgraph isomorphism

## Prerequisites

**Required Modules:**
- `unittest`
- `random`
- `math`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.undirected_gnm_random_graph(...)

```python
graph = rustworkx.undirected_gnm_random_graph(50, 150)
```

### Step 2: Assign nodes = random.sample(...)

```python
nodes = random.sample(range(50), 25)
```

### Step 3: Assign subgraph = graph.subgraph(...)

```python
subgraph = graph.subgraph(nodes)
```

### Step 4: Assign indexes = list(...)

```python
indexes = list(subgraph.edge_indices())
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(rustworkx.is_subgraph_isomorphic(graph, subgraph, id_order=True, induced=False))
```

### Step 6: Call subgraph.remove_edge_from_index()

```python
subgraph.remove_edge_from_index(idx)
```


## Complete Example

```python
# Workflow
graph = rustworkx.undirected_gnm_random_graph(50, 150)
nodes = random.sample(range(50), 25)
subgraph = graph.subgraph(nodes)
indexes = list(subgraph.edge_indices())
for idx in random.sample(indexes, len(indexes) // 2):
    subgraph.remove_edge_from_index(idx)
self.assertTrue(rustworkx.is_subgraph_isomorphic(graph, subgraph, id_order=True, induced=False))
```

## Next Steps


---

*Source: test_random.py:370 | Complexity: Intermediate | Last updated: 2026-05-05*