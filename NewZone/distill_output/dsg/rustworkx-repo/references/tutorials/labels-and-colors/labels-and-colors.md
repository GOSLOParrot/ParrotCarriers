# How To: Labels And Colors

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test labels and colors

## Prerequisites

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `rustworkx`
- `rustworkx.visualization`
- `matplotlib`
- `matplotlib.pyplot`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 2: Call graph.add_nodes_from()

```python
graph.add_nodes_from(list(range(8)))
```

### Step 3: Assign edge_list = value

```python
edge_list = [(0, 1, 5), (1, 2, 2), (2, 3, 7), (3, 0, 6), (5, 6, 1), (4, 5, 7), (6, 7, 3), (7, 4, 7)]
```

### Step 4: Assign labels = value

```python
labels = {}
```

### Step 5: Assign unknown = '$a$'

```python
labels[0] = '$a$'
```

### Step 6: Assign unknown = '$b$'

```python
labels[1] = '$b$'
```

### Step 7: Assign unknown = '$c$'

```python
labels[2] = '$c$'
```

### Step 8: Assign unknown = '$d$'

```python
labels[3] = '$d$'
```

### Step 9: Assign unknown = '$\\alpha$'

```python
labels[4] = '$\\alpha$'
```

### Step 10: Assign unknown = '$\\beta$'

```python
labels[5] = '$\\beta$'
```

### Step 11: Assign unknown = '$\\gamma$'

```python
labels[6] = '$\\gamma$'
```

### Step 12: Assign unknown = '$\\delta$'

```python
labels[7] = '$\\delta$'
```

### Step 13: Call graph.add_edges_from()

```python
graph.add_edges_from(edge_list)
```

### Step 14: Assign pos = rustworkx.random_layout(...)

```python
pos = rustworkx.random_layout(graph)
```

### Step 15: Call mpl_draw()

```python
mpl_draw(graph, pos=pos, node_list=[0, 1, 2, 3], node_color='r', edge_list=[(0, 1), (1, 2), (2, 3), (3, 0)], node_size=500, alpha=0.75, width=1.0, labels=lambda x: labels[x], font_size=16)
```

### Step 16: Call mpl_draw()

```python
mpl_draw(graph, pos=pos, node_list=[4, 5, 6, 7], node_color='b', node_size=500, alpha=0.5, edge_list=[(4, 5), (5, 6), (6, 7), (7, 4)], width=8, edge_color='r', rotate=False, edge_labels=lambda edge: labels[edge])
```

### Step 17: Assign fig = plt.gcf(...)

```python
fig = plt.gcf()
```

### Step 18: Call _save_images()

```python
_save_images(fig, 'test_labels_and_colors.png')
```


## Complete Example

```python
# Workflow
graph = rustworkx.PyGraph()
graph.add_nodes_from(list(range(8)))
edge_list = [(0, 1, 5), (1, 2, 2), (2, 3, 7), (3, 0, 6), (5, 6, 1), (4, 5, 7), (6, 7, 3), (7, 4, 7)]
labels = {}
labels[0] = '$a$'
labels[1] = '$b$'
labels[2] = '$c$'
labels[3] = '$d$'
labels[4] = '$\\alpha$'
labels[5] = '$\\beta$'
labels[6] = '$\\gamma$'
labels[7] = '$\\delta$'
graph.add_edges_from(edge_list)
pos = rustworkx.random_layout(graph)
mpl_draw(graph, pos=pos, node_list=[0, 1, 2, 3], node_color='r', edge_list=[(0, 1), (1, 2), (2, 3), (3, 0)], node_size=500, alpha=0.75, width=1.0, labels=lambda x: labels[x], font_size=16)
mpl_draw(graph, pos=pos, node_list=[4, 5, 6, 7], node_color='b', node_size=500, alpha=0.5, edge_list=[(4, 5), (5, 6), (6, 7), (7, 4)], width=8, edge_color='r', rotate=False, edge_labels=lambda edge: labels[edge])
fig = plt.gcf()
_save_images(fig, 'test_labels_and_colors.png')
```

## Next Steps


---

*Source: test_mpl.py:145 | Complexity: Advanced | Last updated: 2026-05-05*