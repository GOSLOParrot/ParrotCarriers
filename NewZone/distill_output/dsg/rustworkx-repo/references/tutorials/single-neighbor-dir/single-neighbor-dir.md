# How To: Single Neighbor Dir

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test single neighbor dir

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
node_b = dag.add_child(node_a, 'b', {'a': 1})
```

### Step 4: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_a, 'c', {'a': 2})
```

### Step 5: Assign res = dag.adj_direction(...)

```python
res = dag.adj_direction(node_a, False)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
```

### Step 7: Assign res = dag.adj_direction(...)

```python
res = dag.adj_direction(node_a, True)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual({}, res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_a, 'c', {'a': 2})
res = dag.adj_direction(node_a, False)
self.assertEqual({node_b: {'a': 1}, node_c: {'a': 2}}, res)
res = dag.adj_direction(node_a, True)
self.assertEqual({}, res)
```

## Next Steps


---

*Source: test_adj.py:33 | Complexity: Advanced | Last updated: 2026-05-05*