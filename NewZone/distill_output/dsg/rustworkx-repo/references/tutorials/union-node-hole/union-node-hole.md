# How To: Union Node Hole

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test union node hole

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign first = rustworkx.PyGraph(...)

```python
first = rustworkx.PyGraph()
```

### Step 2: Assign nodes = first.add_nodes_from(...)

```python
nodes = first.add_nodes_from([0, 1])
```

### Step 3: Call first.add_edges_from()

```python
first.add_edges_from([(nodes[0], nodes[1], 'a')])
```

### Step 4: Assign second = rustworkx.PyGraph(...)

```python
second = rustworkx.PyGraph()
```

### Step 5: Assign dummy = second.add_node(...)

```python
dummy = second.add_node('dummy')
```

### Step 6: Assign nodes = second.add_nodes_from(...)

```python
nodes = second.add_nodes_from([0, 1])
```

### Step 7: Call second.add_edges_from()

```python
second.add_edges_from([(nodes[0], nodes[1], 'a')])
```

### Step 8: Call second.remove_node()

```python
second.remove_node(dummy)
```

### Step 9: Assign final = rustworkx.graph_union(...)

```python
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])
```


## Complete Example

```python
# Workflow
first = rustworkx.PyGraph()
nodes = first.add_nodes_from([0, 1])
first.add_edges_from([(nodes[0], nodes[1], 'a')])
second = rustworkx.PyGraph()
dummy = second.add_node('dummy')
nodes = second.add_nodes_from([0, 1])
second.add_edges_from([(nodes[0], nodes[1], 'a')])
second.remove_node(dummy)
final = rustworkx.graph_union(first, second, merge_nodes=True, merge_edges=True)
self.assertEqual(final.weighted_edge_list(), [(0, 1, 'a')])
```

## Next Steps


---

*Source: test_union.py:50 | Complexity: Advanced | Last updated: 2026-05-05*