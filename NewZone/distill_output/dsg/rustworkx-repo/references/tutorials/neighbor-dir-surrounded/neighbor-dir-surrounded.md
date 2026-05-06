# How To: Neighbor Dir Surrounded

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test neighbor dir surrounded

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
node_c = dag.add_child(node_b, 'c', {'a': 2})
```

### Step 5: Assign res = dag.adj_direction(...)

```python
res = dag.adj_direction(node_b, False)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual({node_c: {'a': 2}}, res)
```

### Step 7: Assign res = dag.adj_direction(...)

```python
res = dag.adj_direction(node_b, True)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual({node_a: {'a': 1}}, res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = dag.adj_direction(node_b, False)
self.assertEqual({node_c: {'a': 2}}, res)
res = dag.adj_direction(node_b, True)
self.assertEqual({node_a: {'a': 1}}, res)
```

## Next Steps


---

*Source: test_adj.py:43 | Complexity: Advanced | Last updated: 2026-05-05*