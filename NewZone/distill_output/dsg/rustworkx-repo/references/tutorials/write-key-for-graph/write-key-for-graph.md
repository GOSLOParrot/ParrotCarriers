# How To: Write Key For Graph

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: test write key for graph

## Prerequisites

**Required Modules:**
- `unittest`
- `tempfile`
- `gzip`
- `numpy`
- `rustworkx`


## Step-by-Step Guide

### Step 1: Assign graph_xml = self.HEADER.format(...)

```python
graph_xml = self.HEADER.format('\n            <key id="d0" for="graph" attr.name="test" attr.type="boolean"/>\n            <graph id="G" edgedefault="directed">\n            <data key="d0">true</data>\n            <node id="n0"/>\n            </graph>\n            ')
```

### Step 2: Assign graph = value

```python
graph = graphml[0]
```

### Step 3: Assign nodes = value

```python
nodes = [{'id': 'n0'}]
```

### Step 4: Assign edges = value

```python
edges = []
```

### Step 5: Call self.assertGraphEqual()

```python
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': True})
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

### Step 9: Call rustworkx.write_graphml()

```python
rustworkx.write_graphml(graphml[0], fd.name)
```

### Step 10: Assign graphml = rustworkx.read_graphml(...)

```python
graphml = rustworkx.read_graphml(fd.name)
```


## Complete Example

```python
# Workflow
graph_xml = self.HEADER.format('\n            <key id="d0" for="graph" attr.name="test" attr.type="boolean"/>\n            <graph id="G" edgedefault="directed">\n            <data key="d0">true</data>\n            <node id="n0"/>\n            </graph>\n            ')
with tempfile.NamedTemporaryFile('wt') as fd:
    fd.write(graph_xml)
    fd.flush()
    graphml = rustworkx.read_graphml(fd.name)
with tempfile.NamedTemporaryFile('wt') as fd:
    rustworkx.write_graphml(graphml[0], fd.name)
    graphml = rustworkx.read_graphml(fd.name)
graph = graphml[0]
nodes = [{'id': 'n0'}]
edges = []
self.assertGraphEqual(graph, nodes, edges, directed=True, attrs={'id': 'G', 'test': True})
```

## Next Steps


---

*Source: test_graphml.py:292 | Complexity: Advanced | Last updated: 2026-05-05*