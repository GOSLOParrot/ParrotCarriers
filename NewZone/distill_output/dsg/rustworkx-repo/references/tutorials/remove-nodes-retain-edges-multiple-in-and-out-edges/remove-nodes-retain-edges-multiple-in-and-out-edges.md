# How To: Remove Nodes Retain Edges Multiple In And Out Edges

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove nodes retain edges multiple in and out edges

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

### Step 4: Assign node_e = dag.add_node(...)

```python
node_e = dag.add_node('e')
```

### Step 5: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', 'Edgy')
```

### Step 6: Call dag.add_edge()

```python
dag.add_edge(node_b, node_d, 'Multiple out edgy')
```

### Step 7: Call dag.add_edge()

```python
dag.add_edge(node_e, node_b, 'multiple in edgy')
```

### Step 8: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
```

### Step 9: Call dag.remove_node_retain_edges()

```python
dag.remove_node_retain_edges(node_b)
```

### Step 10: Assign res = dag.nodes(...)

```python
res = dag.nodes()
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(['a', 'd', 'e', 'c'], res)
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual([0, 1, 2, 4], dag.node_indexes())
```

### Step 13: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_a, node_c))
```

### Step 14: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_a, node_d))
```

### Step 15: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_e, node_c))
```

### Step 16: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_e, node_d))
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_d = dag.add_node('d')
node_e = dag.add_node('e')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_edge(node_b, node_d, 'Multiple out edgy')
dag.add_edge(node_e, node_b, 'multiple in edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b)
res = dag.nodes()
self.assertEqual(['a', 'd', 'e', 'c'], res)
self.assertEqual([0, 1, 2, 4], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertTrue(dag.has_edge(node_a, node_d))
self.assertTrue(dag.has_edge(node_e, node_c))
self.assertTrue(dag.has_edge(node_e, node_d))
```

## Next Steps


---

*Source: test_nodes.py:147 | Complexity: Advanced | Last updated: 2026-05-05*