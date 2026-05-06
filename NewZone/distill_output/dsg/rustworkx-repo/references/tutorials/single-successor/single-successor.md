# How To: Single Successor

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test single successor

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

### Step 5: Call dag.add_child()

```python
dag.add_child(node_c, 'd', {'a': 1})
```

### Step 6: Assign res_even = dag.find_successors_by_edge(...)

```python
res_even = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 == 0)
```

### Step 7: Assign res_odd = dag.find_successors_by_edge(...)

```python
res_odd = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 != 0)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(['c'], res_even)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual([], res_odd)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag.add_child(node_c, 'd', {'a': 1})
res_even = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 == 0)
res_odd = dag.find_successors_by_edge(node_b, lambda x: x['a'] % 2 != 0)
self.assertEqual(['c'], res_even)
self.assertEqual([], res_odd)
```

## Next Steps


---

*Source: test_pred_succ.py:186 | Complexity: Advanced | Last updated: 2026-05-05*