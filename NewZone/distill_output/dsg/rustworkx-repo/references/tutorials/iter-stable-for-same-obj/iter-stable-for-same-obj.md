# How To: Iter Stable For Same Obj

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test iter stable for same obj

## Prerequisites

**Required Modules:**
- `copy`
- `pickle`
- `unittest`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyDiGraph(...)

```python
graph = rustworkx.PyDiGraph()
```

### Step 2: Call graph.add_node()

```python
graph.add_node(0)
```

### Step 3: Assign in_graph = rustworkx.generators.directed_path_graph(...)

```python
in_graph = rustworkx.generators.directed_path_graph(5)
```

### Step 4: Assign res = self.dag.substitute_node_with_subgraph(...)

```python
res = self.dag.substitute_node_with_subgraph(0, in_graph, lambda *args: None)
```

### Step 5: Assign first_iter = list(...)

```python
first_iter = list(iter(res))
```

### Step 6: Assign second_iter = list(...)

```python
second_iter = list(iter(res))
```

### Step 7: Assign third_iter = list(...)

```python
third_iter = list(iter(res))
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(first_iter, second_iter)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(first_iter, third_iter)
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyDiGraph()
graph.add_node(0)
in_graph = rustworkx.generators.directed_path_graph(5)
res = self.dag.substitute_node_with_subgraph(0, in_graph, lambda *args: None)
first_iter = list(iter(res))
second_iter = list(iter(res))
third_iter = list(iter(res))
self.assertEqual(first_iter, second_iter)
self.assertEqual(first_iter, third_iter)
```

## Next Steps


---

*Source: test_custom_return_types.py:1367 | Complexity: Advanced | Last updated: 2026-05-05*