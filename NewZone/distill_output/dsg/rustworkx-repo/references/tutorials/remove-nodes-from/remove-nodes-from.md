# How To: Remove Nodes From

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove nodes from

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

### Step 5: Call dag.remove_nodes_from()

```python
dag.remove_nodes_from([node_b, node_c])
```

### Step 6: Assign res = dag.nodes(...)

```python
res = dag.nodes()
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(['a'], res)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual([0], dag.node_indexes())
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
node_c = dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_nodes_from([node_b, node_c])
res = dag.nodes()
self.assertEqual(['a'], res)
self.assertEqual([0], dag.node_indexes())
```

## Next Steps


---

*Source: test_nodes.py:59 | Complexity: Advanced | Last updated: 2026-05-05*