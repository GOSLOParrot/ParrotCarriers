# How To: Draw Edges Min Source Target Margins

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that there is a wider gap between the node and the start of an
incident edge when min_source_margin is specified.

This test checks that the use of min_{source/target}_margin kwargs
result in shorter (more padding) between the edges and source and
target nodes. As a crude visual example, let 's' and 't' represent
source and target nodes, respectively:
   Default:
   s-----------------------------t
   With margins:
   s   -----------------------   t

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

### Step 1: "Test that there is a wider gap between the node and the start of an\n        incident edge when min_source_margin is specified.\n\n        This test checks that the use of min_{source/target}_margin kwargs\n        result in shorter (more padding) between the edges and source and\n        target nodes. As a crude visual example, let 's' and 't' represent\n        source and target nodes, respectively:\n           Default:\n           s-----------------------------t\n           With margins:\n           s   -----------------------   t\n        "

```python
"Test that there is a wider gap between the node and the start of an\n        incident edge when min_source_margin is specified.\n\n        This test checks that the use of min_{source/target}_margin kwargs\n        result in shorter (more padding) between the edges and source and\n        target nodes. As a crude visual example, let 's' and 't' represent\n        source and target nodes, respectively:\n           Default:\n           s-----------------------------t\n           With margins:\n           s   -----------------------   t\n        "
```

### Step 2: Assign node_shapes = value

```python
node_shapes = ['o', 's']
```

### Step 3: Assign graph = rustworkx.PyGraph(...)

```python
graph = rustworkx.PyGraph()
```

### Step 4: Call graph.extend_from_edge_list()

```python
graph.extend_from_edge_list([(0, 1)])
```

### Step 5: Assign pos = value

```python
pos = {0: (0, 0), 1: (1, 0)}
```

### Step 6: Assign unknown = plt.subplots(...)

```python
fig, ax = plt.subplots()
```

### Step 7: Call mpl_draw()

```python
mpl_draw(graph, pos=pos, ax=ax, node_shape=node_shape, min_source_margin=100, min_target_margin=100)
```

### Step 8: Call _save_images()

```python
_save_images(fig, f'test_node_shape_{node_shape}.png')
```


## Complete Example

```python
# Workflow
"Test that there is a wider gap between the node and the start of an\n        incident edge when min_source_margin is specified.\n\n        This test checks that the use of min_{source/target}_margin kwargs\n        result in shorter (more padding) between the edges and source and\n        target nodes. As a crude visual example, let 's' and 't' represent\n        source and target nodes, respectively:\n           Default:\n           s-----------------------------t\n           With margins:\n           s   -----------------------   t\n        "
node_shapes = ['o', 's']
graph = rustworkx.PyGraph()
graph.extend_from_edge_list([(0, 1)])
pos = {0: (0, 0), 1: (1, 0)}
for node_shape in node_shapes:
    with self.subTest(shape=node_shape):
        fig, ax = plt.subplots()
        mpl_draw(graph, pos=pos, ax=ax, node_shape=node_shape, min_source_margin=100, min_target_margin=100)
        _save_images(fig, f'test_node_shape_{node_shape}.png')
```

## Next Steps


---

*Source: test_mpl.py:96 | Complexity: Advanced | Last updated: 2026-05-05*