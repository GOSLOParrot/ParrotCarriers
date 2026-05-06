# How To: Remove Nodes Retain Edges Multiple In Edges

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove nodes retain edges multiple in edges

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 3: Assign node_d = dag.add_node(...)

```python
node_d = dag.add_node('d')
```

### Step 4: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', 'Edgy')
```

### Step 5: Call dag.add_edge()

```python
dag.add_edge(node_d, node_b, 'Multiple in edgy')
```

### Step 6: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
```

### Step 7: Call dag.remove_node_retain_edges()

```python
dag.remove_node_retain_edges(node_b)
```

### Step 8: Assign res = dag.nodes(...)

```python
res = dag.nodes()
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(['a', 'd', 'c'], res)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual([0, 1, 3], dag.node_indexes())
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_a, node_c))
```

### Step 12: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_d, node_c))
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_d = dag.add_node('d')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_d, node_b, 'Multiple in edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b)
res = dag.nodes()
self.assertEqual(['a', 'd', 'c'], res)
self.assertEqual([0, 1, 3], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertTrue(dag.has_edge(node_d, node_c))
```

## Next Steps


---

*Source: test_nodes.py:119 | Complexity: Advanced | Last updated: 2026-05-05*