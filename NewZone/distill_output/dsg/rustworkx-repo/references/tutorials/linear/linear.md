# How To: Linear

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
node_b = dag.add_child(node_a, 'b', {})
```

### Step 5: Assign node_c = dag.add_child(...)

```python
node_c = dag.add_child(node_b, 'c', {})
```

### Step 6: Call dag.add_child()

```python
dag.add_child(node_b, 'd', {})
```

### Step 7: Assign node_e = dag.add_child(...)

```python
node_e = dag.add_child(node_c, 'e', {})
```

### Step 8: Assign node_f = dag.add_child(...)

```python
node_f = dag.add_child(node_e, 'f', {})
```

### Step 9: Call dag.add_child()

```python
dag.add_child(node_c, 'g', {})
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual([node_a, node_b, node_c, node_e, node_f], rustworkx.dag_longest_path(dag))
```


## Complete Example

```python
# Workflow
'Longest depth for a simple dag.\n\n        a\n        |\n        b\n        |        c d\n        |        e |\n        | |\n        f g\n        '
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {})
node_c = dag.add_child(node_b, 'c', {})
dag.add_child(node_b, 'd', {})
node_e = dag.add_child(node_c, 'e', {})
node_f = dag.add_child(node_e, 'f', {})
dag.add_child(node_c, 'g', {})
self.assertEqual(4, rustworkx.dag_longest_path_length(dag))
self.assertEqual([node_a, node_b, node_c, node_e, node_f], rustworkx.dag_longest_path(dag))
```

## Next Steps


---

*Source: test_depth.py:19 | Complexity: Advanced | Last updated: 2026-05-05*