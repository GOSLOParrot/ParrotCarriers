# How To: Flow Db

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: DB pre-populated with a call graph for flow detection.

Graph:
    main -> process_request -> validate_token -> query_db
                            -> log_request
    handle_event -> process_event

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `time`
- `pytest`
- `superlocalmemory.code_graph.database`
- `superlocalmemory.code_graph.flows`
- `superlocalmemory.code_graph.models`

**Setup Required:**
```python
# Fixtures: db
```

## Step-by-Step Guide

### Step 1: 'DB pre-populated with a call graph for flow detection.\n\n    Graph:\n        main -> process_request -> validate_token -> query_db\n                                -> log_request\n        handle_event -> process_event\n    '

```python
'DB pre-populated with a call graph for flow detection.\n\n    Graph:\n        main -> process_request -> validate_token -> query_db\n                                -> log_request\n        handle_event -> process_event\n    '
```

### Step 2: Assign now = time.time(...)

```python
now = time.time()
```

### Step 3: Assign nodes = value

```python
nodes = [GraphNode(node_id='main', kind=NodeKind.FUNCTION, name='main', qualified_name='app.py::main', file_path='app.py', line_start=1, line_end=20, language='python', created_at=now, updated_at=now), GraphNode(node_id='process_request', kind=NodeKind.FUNCTION, name='process_request', qualified_name='handlers.py::process_request', file_path='handlers.py', line_start=1, line_end=30, language='python', created_at=now, updated_at=now), GraphNode(node_id='validate_token', kind=NodeKind.FUNCTION, name='validate_token', qualified_name='auth.py::validate_token', file_path='auth.py', line_start=1, line_end=15, language='python', created_at=now, updated_at=now), GraphNode(node_id='query_db', kind=NodeKind.FUNCTION, name='query_db', qualified_name='db.py::query_db', file_path='db.py', line_start=1, line_end=20, language='python', created_at=now, updated_at=now), GraphNode(node_id='log_request', kind=NodeKind.FUNCTION, name='log_request', qualified_name='logging.py::log_request', file_path='logging.py', line_start=1, line_end=10, language='python', created_at=now, updated_at=now), GraphNode(node_id='handle_event', kind=NodeKind.FUNCTION, name='handle_event', qualified_name='events.py::handle_event', file_path='events.py', line_start=1, line_end=25, language='python', created_at=now, updated_at=now), GraphNode(node_id='process_event', kind=NodeKind.FUNCTION, name='process_event', qualified_name='events.py::process_event', file_path='events.py', line_start=30, line_end=50, language='python', created_at=now, updated_at=now)]
```

### Step 4: Assign edges = value

```python
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='main', target_node_id='process_request', file_path='app.py', line=5, created_at=now, updated_at=now), GraphEdge(edge_id='e2', kind=EdgeKind.CALLS, source_node_id='process_request', target_node_id='validate_token', file_path='handlers.py', line=10, created_at=now, updated_at=now), GraphEdge(edge_id='e3', kind=EdgeKind.CALLS, source_node_id='validate_token', target_node_id='query_db', file_path='auth.py', line=5, created_at=now, updated_at=now), GraphEdge(edge_id='e4', kind=EdgeKind.CALLS, source_node_id='process_request', target_node_id='log_request', file_path='handlers.py', line=15, created_at=now, updated_at=now), GraphEdge(edge_id='e5', kind=EdgeKind.CALLS, source_node_id='handle_event', target_node_id='process_event', file_path='events.py', line=10, created_at=now, updated_at=now)]
```

### Step 5: Call db.upsert_node()

```python
db.upsert_node(node)
```

### Step 6: Call db.upsert_edge()

```python
db.upsert_edge(edge)
```


## Complete Example

```python
# Setup
# Fixtures: db

# Workflow
'DB pre-populated with a call graph for flow detection.\n\n    Graph:\n        main -> process_request -> validate_token -> query_db\n                                -> log_request\n        handle_event -> process_event\n    '
now = time.time()
nodes = [GraphNode(node_id='main', kind=NodeKind.FUNCTION, name='main', qualified_name='app.py::main', file_path='app.py', line_start=1, line_end=20, language='python', created_at=now, updated_at=now), GraphNode(node_id='process_request', kind=NodeKind.FUNCTION, name='process_request', qualified_name='handlers.py::process_request', file_path='handlers.py', line_start=1, line_end=30, language='python', created_at=now, updated_at=now), GraphNode(node_id='validate_token', kind=NodeKind.FUNCTION, name='validate_token', qualified_name='auth.py::validate_token', file_path='auth.py', line_start=1, line_end=15, language='python', created_at=now, updated_at=now), GraphNode(node_id='query_db', kind=NodeKind.FUNCTION, name='query_db', qualified_name='db.py::query_db', file_path='db.py', line_start=1, line_end=20, language='python', created_at=now, updated_at=now), GraphNode(node_id='log_request', kind=NodeKind.FUNCTION, name='log_request', qualified_name='logging.py::log_request', file_path='logging.py', line_start=1, line_end=10, language='python', created_at=now, updated_at=now), GraphNode(node_id='handle_event', kind=NodeKind.FUNCTION, name='handle_event', qualified_name='events.py::handle_event', file_path='events.py', line_start=1, line_end=25, language='python', created_at=now, updated_at=now), GraphNode(node_id='process_event', kind=NodeKind.FUNCTION, name='process_event', qualified_name='events.py::process_event', file_path='events.py', line_start=30, line_end=50, language='python', created_at=now, updated_at=now)]
for node in nodes:
    db.upsert_node(node)
edges = [GraphEdge(edge_id='e1', kind=EdgeKind.CALLS, source_node_id='main', target_node_id='process_request', file_path='app.py', line=5, created_at=now, updated_at=now), GraphEdge(edge_id='e2', kind=EdgeKind.CALLS, source_node_id='process_request', target_node_id='validate_token', file_path='handlers.py', line=10, created_at=now, updated_at=now), GraphEdge(edge_id='e3', kind=EdgeKind.CALLS, source_node_id='validate_token', target_node_id='query_db', file_path='auth.py', line=5, created_at=now, updated_at=now), GraphEdge(edge_id='e4', kind=EdgeKind.CALLS, source_node_id='process_request', target_node_id='log_request', file_path='handlers.py', line=15, created_at=now, updated_at=now), GraphEdge(edge_id='e5', kind=EdgeKind.CALLS, source_node_id='handle_event', target_node_id='process_event', file_path='events.py', line=10, created_at=now, updated_at=now)]
for edge in edges:
    db.upsert_edge(edge)
return db
```

## Next Steps


---

*Source: test_flows.py:32 | Complexity: Intermediate | Last updated: 2026-05-05*