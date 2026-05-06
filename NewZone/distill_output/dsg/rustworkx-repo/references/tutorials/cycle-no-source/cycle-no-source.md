# How To: Cycle No Source

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test cycle no source

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`
- `rustworkx.generators`


## Step-by-Step Guide

### Step 1: Assign g = rustworkx.generators.directed_path_graph(...)

```python
g = rustworkx.generators.directed_path_graph(1000)
```

### Step 2: Assign a = g.add_node(...)

```python
a = g.add_node(1000)
```

### Step 3: Assign b = value

```python
b = g.node_indices()[-2]
```

### Step 4: Call g.add_edge()

```python
g.add_edge(b, a, None)
```

### Step 5: Call g.add_edge()

```python
g.add_edge(a, b, None)
```

### Step 6: Assign res = rustworkx.digraph_find_cycle(...)

```python
res = rustworkx.digraph_find_cycle(g)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(len(res), 2)
```

### Step 8: Call self.assertTrue()

```python
self.assertTrue(res[0] == res[1][::-1])
```


## Complete Example

```python
# Workflow
g = rustworkx.generators.directed_path_graph(1000)
a = g.add_node(1000)
b = g.node_indices()[-2]
g.add_edge(b, a, None)
g.add_edge(a, b, None)
res = rustworkx.digraph_find_cycle(g)
self.assertEqual(len(res), 2)
self.assertTrue(res[0] == res[1][::-1])
```

## Next Steps


---

*Source: test_find_cycle.py:88 | Complexity: Advanced | Last updated: 2026-05-05*