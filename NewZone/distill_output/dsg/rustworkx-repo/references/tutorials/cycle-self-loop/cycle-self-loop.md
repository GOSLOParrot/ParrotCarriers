# How To: Cycle Self Loop

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test cycle self loop

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
b = g.node_indices()[-1]
```

### Step 4: Call g.add_edge()

```python
g.add_edge(b, a, None)
```

### Step 5: Call g.add_edge()

```python
g.add_edge(a, a, None)
```

### Step 6: Assign res = rustworkx.digraph_find_cycle(...)

```python
res = rustworkx.digraph_find_cycle(g)
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(res, [(a, a)])
```


## Complete Example

```python
# Workflow
g = rustworkx.generators.directed_path_graph(1000)
a = g.add_node(1000)
b = g.node_indices()[-1]
g.add_edge(b, a, None)
g.add_edge(a, a, None)
res = rustworkx.digraph_find_cycle(g)
self.assertEqual(res, [(a, a)])
```

## Next Steps


---

*Source: test_find_cycle.py:98 | Complexity: Intermediate | Last updated: 2026-05-05*