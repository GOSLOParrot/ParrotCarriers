# How To: Directed Star Graph Bidirectional Inward

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test directed star graph bidirectional inward

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.directed_star_graph(...)

```python
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=True)
```

### Step 2: Assign outw = value

```python
outw = []
```

### Step 3: Assign inw = value

```python
inw = []
```

### Step 4: Call self.assertEqual()

```python
self.assertEqual(graph.out_edges(0), outw[::-1])
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(graph.in_edges(0), inw[::-1])
```

### Step 6: Assign graph = rustworkx.generators.directed_star_graph(...)

```python
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=False)
```

### Step 7: Assign outw = value

```python
outw = []
```

### Step 8: Assign inw = value

```python
inw = []
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(graph.out_edges(0), outw[::-1])
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(graph.in_edges(0), inw[::-1])
```

### Step 11: Call outw.append()

```python
outw.append((0, i, None))
```

### Step 12: Call inw.append()

```python
inw.append((i, 0, None))
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual(graph.out_edges(i), [(i, 0, None)])
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(graph.in_edges(i), [(0, i, None)])
```

### Step 15: Call outw.append()

```python
outw.append((0, i, None))
```

### Step 16: Call inw.append()

```python
inw.append((i, 0, None))
```

### Step 17: Call self.assertEqual()

```python
self.assertEqual(graph.out_edges(i), [(i, 0, None)])
```

### Step 18: Call self.assertEqual()

```python
self.assertEqual(graph.in_edges(i), [(0, i, None)])
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=True)
outw = []
inw = []
for i in range(1, 20):
    outw.append((0, i, None))
    inw.append((i, 0, None))
    self.assertEqual(graph.out_edges(i), [(i, 0, None)])
    self.assertEqual(graph.in_edges(i), [(0, i, None)])
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
graph = rustworkx.generators.directed_star_graph(20, bidirectional=True, inward=False)
outw = []
inw = []
for i in range(1, 20):
    outw.append((0, i, None))
    inw.append((i, 0, None))
    self.assertEqual(graph.out_edges(i), [(i, 0, None)])
    self.assertEqual(graph.in_edges(i), [(0, i, None)])
self.assertEqual(graph.out_edges(0), outw[::-1])
self.assertEqual(graph.in_edges(0), inw[::-1])
```

## Next Steps


---

*Source: test_star.py:53 | Complexity: Advanced | Last updated: 2026-05-05*