# How To: Empty File

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: test empty file

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

### Step 1: Assign parser = get_parser(...)

```python
parser = get_parser('typescript')
```

**Verification:**
```python
assert nodes == []
```

### Step 2: Assign tree = parser.parse(...)

```python
tree = parser.parse(b'')
```

**Verification:**
```python
assert edges == []
```

### Step 3: Assign ext = TypeScriptExtractor(...)

```python
ext = TypeScriptExtractor(tree.root_node, b'', 'empty.ts', config)
```

### Step 4: Assign unknown = ext.extract(...)

```python
nodes, edges = ext.extract()
```

**Verification:**
```python
assert nodes == []
```


## Complete Example

```python
# Setup
# Fixtures: config

# Workflow
from superlocalmemory.code_graph.extractors.typescript import TypeScriptExtractor
parser = get_parser('typescript')
tree = parser.parse(b'')
ext = TypeScriptExtractor(tree.root_node, b'', 'empty.ts', config)
nodes, edges = ext.extract()
assert nodes == []
assert edges == []
```

## Next Steps


---

*Source: test_extractor_typescript.py:171 | Complexity: Intermediate | Last updated: 2026-05-05*