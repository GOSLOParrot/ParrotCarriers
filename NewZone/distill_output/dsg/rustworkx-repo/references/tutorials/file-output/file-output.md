# How To: File Output

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test file output

## Prerequisites

**Required Modules:**
- `json`
- `tempfile`
- `uuid`
- `unittest`
- `rustworkx`
- `networkx`


## Step-by-Step Guide

### Step 1: Assign graph = rustworkx.generators.path_graph(...)

```python
graph = rustworkx.generators.path_graph(3)
```

### Step 2: Assign graph.attrs = 'path_graph'

```python
graph.attrs = 'path_graph'
```

### Step 3: Assign expected = value

```python
expected = {'attrs': {'label': 'path_graph'}, 'directed': False, 'links': [{'data': {'edgeLabel': '0->1'}, 'id': 0, 'source': 0, 'target': 1}, {'data': {'edgeLabel': '1->2'}, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
```

### Step 4: Assign unknown = value

```python
graph[node] = {'nodeLabel': f'node={node}'}
```

### Step 5: Call graph.update_edge_by_index()

```python
graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
```

### Step 6: Assign res = rustworkx.node_link_json(...)

```python
res = rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
```

### Step 7: Call self.assertIsNone()

```python
self.assertIsNone(res)
```

### Step 8: Assign json_dict = json.load(...)

```python
json_dict = json.load(fd)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(json_dict, expected)
```


## Complete Example

```python
# Workflow
graph = rustworkx.generators.path_graph(3)
graph.attrs = 'path_graph'
for node in graph.node_indices():
    graph[node] = {'nodeLabel': f'node={node}'}
for edge, (source, target, _weight) in graph.edge_index_map().items():
    graph.update_edge_by_index(edge, {'edgeLabel': f'{source}->{target}'})
expected = {'attrs': {'label': 'path_graph'}, 'directed': False, 'links': [{'data': {'edgeLabel': '0->1'}, 'id': 0, 'source': 0, 'target': 1}, {'data': {'edgeLabel': '1->2'}, 'id': 1, 'source': 1, 'target': 2}], 'multigraph': True, 'nodes': [{'data': {'nodeLabel': 'node=0'}, 'id': 0}, {'data': {'nodeLabel': 'node=1'}, 'id': 1}, {'data': {'nodeLabel': 'node=2'}, 'id': 2}]}
with tempfile.NamedTemporaryFile() as fd:
    res = rustworkx.node_link_json(graph, path=fd.name, graph_attrs=lambda x: {'label': x}, node_attrs=dict, edge_attrs=dict)
    self.assertIsNone(res)
    json_dict = json.load(fd)
    self.assertEqual(json_dict, expected)
```

## Next Steps


---

*Source: test_node_link_json.py:95 | Complexity: Advanced | Last updated: 2026-05-05*