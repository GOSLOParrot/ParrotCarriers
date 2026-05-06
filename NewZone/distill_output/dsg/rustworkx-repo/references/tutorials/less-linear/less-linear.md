# How To: Less Linear

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test less linear

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
node_b = dag.add_child(node_a, 'b', {})
```

### Step 4: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', {})
```

### Step 5: Assign node_d = dag.add_child(...)

```python
node_d = dag.add_child(node_c, 'd', {})
```

### Step 6: Assign node_e = dag.add_child(...)

```python
node_e = dag.add_child(node_d, 'e', {})
```

### Step 7: Call dag.add_edge()

```python
dag.add_edge(node_a, node_c, {})
```

### Step 8: Call dag.add_edge()

```python
dag.add_edge(node_a, node_e, {})
```

### Step 9: Call dag.add_edge()

```python
dag.add_edge(node_c, node_e, {})
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual([node_a, node_b, node_c, node_d, node_e], rustworkx.dag_longest_path(dag))
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
node_c = dag.add_child(node_b, 'c', {})
node_d = dag.add_child(node_c, 'd', {})
node_e = dag.add_child(node_d, 'e', {})
dag.add_edge(node_a, node_c, {})
dag.add_edge(node_a, node_e, {})
dag.add_edge(node_c, node_e, {})
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
self.assertEqual([node_a, node_b, node_c, node_d, node_e], rustworkx.dag_longest_path(dag))
```

## Next Steps


---

*Source: test_depth.py:46 | Complexity: Advanced | Last updated: 2026-05-05*