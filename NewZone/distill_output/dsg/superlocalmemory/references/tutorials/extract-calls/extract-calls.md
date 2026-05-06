# How To: Extract Calls

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test extract calls

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `__future__`
- `json`
- `pathlib`
- `pytest`
- `superlocalmemory.code_graph.config`
- `superlocalmemory.code_graph.models`
- `tree_sitter`
- `tree_sitter_language_pack`
- `superlocalmemory.code_graph.extractors.typescript`
- `superlocalmemory.code_graph.extractors.typescript`
- `superlocalmemory.code_graph.extractors.typescript`

**Setup Required:**
```python
# Fixtures: ts_extractor
```

## Step-by-Step Guide

### Step 1: Assign unknown = ts_extractor.extract_imports(...)

```python
_, import_map = ts_extractor.extract_imports()
```

**Verification:**
```python
assert 'validateToken' in call_names
```

### Step 2: Assign edges = ts_extractor.extract_calls(...)

```python
edges = ts_extractor.extract_calls(import_map)
```

**Verification:**
```python
assert 'createController' in call_names
```

### Step 3: Assign call_names = value

```python
call_names = []
```

**Verification:**
```python
assert 'AuthController' in call_names
```

### Step 4: Assign extra = json.loads(...)

```python
extra = json.loads(e.extra_json)
```

### Step 5: Call call_names.append()

```python
call_names.append(extra.get('call_name', ''))
```


## Complete Example

```python
# Setup
# Fixtures: ts_extractor

# Workflow
_, import_map = ts_extractor.extract_imports()
edges = ts_extractor.extract_calls(import_map)
call_names = []
for e in edges:
    extra = json.loads(e.extra_json)
    call_names.append(extra.get('call_name', ''))
assert 'validateToken' in call_names
assert 'createController' in call_names
assert 'AuthController' in call_names
```

## Next Steps


---

*Source: test_extractor_typescript.py:115 | Complexity: Intermediate | Last updated: 2026-05-05*