# How To: Union Basic Merge None

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test union basic merge none

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag_a = rustworkx.PyDiGraph(...)

```python
dag_a = rustworkx.PyDiGraph()
```

### Step 2: Assign dag_b = rustworkx.PyDiGraph(...)

```python
dag_b = rustworkx.PyDiGraph()
```

### Step 3: Assign node_a = dag_a.add_node(...)

```python
node_a = dag_a.add_node('a_1')
```

### Step 4: Call dag_a.add_child()

```python
dag_a.add_child(node_a, 'a_2', 'e_1')
```

### Step 5: Call dag_a.add_child()

```python
dag_a.add_child(node_a, 'a_3', 'r_2')
```

### Step 6: Assign node_b = dag_b.add_node(...)

```python
node_b = dag_b.add_node('a_1')
```

### Step 7: Call dag_b.add_child()

```python
dag_b.add_child(node_b, 'a_2', 'e_1')
```

### Step 8: Call dag_b.add_child()

```python
dag_b.add_child(node_b, 'a_3', 'e_2')
```

### Step 9: Assign dag_c = rustworkx.digraph_union(...)

```python
dag_c = rustworkx.digraph_union(dag_a, dag_b, False, False)
```

### Step 10: Call self.assertTrue()

```python
self.assertTrue(len(dag_c.nodes()) == 6)
```

### Step 11: Call self.assertTrue()

```python
self.assertTrue(len(dag_c.edge_list()) == 4)
```


## Complete Example

```python
# Workflow
dag_a = rustworkx.PyDiGraph()
dag_b = rustworkx.PyDiGraph()
node_a = dag_a.add_node('a_1')
dag_a.add_child(node_a, 'a_2', 'e_1')
dag_a.add_child(node_a, 'a_3', 'r_2')
node_b = dag_b.add_node('a_1')
dag_b.add_child(node_b, 'a_2', 'e_1')
dag_b.add_child(node_b, 'a_3', 'e_2')
dag_c = rustworkx.digraph_union(dag_a, dag_b, False, False)
self.assertTrue(len(dag_c.nodes()) == 6)
self.assertTrue(len(dag_c.edge_list()) == 4)
```

## Next Steps


---

*Source: test_union.py:52 | Complexity: Advanced | Last updated: 2026-05-05*