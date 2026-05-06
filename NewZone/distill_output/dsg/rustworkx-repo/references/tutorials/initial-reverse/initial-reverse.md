# How To: Initial Reverse

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test initial reverse

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign dag = rustworkx.PyDiGraph(...)

```python
dag = rustworkx.PyDiGraph()
```

### Step 2: Call dag.add_nodes_from()

```python
dag.add_nodes_from(range(9))
```

### Step 3: Call dag.add_edges_from_no_data()

```python
dag.add_edges_from_no_data([(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (4, 7), (6, 8), (7, 8)])
```

### Step 4: Assign sorter = rustworkx.TopologicalSorter(...)

```python
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1, 2])
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(set(sorter.get_ready()), {1, 2})
```

### Step 6: Call sorter.done()

```python
sorter.done([1, 2])
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(set(sorter.get_ready()), {0})
```

### Step 8: Call sorter.done()

```python
sorter.done([0])
```

### Step 9: Call self.assertFalse()

```python
self.assertFalse(sorter.is_active())
```

### Step 10: Assign initial_sorter = rustworkx.TopologicalSorter(...)

```python
initial_sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[8])
```

### Step 11: Assign base_sorter = rustworkx.TopologicalSorter(...)

```python
base_sorter = rustworkx.TopologicalSorter(dag, reverse=True)
```

### Step 12: Assign bases = value

```python
bases = []
```

### Step 13: Assign initials = value

```python
initials = []
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(bases, initials)
```

### Step 15: Call self.assertFalse()

```python
self.assertFalse(initial_sorter.is_active())
```

### Step 16: Assign sorter = rustworkx.TopologicalSorter(...)

```python
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1])
```

### Step 17: Call self.assertEqual()

```python
self.assertEqual(set(sorter.get_ready()), {1})
```

### Step 18: Call sorter.done()

```python
sorter.done([1])
```

### Step 19: Call self.assertFalse()

```python
self.assertFalse(sorter.is_active())
```

### Step 20: Call bases.append()

```python
bases.append(base_ready)
```

### Step 21: Call initials.append()

```python
initials.append(initial_sorter.get_ready())
```

### Step 22: Call base_sorter.done()

```python
base_sorter.done(bases[-1])
```

### Step 23: Call initial_sorter.done()

```python
initial_sorter.done(initials[-1])
```


## Complete Example

```python
# Workflow
dag = rustworkx.PyDiGraph()
dag.add_nodes_from(range(9))
dag.add_edges_from_no_data([(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (4, 7), (6, 8), (7, 8)])
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1, 2])
self.assertEqual(set(sorter.get_ready()), {1, 2})
sorter.done([1, 2])
self.assertEqual(set(sorter.get_ready()), {0})
sorter.done([0])
self.assertFalse(sorter.is_active())
initial_sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[8])
base_sorter = rustworkx.TopologicalSorter(dag, reverse=True)
bases = []
initials = []
while (base_ready := base_sorter.get_ready()):
    bases.append(base_ready)
    initials.append(initial_sorter.get_ready())
    base_sorter.done(bases[-1])
    initial_sorter.done(initials[-1])
self.assertEqual(bases, initials)
self.assertFalse(initial_sorter.is_active())
sorter = rustworkx.TopologicalSorter(dag, reverse=True, initial=[1])
self.assertEqual(set(sorter.get_ready()), {1})
sorter.done([1])
self.assertFalse(sorter.is_active())
```

## Next Steps


---

*Source: test_toposort.py:165 | Complexity: Advanced | Last updated: 2026-05-05*