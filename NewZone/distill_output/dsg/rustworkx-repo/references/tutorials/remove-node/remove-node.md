# How To: Remove Node

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test remove node

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

### Step 4: Call dag.add_child()

```python
dag.add_child(node_b, 'c', 'Edgy_mk2')
```

### Step 5: Call dag.remove_node()

```python
dag.remove_node(node_b)
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


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 'Edgy')
dag.add_child(node_b, 'c', 'Edgy_mk2')
dag.remove_node(node_b)
res = dag.nodes()
self.assertEqual(['a', 'c'], res)
self.assertEqual([0, 2], dag.node_indexes())
```

## Next Steps


---

*Source: test_nodes.py:39 | Complexity: Advanced | Last updated: 2026-05-05*