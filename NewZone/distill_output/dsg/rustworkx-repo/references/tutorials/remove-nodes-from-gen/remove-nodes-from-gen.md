# How To: Remove Nodes From Gen

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove nodes from gen

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Assign node_a = graph.add_node(...)

```python
node_a = graph.add_node('a')
```

### Step 3: Assign node_b = graph.add_child(...)

```python
node_b = graph.add_child(node_a, 'b', 'Edgy')
```

### Step 4: Assign node_c = graph.add_child(...)

```python
node_c = graph.add_child(node_b, 'c', 'Edgy_mk2')
```

### Step 5: Call graph.remove_nodes_from()

```python
graph.remove_nodes_from((n for n in [node_b, node_c]))
```

### Step 6: Assign res = graph.nodes(...)

```python
res = graph.nodes()
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(['a'], res)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual([0], graph.node_indexes())
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
node_a = graph.add_node('a')
node_b = graph.add_child(node_a, 'b', 'Edgy')
node_c = graph.add_child(node_b, 'c', 'Edgy_mk2')
graph.remove_nodes_from((n for n in [node_b, node_c]))
res = graph.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], graph.node_indexes())
```

## Next Steps


---

*Source: test_nodes.py:69 | Complexity: Advanced | Last updated: 2026-05-05*