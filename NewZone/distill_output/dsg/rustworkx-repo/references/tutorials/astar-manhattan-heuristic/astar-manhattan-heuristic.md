# How To: Astar Manhattan Heuristic

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test astar manhattan heuristic

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign g = rustworkx.PyDAG(...)

```python
g = rustworkx.PyDAG()
```

### Step 2: Assign a = g.add_node(...)

```python
a = g.add_node((0.0, 0.0))
```

### Step 3: Assign b = g.add_node(...)

```python
b = g.add_node((2.0, 0.0))
```

### Step 4: Assign c = g.add_node(...)

```python
c = g.add_node((1.0, 1.0))
```

### Step 5: Assign d = g.add_node(...)

```python
d = g.add_node((0.0, 2.0))
```

### Step 6: Assign e = g.add_node(...)

```python
e = g.add_node((3.0, 3.0))
```

### Step 7: Assign f = g.add_node(...)

```python
f = g.add_node((4.0, 2.0))
```

### Step 8: Assign no_path = g.add_node(...)

```python
no_path = g.add_node((5.0, 5.0))
```

### Step 9: Call g.add_edge()

```python
g.add_edge(a, b, 2.0)
```

### Step 10: Call g.add_edge()

```python
g.add_edge(a, d, 4.0)
```

### Step 11: Call g.add_edge()

```python
g.add_edge(b, c, 1.0)
```

### Step 12: Call g.add_edge()

```python
g.add_edge(b, f, 7.0)
```

### Step 13: Call g.add_edge()

```python
g.add_edge(c, e, 5.0)
```

### Step 14: Call g.add_edge()

```python
g.add_edge(e, f, 1.0)
```

### Step 15: Call g.add_edge()

```python
g.add_edge(d, e, 1.0)
```

### Step 16: Assign expected = value

```python
expected = [[0], [0, 1], [0, 1, 2], [0, 3], [0, 3, 4], [0, 3, 4, 5]]
```

### Step 17: Assign unknown = f

```python
x1, x2 = f
```

### Step 18: Assign path = rustworkx.digraph_astar_shortest_path(...)

```python
path = rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(end, finish), lambda x: float(x), heuristic_func)
```

### Step 19: Call self.assertEqual()

```python
self.assertEqual(expected[index], path)
```

### Step 20: Call rustworkx.digraph_astar_shortest_path()

```python
rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(no_path, finish), lambda x: float(x), heuristic_func)
```


## Complete Example

```python
# Workflow
g = rustworkx.PyDAG()
a = g.add_node((0.0, 0.0))
b = g.add_node((2.0, 0.0))
c = g.add_node((1.0, 1.0))
d = g.add_node((0.0, 2.0))
e = g.add_node((3.0, 3.0))
f = g.add_node((4.0, 2.0))
no_path = g.add_node((5.0, 5.0))
g.add_edge(a, b, 2.0)
g.add_edge(a, d, 4.0)
g.add_edge(b, c, 1.0)
g.add_edge(b, f, 7.0)
g.add_edge(c, e, 5.0)
g.add_edge(e, f, 1.0)
g.add_edge(d, e, 1.0)

def heuristic_func(f):
    x1, x2 = f
    return abs(x2 - x1)

def finish_func(node, x):
    return x == g.get_node_data(node)
expected = [[0], [0, 1], [0, 1, 2], [0, 3], [0, 3, 4], [0, 3, 4, 5]]
for index, end in enumerate([a, b, c, d, e, f]):
    path = rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(end, finish), lambda x: float(x), heuristic_func)
    self.assertEqual(expected[index], path)
with self.assertRaises(rustworkx.NoPathFound):
    rustworkx.digraph_astar_shortest_path(g, a, lambda finish: finish_func(no_path, finish), lambda x: float(x), heuristic_func)
```

## Next Steps


---

*Source: test_astar.py:42 | Complexity: Advanced | Last updated: 2026-05-05*