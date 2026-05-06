# How To: Code Never Contains Banned Plural Path

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Strip the module-level docstring, then ensure banned tokens are absent
from code / string literals. Tokens in the top-level docstring are
permitted because they document the rule — they never execute.

## Prerequisites

**Required Modules:**
- `__future__`
- `re`
- `sqlite3`
- `sys`
- `pathlib`
- `pytest`
- `superlocalmemory.hooks.adapter_base`
- `superlocalmemory.hooks.antigravity_adapter`
- `superlocalmemory.hooks`
- `ast`
- `superlocalmemory.hooks`
- `tests.test_adapters.conftest`


## Step-by-Step Guide

### Step 1: 'Strip the module-level docstring, then ensure banned tokens are absent\n    from code / string literals. Tokens in the top-level docstring are\n    permitted because they document the rule — they never execute.'

```python
'Strip the module-level docstring, then ensure banned tokens are absent\n    from code / string literals. Tokens in the top-level docstring are\n    permitted because they document the rule — they never execute.'
```

**Verification:**
```python
assert banned not in code_without_docstring, f'banned token {banned!r} appears in executable code'
```

### Step 2: Assign src = Path.read_text(...)

```python
src = Path(mod.__file__).read_text()
```

### Step 3: Assign tree = ast.parse(...)

```python
tree = ast.parse(src)
```

### Step 4: Assign code_without_docstring = ast.unparse(...)

```python
code_without_docstring = ast.unparse(tree)
```

### Step 5: Assign tree.body = value

```python
tree.body = tree.body[1:]
```

**Verification:**
```python
assert banned not in code_without_docstring, f'banned token {banned!r} appears in executable code'
```


## Complete Example

```python
# Workflow
'Strip the module-level docstring, then ensure banned tokens are absent\n    from code / string literals. Tokens in the top-level docstring are\n    permitted because they document the rule — they never execute.'
import ast
from superlocalmemory.hooks import antigravity_adapter as mod
src = Path(mod.__file__).read_text()
tree = ast.parse(src)
if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
    tree.body = tree.body[1:]
code_without_docstring = ast.unparse(tree)
for banned in ('.agents/knowledge', '.agents/skills', '.antigravity/knowledge'):
    assert banned not in code_without_docstring, f'banned token {banned!r} appears in executable code'
```

## Next Steps


---

*Source: test_antigravity_adapter.py:136 | Complexity: Intermediate | Last updated: 2026-05-05*