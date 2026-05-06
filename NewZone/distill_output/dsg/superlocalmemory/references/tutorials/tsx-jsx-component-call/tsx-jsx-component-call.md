# How To: Tsx Jsx Component Call

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: TSX file with JSX component usage.

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
# Fixtures: config
```

## Step-by-Step Guide

### Step 1: 'TSX file with JSX component usage.'

```python
'TSX file with JSX component usage.'
```

**Verification:**
```python
assert 'MyComponent' in call_names
```

### Step 2: Assign source = b'\nimport React from \'react\';\nimport MyComponent from \'./MyComponent\';\n\nexport function App() {\n  return <MyComponent prop="x" />;\n}\n'

```python
source = b'\nimport React from \'react\';\nimport MyComponent from \'./MyComponent\';\n\nexport function App() {\n  return <MyComponent prop="x" />;\n}\n'
```

### Step 3: Assign parser = get_parser(...)

```python
parser = get_parser('tsx')
```

### Step 4: Assign tree = parser.parse(...)

```python
tree = parser.parse(source)
```

### Step 5: Assign ext = TypeScriptExtractor(...)

```python
ext = TypeScriptExtractor(tree.root_node, source, 'App.tsx', config)
```

### Step 6: Assign unknown = ext.extract_imports(...)

```python
_, import_map = ext.extract_imports()
```

### Step 7: Assign edges = ext.extract_calls(...)

```python
edges = ext.extract_calls(import_map)
```

### Step 8: Assign call_names = value

```python
call_names = [json.loads(e.extra_json).get('call_name', '') for e in edges]
```

**Verification:**
```python
assert 'MyComponent' in call_names
```


## Complete Example

```python
# Setup
# Fixtures: config

# Workflow
'TSX file with JSX component usage.'
from superlocalmemory.code_graph.extractors.typescript import TypeScriptExtractor
source = b'\nimport React from \'react\';\nimport MyComponent from \'./MyComponent\';\n\nexport function App() {\n  return <MyComponent prop="x" />;\n}\n'
parser = get_parser('tsx')
tree = parser.parse(source)
ext = TypeScriptExtractor(tree.root_node, source, 'App.tsx', config)
_, import_map = ext.extract_imports()
edges = ext.extract_calls(import_map)
call_names = [json.loads(e.extra_json).get('call_name', '') for e in edges]
assert 'MyComponent' in call_names
```

## Next Steps


---

*Source: test_extractor_typescript.py:148 | Complexity: Advanced | Last updated: 2026-05-05*