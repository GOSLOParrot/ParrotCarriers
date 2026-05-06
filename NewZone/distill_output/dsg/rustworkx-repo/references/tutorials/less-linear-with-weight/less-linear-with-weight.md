# How To: Less Linear With Weight

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test less linear with weight

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
node_b = dag.add_child(node_a, 'b', 1)
```

### Step 4: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', 1)
```

### Step 5: Assign node_d = dag.add_child(...)

```python
node_d = dag.add_child(node_c, 'd', 1)
```

### Step 6: Assign node_e = dag.add_child(...)

```python
node_e = dag.add_child(node_d, 'e', 1)
```

### Step 7: Call dag.add_edge()

```python
dag.add_edge(node_a, node_c, 3)
```

### Step 8: Call dag.add_edge()

```python
dag.add_edge(node_a, node_e, 3)
```

### Step 9: Call dag.add_edge()

```python
dag.add_edge(node_c, node_e, 3)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(6, rustworkx.dag_longest_path_length(dag, weight_fn=lambda _, __, weight: weight))
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual([node_a, node_c, node_e], rustworkx.dag_longest_path(dag, weight_fn=lambda _, __, weight: weight))
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 1)
node_c = dag.add_child(node_b, 'c', 1)
node_d = dag.add_child(node_c, 'd', 1)
node_e = dag.add_child(node_d, 'e', 1)
dag.add_edge(node_a, node_c, 3)
dag.add_edge(node_a, node_e, 3)
dag.add_edge(node_c, node_e, 3)
self.assertEqual(6, rustworkx.dag_longest_path_length(dag, weight_fn=lambda _, __, weight: weight))
self.assertEqual([node_a, node_c, node_e], rustworkx.dag_longest_path(dag, weight_fn=lambda _, __, weight: weight))
```

## Next Steps


---

*Source: test_depth.py:141 | Complexity: Advanced | Last updated: 2026-05-05*