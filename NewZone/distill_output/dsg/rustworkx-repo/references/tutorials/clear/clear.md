# How To: Clear

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test clear

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

### Step 8: Call self.assertEqual()

```python
self.assertEqual(graph.num_nodes(), 0)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(graph.num_edges(), 0)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(graph.nodes(), [])
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(graph.edges(), [])
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
self.assertEqual(graph.num_nodes(), 0)
self.assertEqual(graph.num_edges(), 0)
self.assertEqual(graph.nodes(), [])
self.assertEqual(graph.edges(), [])
```

## Next Steps


---

*Source: test_clear.py:19 | Complexity: Advanced | Last updated: 2026-05-05*