# How To: Simple Dag Composition

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test simple dag composition

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 2: Assign dag.check_cycle = True

```python
dag.check_cycle = True
```

### Step 3: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 4: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', {'a': 1})
```

### Step 5: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', {'a': 2})
```

### Step 6: Assign dag_other = rustworkx.PyDAG(...)

```python
dag_other = rustworkx.PyDAG()
```

### Step 7: Assign node_d = dag_other.add_node(...)

```python
node_d = dag_other.add_node('d')
```

### Step 8: Call dag_other.add_child()

```python
dag_other.add_child(node_d, 'e', {'a': 3})
```

### Step 9: Assign res = dag.compose(...)

```python
res = dag.compose(dag_other, {node_c: (node_d, {'b': 1})})
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual({0: 3, 1: 4}, res)
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
dag.check_cycle = True
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
dag_other = rustworkx.PyDAG()
node_d = dag_other.add_node('d')
dag_other.add_child(node_d, 'e', {'a': 3})
res = dag.compose(dag_other, {node_c: (node_d, {'b': 1})})
self.assertEqual({0: 3, 1: 4}, res)
self.assertEqual([0, 1, 2, 3, 4], rustworkx.topological_sort(dag))
```

## Next Steps


---

*Source: test_compose.py:19 | Complexity: Advanced | Last updated: 2026-05-05*