# How To: Astar Null Heuristic

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test astar null heuristic

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
a = g.add_node('A')
```

### Step 3: Assign b = g.add_node(...)

```python
b = g.add_node('B')
```

### Step 4: Assign c = g.add_node(...)

```python
c = g.add_node('C')
```

### Step 5: Assign d = g.add_node(...)

```python
d = g.add_node('D')
```

### Step 6: Assign e = g.add_node(...)

```python
e = g.add_node('E')
```

### Step 7: Assign f = g.add_node(...)

```python
f = g.add_node('F')
```

### Step 8: Call g.add_edge()

```python
g.add_edge(a, b, 7)
```

### Step 9: Call g.add_edge()

```python
g.add_edge(c, a, 9)
```

### Step 10: Call g.add_edge()

```python
g.add_edge(a, d, 14)
```

### Step 11: Call g.add_edge()

```python
g.add_edge(b, c, 10)
```

### Step 12: Call g.add_edge()

```python
g.add_edge(d, c, 2)
```

### Step 13: Call g.add_edge()

```python
g.add_edge(d, e, 9)
```

### Step 14: Call g.add_edge()

```python
g.add_edge(b, f, 15)
```

### Step 15: Call g.add_edge()

```python
g.add_edge(c, f, 11)
```

### Step 16: Call g.add_edge()

```python
g.add_edge(e, f, 6)
```

### Step 17: Assign path = rustworkx.digraph_astar_shortest_path(...)

```python
path = rustworkx.digraph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
```

### Step 18: Assign expected = value

```python
expected = [a, d, e]
```

### Step 19: Call self.assertEqual()

```python
self.assertEqual(expected, path)
```


## Complete Example

```python
# Workflow
g = rustworkx.PyDAG()
a = g.add_node('A')
b = g.add_node('B')
c = g.add_node('C')
d = g.add_node('D')
e = g.add_node('E')
f = g.add_node('F')
g.add_edge(a, b, 7)
g.add_edge(c, a, 9)
g.add_edge(a, d, 14)
g.add_edge(b, c, 10)
g.add_edge(d, c, 2)
g.add_edge(d, e, 9)
g.add_edge(b, f, 15)
g.add_edge(c, f, 11)
g.add_edge(e, f, 6)
path = rustworkx.digraph_astar_shortest_path(g, a, lambda goal: goal == 'E', lambda x: float(x), lambda y: 0)
expected = [a, d, e]
self.assertEqual(expected, path)
```

## Next Steps


---

*Source: test_astar.py:19 | Complexity: Advanced | Last updated: 2026-05-05*