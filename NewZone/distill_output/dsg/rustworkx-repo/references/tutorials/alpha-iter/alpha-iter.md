# How To: Alpha Iter

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test alpha iter

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

### Step 1: Assign graph = rustworkx.generators.grid_graph(...)

```python
graph = rustworkx.generators.grid_graph(4, 6)
```

### Step 2: Call plt.subplot()

```python
plt.subplot(131)
```

### Step 3: Call mpl_draw()

```python
mpl_draw(graph, alpha=[0.1, 0.2])
```

### Step 4: Assign num_nodes = len(...)

```python
num_nodes = len(graph)
```

### Step 5: Assign alpha = value

```python
alpha = [x / num_nodes for x in range(num_nodes)]
```

### Step 6: Assign colors = range(...)

```python
colors = range(num_nodes)
```

### Step 7: Call plt.subplot()

```python
plt.subplot(132)
```

### Step 8: Call mpl_draw()

```python
mpl_draw(graph, node_color=colors, alpha=alpha)
```

### Step 9: Call alpha.append()

```python
alpha.append(1)
```

### Step 10: Call plt.subplot()

```python
plt.subplot(133)
```

### Step 11: Call mpl_draw()

```python
mpl_draw(graph, alpha=alpha)
```

### Step 12: Assign fig = plt.gcf(...)

```python
fig = plt.gcf()
```

### Step 13: Call _save_images()

```python
_save_images(fig, 'test_alpha_iter.png')
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.grid_graph(4, 6)
plt.subplot(131)
mpl_draw(graph, alpha=[0.1, 0.2])
num_nodes = len(graph)
alpha = [x / num_nodes for x in range(num_nodes)]
colors = range(num_nodes)
plt.subplot(132)
mpl_draw(graph, node_color=colors, alpha=alpha)
alpha.append(1)
plt.subplot(133)
mpl_draw(graph, alpha=alpha)
fig = plt.gcf()
_save_images(fig, 'test_alpha_iter.png')
```

## Next Steps


---

*Source: test_mpl.py:127 | Complexity: Advanced | Last updated: 2026-05-05*