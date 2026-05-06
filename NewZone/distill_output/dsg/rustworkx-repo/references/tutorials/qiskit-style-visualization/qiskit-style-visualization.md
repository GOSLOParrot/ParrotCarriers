# How To: Qiskit Style Visualization

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: This test is to test visualizations like qiskit performs which regressed in 0.15.0.

## Prerequisites

**Required Modules:**
- `os`
- `subprocess`
- `tempfile`
- `unittest`
- `rustworkx`
- `rustworkx.visualization`
- `PIL`


## Step-by-Step Guide

### Step 1: 'This test is to test visualizations like qiskit performs which regressed in 0.15.0.'

```python
'This test is to test visualizations like qiskit performs which regressed in 0.15.0.'
```

### Step 2: Assign graph = rustworkx.generators.cycle_graph(...)

```python
graph = rustworkx.generators.cycle_graph(4)
```

### Step 3: Assign colors = value

```python
colors = ['#422952', '#492d58', '#4f305c', '#5e3767']
```

### Step 4: Assign edge_colors = value

```python
edge_colors = ['#4d2f5b', '#693d6f', '#995a88', '#382449']
```

### Step 5: Assign pos = value

```python
pos = [(0, 0), (0, 1), (1, 0), (1, 1)]
```

### Step 6: Call graphviz_draw()

```python
graphviz_draw(graph, node_attr_fn=color_node, edge_attr_fn=color_edge, filename='test_qiskit_style_visualization.png', image_type='png', method='neato')
```

### Step 7: Call self.assertTrue()

```python
self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))
```

### Step 8: Assign unknown = node

```python
graph[node] = node
```

### Step 9: Call graph.update_edge_by_index()

```python
graph.update_edge_by_index(edge, edge)
```

### Step 10: Assign out_dict = value

```python
out_dict = {'label': str(node), 'color': f'"{colors[node]}"', 'pos': f'"{pos[node][0]}, {pos[node][1]}"', 'fontname': '"DejaVu Sans"', 'pin': 'True', 'shape': 'circle', 'style': 'filled', 'fillcolor': f'"{colors[node]}"', 'fontcolor': 'white', 'fontsize': '10', 'height': '0.322', 'fixedsize': 'True'}
```

### Step 11: Assign out_dict = value

```python
out_dict = {'color': f'"{edge_colors[edge]}"', 'fillcolor': f'"{edge_colors[edge]}"', 'penwidth': str(5)}
```

### Step 12: Call self.addCleanup()

```python
self.addCleanup(os.remove, 'test_qiskit_style_visualization.png')
```


## Complete Example

```python
# Workflow
'This test is to test visualizations like qiskit performs which regressed in 0.15.0.'
graph = rustworkx.generators.cycle_graph(4)
colors = ['#422952', '#492d58', '#4f305c', '#5e3767']
edge_colors = ['#4d2f5b', '#693d6f', '#995a88', '#382449']
pos = [(0, 0), (0, 1), (1, 0), (1, 1)]
for node in graph.node_indices():
    graph[node] = node
for edge in graph.edge_indices():
    graph.update_edge_by_index(edge, edge)

def color_node(node):
    out_dict = {'label': str(node), 'color': f'"{colors[node]}"', 'pos': f'"{pos[node][0]}, {pos[node][1]}"', 'fontname': '"DejaVu Sans"', 'pin': 'True', 'shape': 'circle', 'style': 'filled', 'fillcolor': f'"{colors[node]}"', 'fontcolor': 'white', 'fontsize': '10', 'height': '0.322', 'fixedsize': 'True'}
    return out_dict

def color_edge(edge):
    out_dict = {'color': f'"{edge_colors[edge]}"', 'fillcolor': f'"{edge_colors[edge]}"', 'penwidth': str(5)}
    return out_dict
graphviz_draw(graph, node_attr_fn=color_node, edge_attr_fn=color_edge, filename='test_qiskit_style_visualization.png', image_type='png', method='neato')
self.assertTrue(os.path.isfile('test_qiskit_style_visualization.png'))
if not SAVE_IMAGES:
    self.addCleanup(os.remove, 'test_qiskit_style_visualization.png')
```

## Next Steps


---

*Source: test_graphviz.py:153 | Complexity: Advanced | Last updated: 2026-05-05*