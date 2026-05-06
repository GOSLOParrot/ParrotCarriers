# How To: Topo Sort

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test topo sort

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign sorter = rustworkx.TopologicalSorter(...)

```python
sorter = rustworkx.TopologicalSorter(self.graph)
```

### Step 2: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 3: Call self.assertEqual()

```python
self.assertEqual(nodes, [0, 1])
```

### Step 4: Call sorter.done()

```python
sorter.done(nodes)
```

### Step 5: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(nodes, [2])
```

### Step 7: Call sorter.done()

```python
sorter.done(nodes)
```

### Step 8: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(nodes, [4, 3])
```

### Step 10: Call sorter.done()

```python
sorter.done(nodes)
```

### Step 11: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual(nodes, [5])
```

### Step 13: Call sorter.done()

```python
sorter.done(nodes)
```

### Step 14: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 15: Call self.assertEqual()

```python
self.assertEqual(nodes, [])
```


## Complete Example

```python
# Workflow
sorter = rustworkx.TopologicalSorter(self.graph)
nodes = sorter.get_ready()
self.assertEqual(nodes, [0, 1])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [2])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [4, 3])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [5])
sorter.done(nodes)
nodes = sorter.get_ready()
self.assertEqual(nodes, [])
```

## Next Steps


---

*Source: test_toposort.py:31 | Complexity: Advanced | Last updated: 2026-05-05*