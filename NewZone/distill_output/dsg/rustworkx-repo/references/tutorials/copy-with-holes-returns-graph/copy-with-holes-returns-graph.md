# How To: Copy With Holes Returns Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test copy with holes returns graph

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_a = rustworkx.PyGraph(...)

```python
graph_a = rustworkx.PyGraph()
```

### Step 2: Assign node_a = graph_a.add_node(...)

```python
node_a = graph_a.add_node('a_1')
```

### Step 3: Assign node_b = graph_a.add_node(...)

```python
node_b = graph_a.add_node('a_2')
```

### Step 4: Call graph_a.add_edge()

```python
graph_a.add_edge(node_a, node_b, 'edge_1')
```

### Step 5: Assign node_c = graph_a.add_node(...)

```python
node_c = graph_a.add_node('a_3')
```

### Step 6: Call graph_a.add_edge()

```python
graph_a.add_edge(node_b, node_c, 'edge_2')
```

### Step 7: Call graph_a.remove_node()

```python
graph_a.remove_node(node_b)
```

### Step 8: Assign graph_b = graph_a.copy(...)

```python
graph_b = graph_a.copy()
```

### Step 9: Call self.assertIsInstance()

```python
self.assertIsInstance(graph_b, rustworkx.PyGraph)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```


## Complete Example

```python
# Workflow
graph_a = rustworkx.PyGraph()
node_a = graph_a.add_node('a_1')
node_b = graph_a.add_node('a_2')
graph_a.add_edge(node_a, node_b, 'edge_1')
node_c = graph_a.add_node('a_3')
graph_a.add_edge(node_b, node_c, 'edge_2')
graph_a.remove_node(node_b)
graph_b = graph_a.copy()
self.assertIsInstance(graph_b, rustworkx.PyGraph)
self.assertEqual([node_a, node_c], graph_b.node_indexes())
```

## Next Steps


---

*Source: test_copy.py:29 | Complexity: Advanced | Last updated: 2026-05-05*