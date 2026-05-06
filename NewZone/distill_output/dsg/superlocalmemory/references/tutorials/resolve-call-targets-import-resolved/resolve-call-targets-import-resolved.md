# How To: Resolve Call Targets Import Resolved

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Import-resolved call should have confidence=1.0.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `pathlib`
- `pytest`
- `superlocalmemory.code_graph.config`
- `superlocalmemory.code_graph.models`
- `superlocalmemory.code_graph.resolver`

**Setup Required:**
```python
# Fixtures: tmp_path, config
```

## Step-by-Step Guide

### Step 1: 'Import-resolved call should have confidence=1.0.'

```python
'Import-resolved call should have confidence=1.0.'
```

**Verification:**
```python
assert len(resolved) == 1
```

### Step 2: Call unknown.write_text()

```python
(tmp_path / 'b.py').write_text('# b')
```

**Verification:**
```python
assert resolved[0].target_node_id == 'target'
```

### Step 3: Assign resolver = ImportResolver(...)

```python
resolver = ImportResolver(tmp_path, config)
```

**Verification:**
```python
assert resolved[0].confidence == 1.0
```

### Step 4: Assign nodes = value

```python
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='a.py::foo', file_path='a.py'), GraphNode(node_id='target', name='bar', kind=NodeKind.FUNCTION, qualified_name='b.py::bar', file_path='b.py')]
```

### Step 5: Assign edges = value

```python
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__bar', file_path='a.py', line=5)]
```

### Step 6: Assign import_maps = value

```python
import_maps = {'a.py': {'bar': ('b', 'bar')}}
```

### Step 7: Assign resolved = resolver.resolve_call_targets(...)

```python
resolved = resolver.resolve_call_targets(nodes, edges, import_maps)
```

**Verification:**
```python
assert len(resolved) == 1
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, config

# Workflow
'Import-resolved call should have confidence=1.0.'
(tmp_path / 'b.py').write_text('# b')
resolver = ImportResolver(tmp_path, config)
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='a.py::foo', file_path='a.py'), GraphNode(node_id='target', name='bar', kind=NodeKind.FUNCTION, qualified_name='b.py::bar', file_path='b.py')]
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__bar', file_path='a.py', line=5)]
import_maps = {'a.py': {'bar': ('b', 'bar')}}
resolved = resolver.resolve_call_targets(nodes, edges, import_maps)
assert len(resolved) == 1
assert resolved[0].target_node_id == 'target'
assert resolved[0].confidence == 1.0
```

## Next Steps


---

*Source: test_resolver.py:137 | Complexity: Intermediate | Last updated: 2026-05-05*