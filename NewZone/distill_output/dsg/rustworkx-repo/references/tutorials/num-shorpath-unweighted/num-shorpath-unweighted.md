# How To: Num Shorpath Unweighted

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test num shortest path unweighted

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Assign node_a = graph.add_node(...)

```python
node_a = graph.add_node(0)
```

### Step 3: Assign node_b = graph.add_node(...)

```python
node_b = graph.add_node('end')
```

### Step 4: Assign res = rustworkx.graph_num_shortest_paths_unweighted(...)

```python
res = rustworkx.graph_num_shortest_paths_unweighted(graph, node_a)
```

### Step 5: Assign expected = value

```python
expected = {2: 1, 4: 1, 3: 1, 1: 3}
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(expected, res)
```

### Step 7: Assign node = graph.add_node(...)

```python
node = graph.add_node(i)
```

### Step 8: Call graph.add_edge()

```python
graph.add_edge(node_a, node, None)
```

### Step 9: Call graph.add_edge()

```python
graph.add_edge(node, node_b, None)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node(0)
node_b = graph.add_node('end')
for i in range(3):
    node = graph.add_node(i)
    graph.add_edge(node_a, node, None)
    graph.add_edge(node, node_b, None)
res = rustworkx.graph_num_shortest_paths_unweighted(graph, node_a)
expected = {2: 1, 4: 1, 3: 1, 1: 3}
self.assertEqual(expected, res)
```

## Next Steps


---

*Source: test_num_shortest_path.py:19 | Complexity: Advanced | Last updated: 2026-05-05*