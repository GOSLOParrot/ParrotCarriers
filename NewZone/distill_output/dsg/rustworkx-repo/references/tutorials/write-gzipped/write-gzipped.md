# How To: Write Gzipped

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test write gzipped

## Prerequisites

**Required Modules:**
- `unittest`
- `tempfile`
- `gzip`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_xml = self.graphml_xml_example(...)

```python
graph_xml = self.graphml_xml_example()
```

### Step 2: Assign graph = value

```python
graph = graphml[0]
```

### Step 3: Assign graph_reread = value

```python
graph_reread = graphml[0]
```

### Step 4: Assign edges = value

```python
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
```

### Step 5: Call self.assertGraphEqual()

```python
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

### Step 6: Call fd.write()

```python
fd.write(graph_xml)
```

### Step 7: Call fd.flush()

```python
fd.flush()
```

### Step 8: Assign graphml = rustworkx.read_graphml(...)

```python
graphml = rustworkx.read_graphml(fd.name)
```

### Step 9: Assign newname = value

```python
newname = f'{fd.name}.gz'
```

### Step 10: Call rustworkx.write_graphml()

```python
rustworkx.write_graphml(graph, newname)
```

### Step 11: Assign graphml = rustworkx.read_graphml(...)

```python
graphml = rustworkx.read_graphml(newname)
```


## Complete Example

```python
# Workflow
graph_xml = self.graphml_xml_example()
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
with tempfile.NamedTemporaryFile('wt') as fd:
    newname = f'{fd.name}.gz'
    rustworkx.write_graphml(graph, newname)
    graphml = rustworkx.read_graphml(newname)
graph_reread = graphml[0]
edges = [(graph[s]['id'], graph[t]['id'], weight) for s, t, weight in graph.weighted_edge_list()]
self.assertGraphEqual(graph_reread, graph.nodes(), edges, attrs={'id': 'G'}, directed=False)
```

## Next Steps


---

*Source: test_graphml.py:198 | Complexity: Advanced | Last updated: 2026-05-05*