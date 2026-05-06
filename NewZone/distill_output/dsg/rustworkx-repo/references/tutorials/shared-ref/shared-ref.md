# How To: Shared Ref

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test shared ref

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign digraph = rustworkx.PyDiGraph(...)

```python
digraph = rustworkx.PyDiGraph()
```

### Step 2: Assign node_weight = value

```python
node_weight = {'a': 1}
```

### Step 3: Assign node_a = digraph.add_node(...)

```python
node_a = digraph.add_node(node_weight)
```

### Step 4: Assign edge_weight = value

```python
edge_weight = {'a': 1}
```

### Step 5: Call digraph.add_child()

```python
digraph.add_child(node_a, 'b', edge_weight)
```

### Step 6: Assign graph = digraph.to_undirected(...)

```python
graph = digraph.to_undirected()
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(digraph[node_a], {'a': 1})
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(graph[node_a], {'a': 1})
```

### Step 9: Assign unknown = 2

```python
node_weight['b'] = 2
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
```

### Step 14: Assign unknown = 2

```python
edge_weight['b'] = 2
```

### Step 15: Call self.assertEqual()

```python
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

### Step 16: Call self.assertEqual()

```python
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```


## Complete Example

```python
# Workflow
digraph = rustworkx.PyDiGraph()
node_weight = {'a': 1}
node_a = digraph.add_node(node_weight)
edge_weight = {'a': 1}
digraph.add_child(node_a, 'b', edge_weight)
graph = digraph.to_undirected()
self.assertEqual(digraph[node_a], {'a': 1})
self.assertEqual(graph[node_a], {'a': 1})
node_weight['b'] = 2
self.assertEqual(digraph[node_a], {'a': 1, 'b': 2})
self.assertEqual(graph[node_a], {'a': 1, 'b': 2})
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1})
edge_weight['b'] = 2
self.assertEqual(digraph.get_edge_data(0, 1), {'a': 1, 'b': 2})
self.assertEqual(graph.get_edge_data(0, 1), {'a': 1, 'b': 2})
```

## Next Steps


---

*Source: test_to_undirected.py:50 | Complexity: Advanced | Last updated: 2026-05-05*