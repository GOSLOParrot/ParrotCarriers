# How To: Deepcopy Returns Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test deepcopy returns graph

## Prerequisites

**Required Modules:**
- `copy`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag_a = rustworkx.PyGraph(...)

```python
dag_a = rustworkx.PyGraph()
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

### Step 7: Assign dag_b = copy.deepcopy(...)

```python
dag_b = copy.deepcopy(dag_a)
```

### Step 8: Call self.assertIsInstance()

```python
self.assertIsInstance(dag_b, rustworkx.PyGraph)
```


## Complete Example

```python
# Workflow
dag_a = rustworkx.PyGraph()
node_a = dag_a.add_node('a_1')
node_b = dag_a.add_node('a_2')
dag_a.add_edge(node_a, node_b, 'edge_1')
node_c = dag_a.add_node('a_3')
dag_a.add_edge(node_b, node_c, 'edge_2')
dag_b = copy.deepcopy(dag_a)
self.assertIsInstance(dag_b, rustworkx.PyGraph)
```

## Next Steps


---

*Source: test_deepcopy.py:20 | Complexity: Advanced | Last updated: 2026-05-05*