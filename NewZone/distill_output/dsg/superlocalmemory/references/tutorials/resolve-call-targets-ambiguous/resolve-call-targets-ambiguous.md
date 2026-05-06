# How To: Resolve Call Targets Ambiguous

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Multiple matches should pick closest with reduced confidence.

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

### Step 1: 'Multiple matches should pick closest with reduced confidence.'

```python
'Multiple matches should pick closest with reduced confidence.'
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
assert resolved[0].target_node_id == 't1'
```

### Step 3: Assign nodes = value

```python
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='src/a.py::foo', file_path='src/a.py'), GraphNode(node_id='t1', name='bar', kind=NodeKind.FUNCTION, qualified_name='src/b.py::bar', file_path='src/b.py'), GraphNode(node_id='t2', name='bar', kind=NodeKind.FUNCTION, qualified_name='lib/c.py::bar', file_path='lib/c.py'), GraphNode(node_id='t3', name='bar', kind=NodeKind.FUNCTION, qualified_name='vendor/d.py::bar', file_path='vendor/d.py')]
```

**Verification:**
```python
assert resolved[0].confidence == pytest.approx(config.heuristic_confidence * 0.8)
```

### Step 4: Assign edges = value

```python
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__bar', file_path='src/a.py', line=5)]
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
'Multiple matches should pick closest with reduced confidence.'
resolver = ImportResolver(tmp_path, config)
nodes = [GraphNode(node_id='caller', name='foo', kind=NodeKind.FUNCTION, qualified_name='src/a.py::foo', file_path='src/a.py'), GraphNode(node_id='t1', name='bar', kind=NodeKind.FUNCTION, qualified_name='src/b.py::bar', file_path='src/b.py'), GraphNode(node_id='t2', name='bar', kind=NodeKind.FUNCTION, qualified_name='lib/c.py::bar', file_path='lib/c.py'), GraphNode(node_id='t3', name='bar', kind=NodeKind.FUNCTION, qualified_name='vendor/d.py::bar', file_path='vendor/d.py')]
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='caller', target_node_id='__call__bar', file_path='src/a.py', line=5)]
resolved = resolver.resolve_call_targets(nodes, edges, {})
assert len(resolved) == 1
assert resolved[0].target_node_id == 't1'
assert resolved[0].confidence == pytest.approx(config.heuristic_confidence * 0.8)
```

## Next Steps


---

*Source: test_resolver.py:182 | Complexity: Intermediate | Last updated: 2026-05-05*