# How To: Filter Nodes

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test filter nodes

## Prerequisites

**Required Modules:**
- `unittest`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph = rx.PyGraph(...)

```python
graph = rx.PyGraph()
```

### Step 2: Call graph.add_node()

```python
graph.add_node('cat')
```

### Step 3: Call graph.add_node()

```python
graph.add_node('cat')
```

### Step 4: Call graph.add_node()

```python
graph.add_node('dog')
```

### Step 5: Call graph.add_node()

```python
graph.add_node('lizard')
```

### Step 6: Call graph.add_node()

```python
graph.add_node('cat')
```

### Step 7: Assign cat_indices = graph.filter_nodes(...)

```python
cat_indices = graph.filter_nodes(my_filter_function1)
```

### Step 8: Assign lizard_indices = graph.filter_nodes(...)

```python
lizard_indices = graph.filter_nodes(my_filter_function2)
```

### Step 9: Assign human_indices = graph.filter_nodes(...)

```python
human_indices = graph.filter_nodes(my_filter_function3)
```

### Step 10: Call self.assertEqual()

```python
self.assertEqual(list(cat_indices), [0, 1, 4])
```

### Step 11: Call self.assertEqual()

```python
self.assertEqual(list(lizard_indices), [3])
```

### Step 12: Call self.assertEqual()

```python
self.assertEqual(list(human_indices), [])
```


## Complete Example

```python
# Workflow
def my_filter_function1(node):
    return node == 'cat'

def my_filter_function2(node):
    return node == 'lizard'

def my_filter_function3(node):
    return node == 'human'
graph = rx.PyGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
cat_indices = graph.filter_nodes(my_filter_function1)
lizard_indices = graph.filter_nodes(my_filter_function2)
human_indices = graph.filter_nodes(my_filter_function3)
self.assertEqual(list(cat_indices), [0, 1, 4])
self.assertEqual(list(lizard_indices), [3])
self.assertEqual(list(human_indices), [])
```

## Next Steps


---

*Source: test_filter.py:19 | Complexity: Advanced | Last updated: 2026-05-05*