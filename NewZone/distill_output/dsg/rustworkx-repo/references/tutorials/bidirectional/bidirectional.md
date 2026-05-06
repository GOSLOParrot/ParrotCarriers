# How To: Bidirectional

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test bidirectional

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_path_graph(...)

```python
graph = rustworkx.generators.directed_path_graph(5, bidirectional=True)
```

### Step 2: Assign in_graph = rustworkx.generators.directed_star_graph(...)

```python
in_graph = rustworkx.generators.directed_star_graph(5, bidirectional=True)
```

### Step 3: Assign res = graph.substitute_node_with_subgraph(...)

```python
res = graph.substitute_node_with_subgraph(2, in_graph, map_function)
```

### Step 4: Assign expected_node_map = value

```python
expected_node_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9}
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(expected_node_map, res)
```

### Step 6: Assign expected_edge_list = value

```python
expected_edge_list = [(0, 1), (1, 0), (3, 4), (4, 3), (6, 5), (5, 6), (7, 5), (5, 7), (8, 5), (5, 8), (9, 5), (5, 9), (3, 5), (1, 5), (8, 3), (6, 1)]
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(expected_edge_list, graph.edge_list())
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_path_graph(5, bidirectional=True)
in_graph = rustworkx.generators.directed_star_graph(5, bidirectional=True)

def map_function(source, target, _weight):
    if source != 2:
        return 0
    else:
        return target
res = graph.substitute_node_with_subgraph(2, in_graph, map_function)
expected_node_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9}
self.assertEqual(expected_node_map, res)
expected_edge_list = [(0, 1), (1, 0), (3, 4), (4, 3), (6, 5), (5, 6), (7, 5), (5, 7), (8, 5), (5, 8), (9, 5), (5, 9), (3, 5), (1, 5), (8, 3), (6, 1)]
self.assertEqual(expected_edge_list, graph.edge_list())
```

## Next Steps


---

*Source: test_substitute_node_with_subgraph.py:132 | Complexity: Intermediate | Last updated: 2026-05-05*