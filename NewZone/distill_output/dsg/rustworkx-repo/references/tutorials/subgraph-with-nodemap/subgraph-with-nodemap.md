# How To: Subgraph With Nodemap

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test subgraph with nodemap

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Call graph.add_nodes_from()

```python
graph.add_nodes_from(list(range(6)))
```

### Step 3: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (1, 4), (2, 5)])
```

### Step 4: Assign unknown = graph.subgraph_with_nodemap(...)

```python
subgraph, node_map = graph.subgraph_with_nodemap([1, 2, 4])
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(set(subgraph.node_indices()), {0, 1, 2})
```

### Step 6: Assign edge_list = list(...)

```python
edge_list = list(subgraph.edge_list())
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(len(edge_list), 2)
```

### Step 8: Call self.assertIn()

```python
self.assertIn((0, 1), edge_list)
```

### Step 9: Call self.assertIn()

```python
self.assertIn((0, 2), edge_list)
```

### Step 10: Assign node_map_dict = dict(...)

```python
node_map_dict = dict(node_map)
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(len(node_map_dict), 3)
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual(set(node_map_dict.values()), {1, 2, 4})
```

### Step 13: Assign graph2 = rustworkx.PyGraph(...)

```python
graph2 = rustworkx.PyGraph()
```

### Step 14: Call graph2.add_nodes_from()

```python
graph2.add_nodes_from(['a', 'b', 'c', 'd', 'e'])
```

### Step 15: Call graph2.add_edges_from()

```python
graph2.add_edges_from([(0, 1, 1), (2, 3, 2)])
```

### Step 16: Assign unknown = graph2.subgraph_with_nodemap(...)

```python
subgraph, node_map = graph2.subgraph_with_nodemap([0, 2, 4])
```

### Step 17: Call self.assertEqual()

```python
self.assertEqual([], subgraph.weighted_edge_list())
```

### Step 18: Call self.assertEqual()

```python
self.assertEqual(['a', 'c', 'e'], subgraph.nodes())
```

### Step 19: Call self.assertEqual()

```python
self.assertEqual(dict(node_map), {0: 0, 1: 2, 2: 4})
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
graph.add_nodes_from(list(range(6)))
graph.extend_from_edge_list([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (1, 4), (2, 5)])
subgraph, node_map = graph.subgraph_with_nodemap([1, 2, 4])
self.assertEqual(set(subgraph.node_indices()), {0, 1, 2})
edge_list = list(subgraph.edge_list())
self.assertEqual(len(edge_list), 2)
self.assertIn((0, 1), edge_list)
self.assertIn((0, 2), edge_list)
node_map_dict = dict(node_map)
self.assertEqual(len(node_map_dict), 3)
self.assertEqual(set(node_map_dict.values()), {1, 2, 4})
graph2 = rustworkx.PyGraph()
graph2.add_nodes_from(['a', 'b', 'c', 'd', 'e'])
graph2.add_edges_from([(0, 1, 1), (2, 3, 2)])
subgraph, node_map = graph2.subgraph_with_nodemap([0, 2, 4])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['a', 'c', 'e'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 2, 2: 4})
```

## Next Steps


---

*Source: test_subgraph.py:152 | Complexity: Advanced | Last updated: 2026-05-05*