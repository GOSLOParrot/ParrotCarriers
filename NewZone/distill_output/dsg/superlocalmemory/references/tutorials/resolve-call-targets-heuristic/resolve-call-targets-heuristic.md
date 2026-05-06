# How To: Resolve Call Targets Heuristic

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Single global match should use heuristic confidence.

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

### Step 1: 'Single global match should use heuristic confidence.'

```python
'Single global match should use heuristic confidence.'
```

**Verification:**
```python
assert len(resolved) == 1
```

### Step 2: Assign resolver = ImportResolver(...)

```python
resolver = ImportResolver(tmp_path, config)
```

**Verification:**
```python
assert resolved[0].confidence == config.heuristic_confidence
```

### Step 3: Assign nodes = value

```python
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='a.py::foo', file_path='a.py'), GraphNode(node_id='target', name='bar', kind=NodeKind.FUNCTION, qualified_name='c.py::bar', file_path='c.py')]
```

### Step 4: Assign edges = value

```python
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__bar', file_path='a.py', line=5)]
```

### Step 5: Assign resolved = resolver.resolve_call_targets(...)

```python
resolved = resolver.resolve_call_targets(nodes, edges, {})
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
'Single global match should use heuristic confidence.'
resolver = ImportResolver(tmp_path, config)
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='a.py::foo', file_path='a.py'), GraphNode(node_id='target', name='bar', kind=NodeKind.FUNCTION, qualified_name='c.py::bar', file_path='c.py')]
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__bar', file_path='a.py', line=5)]
resolved = resolver.resolve_call_targets(nodes, edges, {})
assert len(resolved) == 1
assert resolved[0].confidence == config.heuristic_confidence
```

## Next Steps


---

*Source: test_resolver.py:162 | Complexity: Intermediate | Last updated: 2026-05-05*