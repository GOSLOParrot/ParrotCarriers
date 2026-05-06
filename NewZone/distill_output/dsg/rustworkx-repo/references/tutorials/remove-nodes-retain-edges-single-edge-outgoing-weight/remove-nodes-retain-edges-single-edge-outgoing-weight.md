# How To: Remove Nodes Retain Edges Single Edge Outgoing Weight

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove nodes retain edges single edge outgoing weight

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

### Step 3: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', 'Edgy')
```

### Step 4: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
```

### Step 5: Call dag.remove_node_retain_edges()

```python
dag.remove_node_retain_edges(node_b, use_outgoing=True)
```

### Step 6: Assign res = dag.nodes(...)

```python
res = dag.nodes()
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(['a', 'c'], res)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual([0, 2], dag.node_indexes())
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue(dag.has_edge(node_a, node_c))
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(dag.get_all_edge_data(node_a, node_c), ['Edgy_mk2'])
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node_retain_edges(node_b, use_outgoing=True)
res = dag.nodes()
self.assertEqual(['a', 'c'], res)
self.assertEqual([0, 2], dag.node_indexes())
self.assertTrue(dag.has_edge(node_a, node_c))
self.assertEqual(dag.get_all_edge_data(node_a, node_c), ['Edgy_mk2'])
```

## Next Steps


---

*Source: test_nodes.py:107 | Complexity: Advanced | Last updated: 2026-05-05*