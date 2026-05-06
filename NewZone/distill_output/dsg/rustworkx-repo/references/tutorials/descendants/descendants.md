# How To: Descendants

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test descendants

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

### Step 5: Assign res = rustworkx.descendants(...)

```python
res = rustworkx.descendants(dag, node_a)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual({node_b, node_c}, res)
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDAG()
node_a = dag.add_node('a')
node_b = dag.add_child(node_a, 'b', {'a': 1})
node_c = dag.add_child(node_b, 'c', {'a': 2})
res = rustworkx.descendants(dag, node_a)
self.assertEqual({node_b, node_c}, res)
```

## Next Steps


---

*Source: test_ancestors_descendants.py:49 | Complexity: Intermediate | Last updated: 2026-05-05*