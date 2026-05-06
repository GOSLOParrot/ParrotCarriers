# How To: Subgraph With Nodemap Edge Cases

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test subgraph with nodemap edge cases

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
graph.add_nodes_from(['a', 'b', 'c'])
```

### Step 3: Call graph.add_edges_from()

```python
graph.add_edges_from([(0, 1, 1), (1, 2, 2)])
```

### Step 4: Assign unknown = graph.subgraph_with_nodemap(...)

```python
subgraph, node_map = graph.subgraph_with_nodemap([])
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual([], subgraph.weighted_edge_list())
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(0, len(subgraph))
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(dict(node_map), {})
```

### Step 8: Assign unknown = graph.subgraph_with_nodemap(...)

```python
subgraph, node_map = graph.subgraph_with_nodemap([42, 100])
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual([], subgraph.weighted_edge_list())
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(0, len(subgraph))
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(dict(node_map), {})
```

### Step 12: Assign unknown = graph.subgraph_with_nodemap(...)

```python
subgraph, node_map = graph.subgraph_with_nodemap([1])
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual([], subgraph.weighted_edge_list())
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(['b'], subgraph.nodes())
```

### Step 15: Call self.assertEqual()

```python
self.assertEqual(dict(node_map), {0: 1})
```

### Step 16: Assign unknown = graph.subgraph_with_nodemap(...)

```python
subgraph, node_map = graph.subgraph_with_nodemap([0, 1, 2])
```

### Step 17: Call self.assertEqual()

```python
self.assertEqual([(0, 1, 1), (1, 2, 2)], subgraph.weighted_edge_list())
```

### Step 18: Call self.assertEqual()

```python
self.assertEqual(['a', 'b', 'c'], subgraph.nodes())
```

### Step 19: Call self.assertEqual()

```python
self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
graph.add_nodes_from(['a', 'b', 'c'])
graph.add_edges_from([(0, 1, 1), (1, 2, 2)])
subgraph, node_map = graph.subgraph_with_nodemap([])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([42, 100])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(0, len(subgraph))
self.assertEqual(dict(node_map), {})
subgraph, node_map = graph.subgraph_with_nodemap([1])
self.assertEqual([], subgraph.weighted_edge_list())
self.assertEqual(['b'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 1})
subgraph, node_map = graph.subgraph_with_nodemap([0, 1, 2])
self.assertEqual([(0, 1, 1), (1, 2, 2)], subgraph.weighted_edge_list())
self.assertEqual(['a', 'b', 'c'], subgraph.nodes())
self.assertEqual(dict(node_map), {0: 0, 1: 1, 2: 2})
```

## Next Steps


---

*Source: test_subgraph.py:183 | Complexity: Advanced | Last updated: 2026-05-05*