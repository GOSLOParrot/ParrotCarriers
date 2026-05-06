# How To: Write Edge List Round Trip

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test write edge list round trip

## Prerequisites

**Required Modules:**
- `os`
- `tempfile`
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign path = os.path.join(...)

```python
path = os.path.join(tempfile.gettempdir(), 'round_trip.txt')
```

### Step 2: Assign graph = rustworkx.generators.directed_star_graph(...)

```python
graph = rustworkx.generators.directed_star_graph(5)
```

### Step 3: Assign count = iter(...)

```python
count = iter(range(5))
```

### Step 4: Call graph.write_edge_list()

```python
graph.write_edge_list(path, weight_fn=weight_fn)
```

### Step 5: Call self.addCleanup()

```python
self.addCleanup(os.remove, path)
```

### Step 6: Assign new_graph = rustworkx.PyDiGraph.read_edge_list(...)

```python
new_graph = rustworkx.PyDiGraph.read_edge_list(path)
```

### Step 7: Assign expected = value

```python
expected = [(0, 1, '0'), (0, 2, '1'), (0, 3, '2'), (0, 4, '3')]
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(expected, new_graph.weighted_edge_list())
```


## Complete Example

```python
# Workflow
path = os.path.join(tempfile.gettempdir(), 'round_trip.txt')
graph = rustworkx.generators.directed_star_graph(5)
count = iter(range(5))

def weight_fn(edge):
    return str(next(count))
graph.write_edge_list(path, weight_fn=weight_fn)
self.addCleanup(os.remove, path)
new_graph = rustworkx.PyDiGraph.read_edge_list(path)
expected = [(0, 1, '0'), (0, 2, '1'), (0, 3, '2'), (0, 4, '3')]
self.assertEqual(expected, new_graph.weighted_edge_list())
```

## Next Steps


---

*Source: test_edgelist.py:189 | Complexity: Advanced | Last updated: 2026-05-05*