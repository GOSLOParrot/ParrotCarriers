# How To: Multiple Mapping

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test multiple mapping

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
in_graph = rustworkx.generators.star_graph(3)
```

### Step 3: Assign res = graph.substitute_node_with_subgraph(...)

```python
res = graph.substitute_node_with_subgraph(0, in_graph, map_function)
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual({0: 5, 1: 6, 2: 7}, res)
```

### Step 5: Assign expected = value

```python
expected = [(5, 6), (5, 7), (7, 4), (7, 3), (6, 2), (6, 1)]
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(sorted(expected), sorted(graph.edge_list()))
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.star_graph(5)
in_graph = rustworkx.generators.star_graph(3)

def map_function(_source, target, _weight):
    if target > 2:
        return 2
    return 1
res = graph.substitute_node_with_subgraph(0, in_graph, map_function)
self.assertEqual({0: 5, 1: 6, 2: 7}, res)
expected = [(5, 6), (5, 7), (7, 4), (7, 3), (6, 2), (6, 1)]
self.assertEqual(sorted(expected), sorted(graph.edge_list()))
```

## Next Steps


---

*Source: test_substitute_node_with_subgraph.py:92 | Complexity: Intermediate | Last updated: 2026-05-05*