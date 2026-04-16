# How To: Edge Type Signatures Map Preserves Multiple Signatures

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that edge types used across multiple node type pairs preserve all signatures.

This tests the fix for the bug where dict comprehension would overwrite
previous signatures when the same edge type appeared in multiple node pairs.

## Prerequisites

**Required Modules:**
- `datetime`
- `types`
- `unittest.mock`
- `pytest`
- `pydantic`
- `graphiti_core.edges`
- `graphiti_core.nodes`
- `graphiti_core.search.search_config`
- `graphiti_core.utils.maintenance.edge_operations`
- `graphiti_core.utils.maintenance`
- `graphiti_core.utils.maintenance`


## Step-by-Step Guide

### Step 1: 'Test that edge types used across multiple node type pairs preserve all signatures.\n\n    This tests the fix for the bug where dict comprehension would overwrite\n    previous signatures when the same edge type appeared in multiple node pairs.\n    '

```python
'Test that edge types used across multiple node type pairs preserve all signatures.\n\n    This tests the fix for the bug where dict comprehension would overwrite\n    previous signatures when the same edge type appeared in multiple node pairs.\n    '
```

**Verification:**
```python
assert 'InterpersonalRelationship' in edge_type_signatures_map
```

### Step 2: Assign interpersonal_signatures = value

```python
interpersonal_signatures = edge_type_signatures_map['InterpersonalRelationship']
```

**Verification:**
```python
assert len(interpersonal_signatures) == 2
```

### Step 3: Assign located_signatures = value

```python
located_signatures = edge_type_signatures_map['LocatedIn']
```

**Verification:**
```python
assert ('Person', 'Person') in interpersonal_signatures
```

### Step 4: Assign edge_types_context = value

```python
edge_types_context = [{'fact_type_name': type_name, 'fact_type_signatures': edge_type_signatures_map.get(type_name, [('Entity', 'Entity')]), 'fact_type_description': type_model.__doc__} for type_name, type_model in edge_types.items()]
```

**Verification:**
```python
assert ('Person', 'Entity') in interpersonal_signatures
```

### Step 5: Call unknown.append()

```python
edge_type_signatures_map[edge_type].append(signature)
```

**Verification:**
```python
assert 'LocatedIn' in edge_type_signatures_map
```

### Step 6: Assign unknown = value

```python
edge_type_signatures_map[edge_type] = []
```

**Verification:**
```python
assert len(located_signatures) == 2
```


## Complete Example

```python
# Workflow
'Test that edge types used across multiple node type pairs preserve all signatures.\n\n    This tests the fix for the bug where dict comprehension would overwrite\n    previous signatures when the same edge type appeared in multiple node pairs.\n    '
edge_type_map: dict[tuple[str, str], list[str]] = {('Person', 'Person'): ['InterpersonalRelationship'], ('Person', 'Entity'): ['InterpersonalRelationship'], ('Person', 'City'): ['LocatedIn'], ('Entity', 'City'): ['LocatedIn']}
edge_types: dict[str, type[BaseModel]] = {'InterpersonalRelationship': InterpersonalRelationship, 'LocatedIn': LocatedIn}
edge_type_signatures_map: dict[str, list[tuple[str, str]]] = {}
for signature, edge_type_names in edge_type_map.items():
    for edge_type in edge_type_names:
        if edge_type not in edge_type_signatures_map:
            edge_type_signatures_map[edge_type] = []
        edge_type_signatures_map[edge_type].append(signature)
assert 'InterpersonalRelationship' in edge_type_signatures_map
interpersonal_signatures = edge_type_signatures_map['InterpersonalRelationship']
assert len(interpersonal_signatures) == 2
assert ('Person', 'Person') in interpersonal_signatures
assert ('Person', 'Entity') in interpersonal_signatures
assert 'LocatedIn' in edge_type_signatures_map
located_signatures = edge_type_signatures_map['LocatedIn']
assert len(located_signatures) == 2
assert ('Person', 'City') in located_signatures
assert ('Entity', 'City') in located_signatures
edge_types_context = [{'fact_type_name': type_name, 'fact_type_signatures': edge_type_signatures_map.get(type_name, [('Entity', 'Entity')]), 'fact_type_description': type_model.__doc__} for type_name, type_model in edge_types.items()]
for ctx in edge_types_context:
    assert 'fact_type_signatures' in ctx
    assert isinstance(ctx['fact_type_signatures'], list)
    assert len(ctx['fact_type_signatures']) == 2
```

## Next Steps


---

*Source: test_edge_operations.py:460 | Complexity: Intermediate | Last updated: 2026-04-12*