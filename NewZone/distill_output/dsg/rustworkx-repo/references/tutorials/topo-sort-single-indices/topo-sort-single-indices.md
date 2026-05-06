# How To: Topo Sort Single Indices

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test topo sort single indices

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
self.assertEqual(set(nodes), {0, 1})
```

### Step 4: Call sorter.done()

```python
sorter.done(0)
```

### Step 5: Call sorter.done()

```python
sorter.done(1)
```

### Step 6: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(set(nodes), {2})
```

### Step 8: Call sorter.done()

```python
sorter.done(2)
```

### Step 9: Assign nodes = sorter.get_ready(...)

```python
nodes = sorter.get_ready()
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(set(nodes), {3, 4})
```

### Step 11: Call sorter.done()

```python
sorter.done(3)
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual(set(sorter.get_ready()), {5})
```

### Step 13: Call sorter.done()

```python
sorter.done(5)
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(set(sorter.get_ready()), set())
```

### Step 15: Call self.assertTrue()

```python
self.assertTrue(sorter.is_active())
```

### Step 16: Call sorter.done()

```python
sorter.done(4)
```

### Step 17: Call self.assertEqual()

```python
self.assertEqual(set(sorter.get_ready()), set())
```

### Step 18: Call self.assertFalse()

```python
self.assertFalse(sorter.is_active())
```


## Complete Example

```python
# Workflow
sorter = rustworkx.TopologicalSorter(self.graph)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {0, 1})
sorter.done(0)
sorter.done(1)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {2})
sorter.done(2)
nodes = sorter.get_ready()
self.assertEqual(set(nodes), {3, 4})
sorter.done(3)
self.assertEqual(set(sorter.get_ready()), {5})
sorter.done(5)
self.assertEqual(set(sorter.get_ready()), set())
self.assertTrue(sorter.is_active())
sorter.done(4)
self.assertEqual(set(sorter.get_ready()), set())
self.assertFalse(sorter.is_active())
```

## Next Steps


---

*Source: test_toposort.py:48 | Complexity: Advanced | Last updated: 2026-05-05*