# How To: Graph To Dot To File

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test graph to dot to file

## Prerequisites

**Required Modules:**
- `os`
- `tempfile`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Call graph.add_node()

```python
graph.add_node({'color': 'black', 'fillcolor': 'green', 'label': 'a', 'style': 'filled'})
```

### Step 3: Call graph.add_node()

```python
graph.add_node({'color': 'black', 'fillcolor': 'red', 'label': 'a', 'style': 'filled'})
```

### Step 4: Call graph.add_edge()

```python
graph.add_edge(0, 1, dict(label='1', name='1'))
```

### Step 5: Assign expected = 'graph {\n0 [color=black, fillcolor=green, label="a", style=filled];\n1 [color=black, fillcolor=red, label="a", style=filled];\n0 -- 1 [label="1", name=1];\n}\n'

```python
expected = 'graph {\n0 [color=black, fillcolor=green, label="a", style=filled];\n1 [color=black, fillcolor=red, label="a", style=filled];\n0 -- 1 [label="1", name=1];\n}\n'
```

### Step 6: Assign res = graph.to_dot(...)

```python
res = graph.to_dot(lambda node: node, lambda edge: edge, filename=self.path)
```

### Step 7: Call self.addCleanup()

```python
self.addCleanup(os.remove, self.path)
```

### Step 8: Call self.assertIsNone()

```python
self.assertIsNone(res)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(expected, res)
```

### Step 10: Assign res = fd.read(...)

```python
res = fd.read()
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
graph.add_node({'color': 'black', 'fillcolor': 'green', 'label': 'a', 'style': 'filled'})
graph.add_node({'color': 'black', 'fillcolor': 'red', 'label': 'a', 'style': 'filled'})
graph.add_edge(0, 1, dict(label='1', name='1'))
expected = 'graph {\n0 [color=black, fillcolor=green, label="a", style=filled];\n1 [color=black, fillcolor=red, label="a", style=filled];\n0 -- 1 [label="1", name=1];\n}\n'
res = graph.to_dot(lambda node: node, lambda edge: edge, filename=self.path)
self.addCleanup(os.remove, self.path)
self.assertIsNone(res)
with open(self.path) as fd:
    res = fd.read()
self.assertEqual(expected, res)
```

## Next Steps


---

*Source: test_dot.py:80 | Complexity: Advanced | Last updated: 2026-05-05*