# How To: Slices Negatives

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test slices negatives

## Prerequisites

**Required Modules:**
- `copy`
- `pickle`
- `unittest`
- `rustworkx`
- `numpy`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Call graph.add_nodes_from()

```python
graph.add_nodes_from(range(5))
```

### Step 3: Assign indices = graph.node_indices(...)

```python
indices = graph.node_indices()
```

### Step 4: Assign slice_return = value

```python
slice_return = indices[-1:-3:-1]
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual([4, 3], slice_return)
```

### Step 6: Assign slice_return = value

```python
slice_return = indices[3:1:-2]
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual([3], slice_return)
```

### Step 8: Assign slice_return = value

```python
slice_return = indices[-3:-1]
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual([2, 3], slice_return)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual([], indices[-1:-2])
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
graph.add_nodes_from(range(5))
indices = graph.node_indices()
slice_return = indices[-1:-3:-1]
self.assertEqual([4, 3], slice_return)
slice_return = indices[3:1:-2]
self.assertEqual([3], slice_return)
slice_return = indices[-3:-1]
self.assertEqual([2, 3], slice_return)
self.assertEqual([], indices[-1:-2])
```

## Next Steps


---

*Source: test_custom_return_types.py:175 | Complexity: Advanced | Last updated: 2026-05-05*