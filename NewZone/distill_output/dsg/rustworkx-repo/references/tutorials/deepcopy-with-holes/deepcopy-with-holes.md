# How To: Deepcopy With Holes

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test deepcopy with holes

## Prerequisites

**Required Modules:**
- `copy`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag_a = rustworkx.PyDAG(...)

```python
dag_a = rustworkx.PyDAG()
```

### Step 2: Assign node_a = dag_a.add_node(...)

```python
node_a = dag_a.add_node('a_1')
```

### Step 3: Assign node_b = dag_a.add_node(...)

```python
node_b = dag_a.add_node('a_2')
```

### Step 4: Call dag_a.add_edge()

```python
dag_a.add_edge(node_a, node_b, 'edge_1')
```

### Step 5: Assign node_c = dag_a.add_node(...)

```python
node_c = dag_a.add_node('a_3')
```

### Step 6: Call dag_a.add_edge()

```python
dag_a.add_edge(node_b, node_c, 'edge_2')
```

### Step 7: Call dag_a.remove_node()

```python
dag_a.remove_node(node_b)
```

### Step 8: Assign dag_b = copy.deepcopy(...)

```python
dag_b = copy.deepcopy(dag_a)
```

### Step 9: Call self.assertIsInstance()

```python
self.assertIsInstance(dag_b, rustworkx.PyDAG)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```


## Complete Example

```python
# Workflow
dag_a = rustworkx.PyDAG()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_a.remove_node(node_b)
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyDAG)
self.assertEqual([node_a, node_c], dag_b.node_indexes())
```

## Next Steps


---

*Source: test_deepcopy.py:28 | Complexity: Advanced | Last updated: 2026-05-05*