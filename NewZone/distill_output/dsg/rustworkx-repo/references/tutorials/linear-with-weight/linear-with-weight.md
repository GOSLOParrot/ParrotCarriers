# How To: Linear With Weight

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Longest depth for a simple dag.

a
|
b
|        c d
|        e |
| |
f g

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: 'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '

```python
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
```

### Step 2: Assign dag = rustworkx.PyDAG(...)

```python
dag = rustworkx.PyDAG()
```

### Step 3: Assign node_a = dag.add_node(...)

```python
node_a = dag.add_node('a')
```

### Step 4: Assign node_b = dag.add_child(...)

```python
node_b = dag.add_child(node_a, 'b', 4)
```

### Step 5: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', 4)
```

### Step 6: Call dag.add_child()

```python
dag.add_child(node_b, 'd', 5)
```

### Step 7: Assign node_e = dag.add_child(...)

```python
node_e = dag.add_child(node_c, 'e', 2)
```

### Step 8: Call dag.add_child()

```python
dag.add_child(node_e, 'f', 2)
```

### Step 9: Assign node_g = dag.add_child(...)

```python
node_g = dag.add_child(node_c, 'g', 15)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual([node_a, node_b, node_c, node_g], rustworkx.dag_longest_path(dag, lambda _, __, weight: weight))
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(23, rustworkx.dag_longest_path_length(dag, lambda _, __, weight: weight))
```


## Complete Example

```python
# Workflow
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', 4)
node_c = dag.add_child(node_b, 'c', 4)
dag.add_child(node_b, 'd', 5)
node_e = dag.add_child(node_c, 'e', 2)
dag.add_child(node_e, 'f', 2)
node_g = dag.add_child(node_c, 'g', 15)
self.assertEqual([node_a, node_b, node_c, node_g], rustworkx.dag_longest_path(dag, lambda _, __, weight: weight))
self.assertEqual(23, rustworkx.dag_longest_path_length(dag, lambda _, __, weight: weight))
```

## Next Steps


---

*Source: test_depth.py:90 | Complexity: Advanced | Last updated: 2026-05-05*