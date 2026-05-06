# How To: Simple Graph Composition

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test simple graph composition

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
graph.add_edge(node_b, node_c, {'a': 2})
```

### Step 7: Assign graph_other = rustworkx.PyGraph(...)

```python
graph_other = rustworkx.PyGraph()
```

### Step 8: Assign node_d = graph_other.add_node(...)

```python
node_d = graph_other.add_node('d')
```

### Step 9: Assign node_e = graph_other.add_node(...)

```python
node_e = graph_other.add_node('e')
```

### Step 10: Call graph_other.add_edge()

```python
graph_other.add_edge(node_d, node_e, {'a': 3})
```

### Step 11: Assign res = graph.compose(...)

```python
res = graph.compose(graph_other, {node_c: (node_d, {'b': 1})})
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual({0: 3, 1: 4}, res)
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, {'a': 1})
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, {'a': 2})
graph_other = rustworkx.PyGraph()
node_d = graph_other.add_node('d')
node_e = graph_other.add_node('e')
graph_other.add_edge(node_d, node_e, {'a': 3})
res = graph.compose(graph_other, {node_c: (node_d, {'b': 1})})
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], graph.node_indexes())
```

## Next Steps


---

*Source: test_compose.py:19 | Complexity: Advanced | Last updated: 2026-05-05*