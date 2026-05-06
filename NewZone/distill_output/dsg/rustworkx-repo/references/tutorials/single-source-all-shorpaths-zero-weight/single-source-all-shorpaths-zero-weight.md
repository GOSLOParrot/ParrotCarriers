# How To: Single Source All Shorpaths Zero Weight

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test single source all shortest paths zero weight

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Assign nodes = graph.add_nodes_from(...)

```python
nodes = graph.add_nodes_from([0, 1, 2, 3])
```

### Step 3: Call graph.add_edge()

```python
graph.add_edge(nodes[0], nodes[1], 0.0)
```

### Step 4: Call graph.add_edge()

```python
graph.add_edge(nodes[0], nodes[2], 1.0)
```

### Step 5: Call graph.add_edge()

```python
graph.add_edge(nodes[1], nodes[3], 1.0)
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(nodes[2], nodes[3], 0.0)
```

### Step 7: Assign source = value

```python
source = nodes[0]
```

### Step 8: Assign shortest_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(...)

```python
shortest_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(graph, source, lambda e: e)
```

### Step 9: Assign all_shortest_paths = rustworkx.digraph_single_source_all_shortest_paths(...)

```python
all_shortest_paths = rustworkx.digraph_single_source_all_shortest_paths(graph, source)
```

### Step 10: Assign target_idx = target

```python
target_idx = target
```

### Step 11: Assign all_paths = rustworkx.all_simple_paths(...)

```python
all_paths = rustworkx.all_simple_paths(graph, source, target_idx)
```

### Step 12: Assign expected_paths = value

```python
expected_paths = [path for path in all_paths if path_weight(path) == shortest_lengths[target_idx]]
```

### Step 13: Assign computed_paths = all_shortest_paths.get(...)

```python
computed_paths = all_shortest_paths.get(target_idx, [])
```

### Step 14: Call expected_paths.sort()

```python
expected_paths.sort()
```

### Step 15: Call computed_paths.sort()

```python
computed_paths.sort()
```

### Step 16: Call self.assertEqual()

```python
self.assertEqual(computed_paths, expected_paths)
```

### Step 17: Assign weight = 0.0

```python
weight = 0.0
```

### Step 18: Assign edge = graph.get_edge_data(...)

```python
edge = graph.get_edge_data(path[i], path[i + 1])
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
nodes = graph.add_nodes_from([0, 1, 2, 3])
graph.add_edge(nodes[0], nodes[1], 0.0)
graph.add_edge(nodes[0], nodes[2], 1.0)
graph.add_edge(nodes[1], nodes[3], 1.0)
graph.add_edge(nodes[2], nodes[3], 0.0)
source = nodes[0]
shortest_lengths = rustworkx.digraph_dijkstra_shortest_path_lengths(graph, source, lambda e: e)
all_shortest_paths = rustworkx.digraph_single_source_all_shortest_paths(graph, source)
for target in nodes:
    target_idx = target
    if target_idx == source:
        continue
    all_paths = rustworkx.all_simple_paths(graph, source, target_idx)

    def path_weight(path):
        weight = 0.0
        for i in range(len(path) - 1):
            edge = graph.get_edge_data(path[i], path[i + 1])
            weight += edge
        return weight
    expected_paths = [path for path in all_paths if path_weight(path) == shortest_lengths[target_idx]]
    computed_paths = all_shortest_paths.get(target_idx, [])
    expected_paths.sort()
    computed_paths.sort()
    self.assertEqual(computed_paths, expected_paths)
```

## Next Steps


---

*Source: test_digraph_single_source_all_shortest_paths.py:55 | Complexity: Advanced | Last updated: 2026-05-05*