# How To: Vf2Pp Remapping

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test vf2pp remapping

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign temp = rustworkx.generators.grid_graph(...)

```python
temp = rustworkx.generators.grid_graph(3, 3)
```

### Step 2: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 3: Assign dummy = graph.add_node(...)

```python
dummy = graph.add_node(0)
```

### Step 4: Call graph.compose()

```python
graph.compose(temp, dict())
```

### Step 5: Call graph.remove_node()

```python
graph.remove_node(dummy)
```

### Step 6: Assign second_graph = rustworkx.generators.grid_graph(...)

```python
second_graph = rustworkx.generators.grid_graph(2, 2)
```

### Step 7: Assign mapping = rustworkx.graph_vf2_mapping(...)

```python
mapping = rustworkx.graph_vf2_mapping(graph, second_graph, subgraph=True, id_order=False)
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(next(mapping), {5: 0, 4: 2, 1: 3, 2: 1})
```


## Complete Example

```python
# Workflow
temp = rustworkx.generators.grid_graph(3, 3)
graph = rustworkx.PyGraph()
dummy = graph.add_node(0)
graph.compose(temp, dict())
graph.remove_node(dummy)
second_graph = rustworkx.generators.grid_graph(2, 2)
mapping = rustworkx.graph_vf2_mapping(graph, second_graph, subgraph=True, id_order=False)
self.assertEqual(next(mapping), {5: 0, 4: 2, 1: 3, 2: 1})
```

## Next Steps


---

*Source: test_subgraph_isomorphic.py:265 | Complexity: Advanced | Last updated: 2026-05-05*