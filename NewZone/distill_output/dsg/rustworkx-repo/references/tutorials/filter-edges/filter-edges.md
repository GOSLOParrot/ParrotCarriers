# How To: Filter Edges

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test filter edges

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

### Step 7: Call graph.add_edge()

```python
graph.add_edge(0, 2, 'friends')
```

### Step 8: Call graph.add_edge()

```python
graph.add_edge(0, 1, 'friends')
```

### Step 9: Call graph.add_edge()

```python
graph.add_edge(0, 3, 'enemies')
```

### Step 10: Assign friends_indices = graph.filter_edges(...)

```python
friends_indices = graph.filter_edges(my_filter_function1)
```

### Step 11: Assign enemies_indices = graph.filter_edges(...)

```python
enemies_indices = graph.filter_edges(my_filter_function2)
```

### Step 12: Assign frenemies_indices = graph.filter_edges(...)

```python
frenemies_indices = graph.filter_edges(my_filter_function3)
```

### Step 13: Call self.assertEqual()

```python
self.assertEqual(list(friends_indices), [0, 1])
```

### Step 14: Call self.assertEqual()

```python
self.assertEqual(list(enemies_indices), [2])
```

### Step 15: Call self.assertEqual()

```python
self.assertEqual(list(frenemies_indices), [])
```


## Complete Example

```python
# Workflow
def my_filter_function1(edge):
    return edge == 'friends'

def my_filter_function2(edge):
    return edge == 'enemies'

def my_filter_function3(node):
    return node == 'frenemies'
graph = rx.PyGraph()
graph.add_node('cat')
graph.add_node('cat')
graph.add_node('dog')
graph.add_node('lizard')
graph.add_node('cat')
graph.add_edge(0, 2, 'friends')
graph.add_edge(0, 1, 'friends')
graph.add_edge(0, 3, 'enemies')
friends_indices = graph.filter_edges(my_filter_function1)
enemies_indices = graph.filter_edges(my_filter_function2)
frenemies_indices = graph.filter_edges(my_filter_function3)
self.assertEqual(list(friends_indices), [0, 1])
self.assertEqual(list(enemies_indices), [2])
self.assertEqual(list(frenemies_indices), [])
```

## Next Steps


---

*Source: test_filter.py:42 | Complexity: Advanced | Last updated: 2026-05-05*