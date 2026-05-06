# How To: Remove Node Delitem

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove node delitem

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
graph.add_edge(node_a, node_b, 'Edgy')
```

### Step 5: Assign node_c = graph.add_node(...)

```python
node_c = graph.add_node('c')
```

### Step 6: Call graph.add_edge()

```python
graph.add_edge(node_b, node_c, 'Edgy_mk2')
```

### Step 7: Assign res = graph.nodes(...)

```python
res = graph.nodes()
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(['a', 'c'], res)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual([0, 2], graph.node_indexes())
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
node_a = graph.add_node('a')
node_b = graph.add_node('b')
graph.add_edge(node_a, node_b, 'Edgy')
node_c = graph.add_node('c')
graph.add_edge(node_b, node_c, 'Edgy_mk2')
del graph[node_b]
res = graph.nodes()
self.assertEqual(['a', 'c'], res)
self.assertEqual([0, 2], graph.node_indexes())
```

## Next Steps


---

*Source: test_nodes.py:180 | Complexity: Advanced | Last updated: 2026-05-05*