# How To: Multiple Mapping Full

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test multiple mapping full

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.star_graph(...)

```python
graph = rustworkx.generators.star_graph(5)
```

### Step 2: Assign in_graph = rustworkx.generators.star_graph(...)

```python
in_graph = rustworkx.generators.star_graph(weights=list(range(3)))
```

### Step 3: Call in_graph.add_edge()

```python
in_graph.add_edge(1, 2, None)
```

### Step 4: Assign res = graph.substitute_node_with_subgraph(...)

```python
res = graph.substitute_node_with_subgraph(0, in_graph, map_function, filter_fn, map_weight)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual({1: 5, 2: 6}, res)
```

### Step 6: Assign expected = value

```python
expected = [(5, 6, 'migrated'), (6, 4, None), (6, 3, None), (5, 2, None), (5, 1, None)]
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(expected, graph.weighted_edge_list())
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.star_graph(5)
in_graph = rustworkx.generators.star_graph(weights=list(range(3)))
in_graph.add_edge(1, 2, None)

def map_function(source, target, _weight):
    if target > 2:
        return 2
    return 1

def filter_fn(node):
    return node > 0

def map_weight(_):
    return 'migrated'
res = graph.substitute_node_with_subgraph(0, in_graph, map_function, filter_fn, map_weight)
self.assertEqual({1: 5, 2: 6}, res)
expected = [(5, 6, 'migrated'), (6, 4, None), (6, 3, None), (5, 2, None), (5, 1, None)]
self.assertEqual(expected, graph.weighted_edge_list())
```

## Next Steps


---

*Source: test_substitute_node_with_subgraph.py:106 | Complexity: Intermediate | Last updated: 2026-05-05*