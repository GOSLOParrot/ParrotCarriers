# How To: Single Neighbor

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test single neighbor

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

### Step 7: Assign res = graph.neighbors(...)

```python
res = graph.neighbors(node_a)
```

### Step 8: Call self.assertCountEqual()

```python
self.assertCountEqual([node_c, node_b], res)
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
res = graph.neighbors(node_a)
self.assertCountEqual([node_c, node_b], res)
```

## Next Steps


---

*Source: test_neighbors.py:19 | Complexity: Advanced | Last updated: 2026-05-05*