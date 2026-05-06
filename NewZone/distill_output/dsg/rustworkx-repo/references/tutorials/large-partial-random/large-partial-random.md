# How To: Large Partial Random

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test a random (partial) mapping on a large randomly generated graph

## Prerequisites

**Required Modules:**
- `unittest`
- `itertools`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: 'Test a random (partial) mapping on a large randomly generated graph'

```python
'Test a random (partial) mapping on a large randomly generated graph'
```

### Step 2: Assign size = 100

```python
size = 100
```

### Step 3: Assign graph = rx.undirected_gnm_random_graph(...)

```python
graph = rx.undirected_gnm_random_graph(size, size ** 2 // 10)
```

### Step 4: Call graph.add_edges_from_no_data()

```python
graph.add_edges_from_no_data([(i, i + 1) for i in range(len(graph) - 1)])
```

### Step 5: Assign rand_perm = random.permutation(...)

```python
rand_perm = random.permutation(graph.nodes())
```

### Step 6: Assign permutation = dict(...)

```python
permutation = dict(zip(graph.nodes(), rand_perm))
```

### Step 7: Assign mapping = dict(...)

```python
mapping = dict(itertools.islice(permutation.items(), 0, size, 2))
```

### Step 8: Assign swaps = rx.graph_token_swapper(...)

```python
swaps = rx.graph_token_swapper(graph, permutation, 4, 4)
```

### Step 9: Call swap_permutation()

```python
swap_permutation(mapping, swaps)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual({i: i for i in mapping.values()}, mapping)
```

### Step 11: Call graph.remove_edge()

```python
graph.remove_edge(i, i)
```


## Complete Example

```python
# Workflow
'Test a random (partial) mapping on a large randomly generated graph'
size = 100
graph = rx.undirected_gnm_random_graph(size, size ** 2 // 10)
for i in graph.node_indexes():
    try:
        graph.remove_edge(i, i)
    except rx.NoEdgeBetweenNodes:
        continue
graph.add_edges_from_no_data([(i, i + 1) for i in range(len(graph) - 1)])
rand_perm = random.permutation(graph.nodes())
permutation = dict(zip(graph.nodes(), rand_perm))
mapping = dict(itertools.islice(permutation.items(), 0, size, 2))
swaps = rx.graph_token_swapper(graph, permutation, 4, 4)
swap_permutation(mapping, swaps)
self.assertEqual({i: i for i in mapping.values()}, mapping)
```

## Next Steps


---

*Source: test_token_swapper.py:99 | Complexity: Advanced | Last updated: 2026-05-05*