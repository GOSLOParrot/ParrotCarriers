# How To: Clear Reuse

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test clear reuse

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
node_a = graph.add_node('a')
```

### Step 3: Assign node_b = graph.add_node(...)

```python
node_b = graph.add_node('b')
```

### Step 4: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, {'a': 1})
```

### Step 5: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_a, node_c, {'a': 2})
```

### Step 7: Call graph.clear()

```python
graph.clear()
```

### Step 8: Assign node_a = graph.add_node(...)

```python
node_a = graph.add_node('a')
```

### Step 9: Assign node_b = graph.add_node(...)

```python
node_b = graph.add_node('b')
```

### Step 10: Call graph.add_edge()

```python
graph.add_edge(node_a, node_b, {'a': 1})
```

### Step 11: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 12: Call graph.add_edge()

```python
graph.add_edge(node_a, node_c, {'a': 2})
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual(graph.num_nodes(), 3)
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(graph.num_edges(), 2)
```

### Step 15: Call self.assertEqual()

```python
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
```

### Step 16: Call self.assertEqual()

```python
self.assertEqual(graph.edges(), [{'a': 1}, {'a': 2}])
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
graph.clear()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_a, node_c, {'a': 2})
self.assertEqual(graph.num_nodes(), 3)
self.assertEqual(graph.num_edges(), 2)
self.assertEqual(graph.nodes(), ['a', 'b', 'c'])
self.assertEqual(graph.edges(), [{'a': 1}, {'a': 2}])
```

## Next Steps


---

*Source: test_clear.py:32 | Complexity: Advanced | Last updated: 2026-05-05*